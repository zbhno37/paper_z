#coding=utf-8
import jieba
import csv
from collections import defaultdict
import logging
logging.basicConfig(format='%(asctime)s\t%(message)s', level=logging.INFO)

keywords = ['性价比']#['服务员', '服务态度', '价格', '价钱', '团购']#['装修', '出品', '等位', '点菜'] #'环境', '服务', '态度', '上菜',

def load_set(filename):
    stop_word = set()
    with open(filename) as fin:
        for line in fin:
            stop_word.add(line.strip())
    return stop_word

def find_all(array, word):
    return [i for i, x in enumerate(array) if x == word]

def filter_line(filename, stop_word):
    bow = {}
    for word in keywords:
        # 2 here, default 4
        bow[word] = [defaultdict(lambda: 0) for i in range(2)]
    count = 0
    with open(filename) as fin:
        reader = csv.DictReader(fin)
        for row in reader:
            sent = None
            for word in keywords:
                if word in row['content']:
                    if not sent:
                        sent = [x.encode('utf-8') for x in jieba.cut(row['content'])]
                    indexes = find_all(sent, word)
                    for index in indexes:
                        for i in range(4):
                            if index + i - 4 >= 0 and sent[index + i - 4] not in stop_word:
                                # 0 here, default i
                                bow[word][0][sent[index + i - 4]] += 1
                        for i in range(4):
                            if index + i + 1 < len(sent) and sent[index + i + 1] not in stop_word:
                                # 1 here, default i
                                bow[word][1][sent[index + i + 1]] += 1
            if count % 10000 == 0:
                logging.info(count)
            count += 1

    return bow

def main():
    stop_word = load_set('../../paper/data/dianping/mark')
    bow = filter_line('../../paper/data/dianping/comment.mongo', stop_word)
    fout = file('./bow_keyword_3.part4', 'w')
    for word in bow:
        fout.write('%s\n' % word)
        for i in range(len(bow[word])):
            sorted_words = sorted(bow[word][i].items(), key=lambda x: x[1], reverse=True)[:100]
            fout.write('%s:%d\n' % (word, i))
            for w in sorted_words:
                fout.write('\t%s,%d\n' % (w[0], w[1]))
    fout.close()

if __name__ == '__main__':
    main()
