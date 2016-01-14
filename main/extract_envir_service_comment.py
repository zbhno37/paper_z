#coding=utf-8
import jieba
import jieba.posseg as pseg
import logging
logging.basicConfig(format='%(asctime)s\t%(message)s', level=logging.INFO)

class EnvirServExtractor:
    def __init__(self):
        self.keywords = self.load_comment_word('../gen_data/envir_service_dict')
        self.stop_word = self.load_set('../../paper/data/dianping/mark')

    def load_comment_word(self, filename):
        keywords = {}
        with open(filename) as fin:
            while True:
                line = fin.readline()
                if not line: break
                word = line.strip()
                keywords[word] = {}
                keywords[word]['pre'] = set(fin.readline().strip().split(' '))
                keywords[word]['post'] = set(fin.readline().strip().split(' '))
        return keywords

    def find_all(self, array, word):
        return [i for i, x in enumerate(array) if x == word]

    def find_all_pos(self, array, word):
        return [i for i, x in enumerate(array) if x[0] == word]

    def load_set(self, filename):
        stop_word = set()
        with open(filename) as fin:
            for line in fin:
                stop_word.add(line.strip())
        return stop_word

    def extract(self, sentence):
        # return list of words
        # [
        # [w1, w2, w3],
        # ]
        res = []
        sent = None
        for word in self.keywords:
            if word in sentence:
                if not sent:
                    sent = [x.encode('utf-8') for x in jieba.cut(sentence)]
                indexes = self.find_all(sent, word)
                for index in indexes:
                    candidate = []
                    for i in range(4):
                        j = index + i - 4
                        if j >= 0 and sent[j] not in self.stop_word and sent[j] in self.keywords[word]['pre']:
                            candidate.append(sent[j])
                    candidate.append(word)
                    for i in range(4):
                        j = index + i + 1
                        if j < len(sent) and sent[j] not in self.stop_word and sent[j] in self.keywords[word]['post']:
                            candidate.append(sent[j])
                    if len(candidate) > 1:
                        # exclude word itself
                        res.append(candidate)
        return res

    def extract_pos(self, sentence):
        # return list of words
        # [
        # [w1, w2, w3],
        # ]
        res = []
        sent = None
        for word in self.keywords:
            if word in sentence:
                if not sent:
                    sent = [(x.encode('utf-8'), flag) for x,flag in pseg.cut(sentence)]
                    #for i in range(len(sent)):
                        #print i, sent[i][0], sent[i][1]
                indexes = self.find_all_pos(sent, word)
                for index in indexes:
                    candidate = []
                    for i in range(4):
                        j = index + i - 4
                        if j >= 0 and sent[j][0] in self.keywords[word]['pre']:
                            candidate.append(sent[j][0])
                    candidate.append(word)
                    hasMark = False
                    for i in range(4):
                        j = index + i + 1
                        if j < len(sent):
                            # for this case
                            # 环境不错，味道不错
                            if sent[j][0] in ',，。.':
                                hasMark = True
                                continue
                            # new sentence
                            if hasMark and sent[j][1] == 'n': break
                            # case end

                            if sent[j][0] in self.keywords[word]['post']:
                                candidate.append(sent[j][0])
                    if len(candidate) > 1:
                        # exclude word itself
                        res.append(candidate)
        return res

def process(filename):
    fout = file('../../paper/data/dianping/envir_service.pos.res', 'w')
    count = 0
    extractor = EnvirServExtractor()
    import csv
    with open(filename) as fin:
        reader = csv.DictReader(fin)
        for line in reader:
            if count % 10000 == 0:
                logging.info(count)
            count += 1
            content = line['content']
            res = extractor.extract_pos(content)
            if res:
                fout.write('%s\n' % content)
                for each in res:
                    fout.write('%s;' % ','.join(each))
                fout.write('\n')

if __name__ == '__main__':
    process('../../paper/data/dianping/comment.mongo')
    #extractor = EnvirServExtractor()
    #while 1:
        #query = raw_input('query:\n')
        #for line in extractor.extract(query):
            #print ','.join(line)

