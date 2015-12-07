import csv
from collections import defaultdict
import sys
from datetime import datetime

def log(logstr, writer = sys.stdout):
    writer.write("%s\t%s\n" % (str(datetime.now()), logstr))
    writer.flush()

def log_inline(logstr, writer = sys.stdout):
    writer.write("\r%s\t%s" % (str(datetime.now()), logstr))
    writer.flush()

def load_set(filename):
    s = set()
    with open(filename) as fin:
        for line in fin:
            s.add(line.strip())
    return s

def get_dict_word(content, word_dict):
    # find out all dishes in comment
    res = []
    for each in word_dict:
        if each in content and each.strip() != "":
            res.append(each)
    return res

def main():
    word_dict = load_set('../ner/dish.txt')
    user_comment = defaultdict(list)
    shop_comment = defaultdict(list)
    count = 1
    log("loading comment...")
    with open('../../paper/data/comment.mongo') as fin:
        reader = csv.DictReader(fin)
        for row in reader:
            if count % 10000 == 0:
                log(count)
            count += 1
            res = get_dict_word(row['content'], word_dict)
            user_comment[row['user_id']].extend(res)
            shop_comment[row['shop_id']].extend(res)
    print ''
    log("saving shop_comment...")
    count = 1
    with open('../../paper/data/shop_comment_dish.txt', 'w') as fout:
        for shop_id, comment in shop_comment.iteritems():
            log(count)
            count += 1
            if len(comment) == 0: continue
            fout.write('%s\t%s\n' % (shop_id, '\t'.join(comment)))
    print ''
    log("saving user_comment...")
    count = 1
    with open('../../paper/data/user_comment_dish.txt', 'w') as fout:
        for user_id, comment in user_comment.iteritems():
            log(count)
            count += 1
            if len(comment) == 0: continue
            fout.write('%s\t%s\n' % (user_id, '\t'.join(comment)))
    print ''
    log("finish")

if __name__ == '__main__':
    main()
