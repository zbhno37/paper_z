import jieba

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
                    print 'cut words:%s' % ' '.join(sent)
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

if __name__ == '__main__':
    extractor = EnvirServExtractor()
    while 1:
        query = raw_input('query:\n')
        for line in extractor.extract(query):
            print ','.join(line)

