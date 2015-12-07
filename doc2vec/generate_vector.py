from gensim.models.doc2vec import LabeledSentence, Doc2Vec
from collections import defaultdict
import csv
import jieba
import sys
from datetime import datetime

def log(logstr, writer = sys.stdout):
    writer.write("%s\t%s\n" % (str(datetime.now()), logstr))
    writer.flush()

def log_inline(logstr, writer = sys.stdout):
    writer.write("%s\t%s\r" % (str(datetime.now()), logstr))
    writer.flush()

def load_file_set(filename):
    res = set()
    with open(filename) as fin:
        for line in fin:
            res.add(line.strip().decode('utf-8'))
    return res

def load_user_comment(filename):
    comment_labeled = []
    log('loading LabeledSentence...')
    count = 1
    with open(filename) as fin:
        for line in fin:
            line = line.strip().split('\t')
            arr = [x for x in line if x.strip() != ""]
            comment_labeled.append(LabeledSentence(words=arr[1:], tags=[arr[0].decode('utf-8')]))
            log(count)
            count += 1
    print ''
    return comment_labeled

def main():
    #user_comment = load_user_comment('../../paper/data/user_comment_without_stopword.txt')
    user_comment = load_user_comment('../../paper/data/shop_comment_dish.txt')
    log('training model...')
    model = Doc2Vec(user_comment, size=100)
    log('saving model...')
    model.save('../model/shop.d2v.dish.model')

if __name__ == '__main__':
    main()

def _load_user_comment(filename):
    #stop_words = load_file_set('../../paper/data/full_stopwords.txt')
    stop_words = set()
    fout = file('../../paper/data/shop_comment.txt', 'w')
    user_comment = defaultdict(list)
    log('reading comments...')
    count = 1
    with open(filename) as fin:
        reader = csv.DictReader(fin)
        for row in reader:
            user_comment[row['shop_id']].append(row['content'])
            sys.stdout.write('\r%d' % count)
            count += 1
    log('loading LabeledSentence...')
    comment_labeled = []
    count = 1
    for user_id, comments in user_comment.iteritems():
        words = []
        for sentence in comments:
            words.extend([x for x in jieba.cut(sentence) if x not in stop_words])
        #comment_labeled.append(LabeledSentence(words=words, tags=[('uid_' + user_id).decode('utf-8')]))
        sys.stdout.write('\r%d' % count)
        count += 1
        fout.write('%s\t%s\n' % (user_id, '\t'.join([x.encode('utf-8') for x in words])))
    fout.close()
    return comment_labeled


