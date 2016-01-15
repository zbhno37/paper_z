import logging
logging.basicConfig(format='%(asctime)s\t%(message)s', level=logging.INFO)
import csv
from extract_comment_opinion import DishOpinionExtractor
from extract_enviro_service_comment import EnvirServExtractor
from multiprocessing import Process

def line_count(filename):
    count = 0
    with open(filename) as fin:
        for line in fin:
            count += 1
    return count

def filter_to_kw(filename, beg, end, id):
    logging.info('info:%s,%s,%s-%s' % (id, filename, beg, end))
    dish_extractor = DishOpinionExtractor()
    envir_service_extractor = EnvirServExtractor()
    fout = file('../../paper/data/dianping/comment.kw/comment.keyword.%s' % beg, 'w')
    fieldnames = ['_id', 'content', 'shop_id', 'user_id', 'star']
    writer = csv.DictWriter(fout, fieldnames=fieldnames)
    writer.writeheader()
    count = 0
    with open(filename) as fin:
        reader = csv.DictReader(fin)
        for line in reader:
            if count < beg:
                continue
            if count >= end:
                break
            count += 1
            if count % 500 == 0:
                logging.info('process:%d:%d' % (id, count))
            new_comment = ''
            opinion = dish_extractor.extract(line['content'])
            envir_service = envir_service_extractor.extract(line['content'])
            for each in opinion:
                new_comment += ' %s' % ' '.join(each)
            for each in envir_service:
                new_comment += ' %s' % ' '.join(each)
            row = {}
            for key in fieldnames:
                if key != 'content':
                    row[key] = line[key]
            row['content'] = new_comment if new_comment.strip() != '' else line['content']
            writer.writerow(row)

def main():
    filename = '../../paper/data/dianping/comment.mongo'
    thread_nums = 10
    lc = line_count(filename)
    print lc
    seg_info = [1]
    thread_lines = lc / thread_nums
    for i in range(thread_nums - 1):
        seg_info.append(seg_info[-1] + thread_lines)
    seg_info.append(lc + 1)
    print len(seg_info)
    processes = []
    for i in range(thread_nums):
        processes.append(Process(target=filter_to_kw, args=(filename, seg_info[i], seg_info[i + 1], i, )))
    for p in processes:
        p.start()
    for p in processes:
        p.join()

if __name__ == '__main__':
    main()
