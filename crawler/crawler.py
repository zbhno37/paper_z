# -*- coding: utf-8 -*-
import urllib2
import lxml.html as H
from collections import defaultdict
import socket
from time import sleep
from datetime import datetime
from Queue import Queue, Empty
import threading
import re
import sys
from mongoengine import connect
from data import Shop, User, Comment

HOST = 'http://www.dianping.com' #class, region, page
SHOP_URL = 'http://www.dianping.com/shop/'
SHOP_ID_XPATH = '//div[@id="shop-all-list"]//a[@data-hippo-type="shop"]/@href'
NEXT_XPATH = '//a[@class="next"]/@href'
PARAM = '/search/category/4/10/%s%sp%d'
SHOP_NAME_XPATH = '//h1[@class="shop-name"]/text()'
SHOP_STARS_XPATH = '//ul[@class="stars"]/li'
SHOP_INFO_XPATH = '//div[@class="brief-info"]/span[@class="item"]'
SHOP_ADDR = '//span[@itemprop="street-address"]'
SHOP_TEL = '//span[@itemprop="tel"]'
number_pattern = re.compile('\d+(\.\d*)?')
info_list = ['review_num', 'average', 'taste', 'envir', 'service']
# comment
shop_id_pattern = re.compile('\d+')
COMMENT_LIST_XPATH = '//div[@class="comment-list"]/ul/li'
COMMENT_ID_XPATH = './@data-id'
USER_ID_XPATH = './div[@class="pic"]/a[@class="J_card"]/@user-id'
USER_NAME_XPATH = './div[@class="pic"]/p[@class="name"]/a'
SCORE_XPATH = './div[@class="content"]/div[@class="user-info"]/span[contains(@class, "item-rank-rst")]/@class'
AVERAGE_PER_XPATH = './div[@class="content"]/div[@class="user-info"]/span[@class="comm-per"]'
DATE_XPATH = './div[@class="content"]/div[@class="misc-info"]/span[@class="time"]'
CONTENT_XPATH = './div[@class="content"]/div[@class="comment-txt"]/div[@class="J_brief-cont"]'
CONTENT_EXTRA_XPATH = './div[@class="content"]/div[@class="comment-txt"]/div[contains(@class, "J_extra-cont")]'
OTHER_SCORE_XPATH = './div[@class="content"]/div[@class="user-info"]/div[@class="comment-rst"]/span[@class="rst"]'
DATE_FORMAT = '%Y-%m-%d'
COMMENT_NEXT_XPATH = '//a[@class="NextPage"]/@href'
pageno_pattern = re.compile('\?pageno=\d+')
TASTE_TAG = u'口味'
ENVIR_TAG = u'环境'
SERVICE_TAG = u'服务'

def log(logstr, writer = sys.stdout):
    writer.write("%s\t%s\n" % (str(datetime.now()), logstr))
    writer.flush()

class Requester:
    UR_KEY = 'User-Agent'
    UR_VALUE = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.65'

    def __init__(self, timeout = 5):
        self.timeout = timeout

    def get(self, url):
        req = urllib2.Request(url)
        req.add_header(self.UR_KEY, self.UR_VALUE)
        content = urllib2.urlopen(req, timeout=self.timeout).read()
        return content

    def post(self, url, data):
        req = urllib2.Request(url, data)
        req.add_header(self.UR_KEY, self.UR_VALUE)
        content = urllib2.urlopen(req, timeout=self.timeout).read()
        return content

def load_list(filename):
    res = []
    with open(filename) as fin:
        for line in fin:
            line = line.strip()
            if line.startswith('#'): continue
            res.append(line)
    return res

def dump_queue(queue):
    with open('queue.dump', 'w') as fout:
        while not queue.empty():
            item, count = queue.get(False)
            fout.write(item + '\n')

def load_queue(filename):
    res = []
    with open(filename) as fin:
        for line in fin:
            res.append(line.strip())
    return res

def fill_date(ori_date, format):
    if ori_date.count('-') == 1:
        ori_date = '2015-' + ori_date
    elif ori_date.count('-') == 2:
        ori_date = '20' + ori_date
    return datetime.strptime(ori_date, format)

def load_log(filename):
    shop_ids = set()
    with open(filename) as fin:
        for line in fin:
            arr = line.strip().split(':')
            res = shop_id_pattern.search(arr[-1])
            if res:
                shop_ids.add(res.group())
    return shop_ids

def crawler_comment_thread(requester, queue, index):
    fout = file('./tmp/comment.part.%d' % index, 'w')
    ferr = file('./tmp/comment.err.part.%d' % index, 'w')
    failure_count = 1
    while not queue.empty():
        try:
            url, count = queue.get(True, 30)
            if count == 10:
                log('10:' + url + '\n', ferr)
                continue
            html = requester.get(url)
            log('%d:%d:%s' % (queue.qsize(), index, url), fout)
            page = H.document_fromstring(html)
            shop_id = shop_id_pattern.search(url).group()
            comment_list_node = page.xpath(COMMENT_LIST_XPATH)
            for comment_block in comment_list_node:
                comment = Comment()
                user = User()
                comment.comment_id = comment_block.xpath(COMMENT_ID_XPATH)[0]
                comment.shop_id = shop_id
                user.user_id = comment_block.xpath(USER_ID_XPATH)[0]
                comment.user_id = user.user_id
                username_node = comment_block.xpath(USER_NAME_XPATH)
                if len(username_node) < 1:
                    log('no username:%s' % url, ferr)
                    continue
                user.username = comment_block.xpath(USER_NAME_XPATH)[0].text_content()
                score_node = comment_block.xpath(SCORE_XPATH)
                comment.star = int(number_pattern.search(comment_block.xpath(SCORE_XPATH)[0].split(' ')[1]).group()) / 10 if len(score_node) > 0 else 0
                average_node = comment_block.xpath(AVERAGE_PER_XPATH)
                comment.average = number_pattern.search(average_node[0].text_content()).group() if len(average_node) > 0 else 0
                comment.date = fill_date(str(comment_block.xpath(DATE_XPATH)[0].text_content().encode('utf-8')).split('\xc2\xa0')[0], DATE_FORMAT)
                content_extra_node = comment_block.xpath(CONTENT_EXTRA_XPATH)
                if len(content_extra_node) > 0:
                    comment.content = content_extra_node[0].text_content().strip()
                else:
                    comment.content = comment_block.xpath(CONTENT_XPATH)[0].text_content().strip()
                other_score_node = comment_block.xpath(OTHER_SCORE_XPATH)
                comment.taste_score = 0
                comment.envir_score = 0
                comment.service_score = 0
                for each_node in other_score_node:
                    if TASTE_TAG in each_node.text_content():
                        comment.taste_score = each_node.text_content()[2]
                    elif ENVIR_TAG in each_node.text_content():
                        comment.envir_score = each_node.text_content()[2]
                    elif SERVICE_TAG in each_node.text_content():
                        comment.service_score = each_node.text_content()[2]
                #has_other_score = len(other_score_node) > 0
                #comment.taste_score = number_pattern.search(other_score_node[0].text_content()).group() if has_other_score else 0
                #comment.envir_score = number_pattern.search(other_score_node[1].text_content()).group() if has_other_score else 0
                #comment.service_score = number_pattern.search(other_score_node[2].text_content()).group() if has_other_score else 0
                user.save()
                comment.save()
            next_page_node = page.xpath(COMMENT_NEXT_XPATH)
            if len(next_page_node) > 0:
                pageno = next_page_node[0]
                comment_url_prefix = pageno_pattern.sub('', url)
                next_url = comment_url_prefix + pageno
                queue.put((next_url, 1))
            failure_count = 1
        except Empty,e:
            log('%d:Empty' % index, fout)
            break
        except urllib2.HTTPError,e:
            if e.code != 404:
                # 403 forbbidden
                queue.put((url, count))
                sleep(10 * failure_count)
                failure_count += 1
                if failure_count == 10:
                    log('%d:403:%s' % (index, url), fout)
            else:
                log('%d:404:error:%s' % (index, url), fout)
        except (urllib2.URLError, socket.timeout, socket.error):
            queue.put((url, count + 1))
            sleep(10 * failure_count)
            failure_count += 1
            if failure_count == 10:
                log('%d:timeout:%s' % (index, url), fout)
    #    except IndexError, e:
    #        queue.put((url, count + 1))
    #        log('###:%s\n' % url, ferr)
    #        log(str(e), ferr)
    fout.close()
    ferr.close()

def crawler_comment():
    #comment_url = HOST + '/shop/%s/review_all?pageno=1'
    requester = Requester()
#    shop_ids = load_list('shop_id.txt')
#    crawled_ids = load_log('crawled.shopid')
    shop_ids = load_queue('queue.dump')
    queue = Queue()
    for each in shop_ids:
        queue.put((each, 1))
#        if each not in crawled_ids:
#            queue.put((comment_url % each, 1))

    threads = []
    for i in range(1):
        threads.append(threading.Thread(target=crawler_comment_thread, args=(requester, queue, i)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    if not queue.empty():
        dump_queue(queue)

def crawler_shop_thread(requester, queue, index):
    fout = file('./shop_res/shop_id.part.%d' % index, 'w')
    ferr = file('./shop_res/shop_id.err.part.%d' % index, 'w')
    failure_count = 1
    while not queue.empty():
        try:
            shop_id, count = queue.get(True, 30)
            #shop_id = '14729436'
            if count == 4:
                ferr.write('4:' + shop_id + '\n')
                ferr.flush()
                continue
            url = SHOP_URL + shop_id
            log('%d:%d:%s' % (queue.qsize(), index, url))
            html = requester.get(url)
            page = H.document_fromstring(html)
            shop_title_node = page.xpath(SHOP_NAME_XPATH)
            if len(shop_title_node) < 1:
                # It's not food shop
                ferr.write('n:' + shop_id + '\n')
                ferr.flush()
                continue
            shop_title = shop_title_node[0].strip()
            info = defaultdict(lambda: 0)
            star = 0.0
            shop_stars_node = page.xpath(SHOP_STARS_XPATH)
            if len(shop_stars_node) == 5:
                # Has stars
                total_people = 0
                total_score = 0
                for i in range(0, 5):
                    info[5 - i] = int(shop_stars_node[i].text_content().strip())
                    total_score += info[5 - i] * (5 - i)
                    total_people += info[5 - i]
                star = total_score * 1.0 / total_people

                # shop information
                shop_info_node = page.xpath(SHOP_INFO_XPATH)
                if len(shop_info_node) == len(info_list):
                    for i in range(len(info_list)):
                        number = number_pattern.search(shop_info_node[i].text_content().strip())
                        info[info_list[i]] = number.group() if number else 0

            shop_addr_node = page.xpath(SHOP_ADDR)
            shop_addr = shop_addr_node[0].text_content().strip() if len(shop_addr_node) > 0 else ""
            shop_tel_node = page.xpath(SHOP_TEL)
            shop_tel = shop_tel_node[0].text_content().strip() if len(shop_tel_node) > 0 else ""
            shop = Shop(shop_id=shop_id, title=shop_title, star=star,\
                        star_1_num=info[1], star_2_num=info[2], star_3_num=info[3],\
                        star_4_num=info[4], star_5_num=info[5], review_num=info['review_num'],\
                        average=info['average'], taste_score=info['taste'], envir_score=info['envir'],\
                        service_score=info['service'], telephone=shop_tel, address=shop_addr)
            shop.save()
            failure_count = 1
        except Empty,e:
            log('%d:Empty' % index)
            break
        except urllib2.HTTPError,e:
            if e.code != 404:
                # 403 forbbidden
                queue.put((shop_id, count))
                sleep(10 * failure_count)
                failure_count += 1
                if failure_count == 10:
                    log('%d:403:%s' % (index, shop_id))
            else:
                log('404:error:%s' % shop_id)
        except (urllib2.URLError, socket.timeout):
            log('%d:timeout:%s' % (index, shop_id))
            queue.put((shop_id, count + 1))
            sleep(10)
    fout.close()
    ferr.close()

def crawler_shop():
    requester = Requester()
    shop_ids = load_list('shop_id.txt')
    shop_id_crawled = set(load_list('shop_id.export'))
    queue = Queue()
    for each in shop_ids:
        if each not in shop_id_crawled:
            queue.put((each, 1))
    shop_ids = []
    threads = []
    for i in range(3):
        threads.append(threading.Thread(target=crawler_shop_thread, args=(requester, queue, i)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    if not queue.empty():
        dump_queue(queue)


def crawler_shop_id_thread(requester, queue, index):
    fout = file('./shop_id_res/shop_id.part.%d' % index, 'w')
    ferr = file('./shop_id_res/shop_id.err.part.%d' % index, 'w')
    failure_count = 1
    while not queue.empty():
        try:
            param, count = queue.get(True, 30)
            if count == 4:
                ferr.write(param + '\n')
                ferr.flush()
                continue
            url = HOST + param
            print '%d,%d:%s' % (queue.qsize(), index, url)
            html = requester.get(url)
            page = H.document_fromstring(html)
            shop_ids = page.xpath(SHOP_ID_XPATH)
            for shop in shop_ids:
                fout.write(str(shop).replace('/shop/', '') + '\n')
            fout.flush()
            next_node = page.xpath(NEXT_XPATH)
            if len(next_node) > 0:
                next_param = str(next_node[0])
                queue.put((next_param, 1))
            # visit normally
            failure_count = 1
        except Empty,e:
            print '%d:Empty' % index
            break
        except urllib2.HTTPError,e:
            if e.code != 404:
                queue.put((param, count))
                sleep(10 * failure_count)
                failure_count += 1
                if failure_count == 10:
                    print '%d:403:%s' % (index, param)
            else:
                print '404 error:%s' % param
        except (urllib2.URLError, socket.timeout):
            queue.put((param, count + 1))
            sleep(10)

def crawler_shop_id():
    requester = Requester()
    region_list = load_list('region.txt')
    class_list = load_list('class.txt')
    queue = Queue()
    for region in region_list:
        for each_class in class_list:
            queue.put((PARAM % (each_class, region, 1), 1))
    threads = []
    for i in range(2):
        threads.append(threading.Thread(target=crawler_shop_id_thread, args=(requester, queue, i)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()

def main():
    mongo_db = 'dianping'
    connect(db=mongo_db)
    crawler_comment()

if __name__ == "__main__":
    main()

