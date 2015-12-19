#encoding=utf-8

import sys
import re
import jieba
sys.path.append('../xiaoyang/dianping_nlp/pos/python/')

from pos_tagger_stdin import PosTagger
from ner_tagger_reducer import NerTagger

BASE_DIR = '/home/zhangbaihan/lizz/xiaoyang/dianping_nlp'

replacer = re.compile(r':[^:]*$')

def get_pos_tag(posTagger, sentence):
    """
    posTagger: PosTagger
    sentence: word list, str type
    """
    if not sentence: return []
    pos = posTagger.TagSentence(sentence)
    pos = [replacer.sub('', p) for p in pos]
    return pos

def get_ner_tag(nerTagger, sentence, pos_ls):
    """
    nerTagger: NerTagger
    sentence: word list, str type
    pos_ls: pos tagger
    """
    if not sentence or not pos_ls: return []
    ner = nerTagger.TagSentence(sentence, pos_ls)
    ner = [replacer.sub('', p) for p in ner]
    return ner

#class NER:
#    class_model = '%s/ner_data/lizz_model/maxent.classifier_0' % BASE_DIR
#    input_file = '%s/ner_data/lizz_model/input_file' % BASE_DIR
#    # output '-' is stdout
#    output_file = '-'
#    cmd = '%s/mallet-2.0.6/bin/mallet classify-file --classifier %s --input %s --output %s'
#
#    tag = ['O', 'B_food', 'I_food']
#
#    def __init__(self):
#        pass
#
#    def ner(self):
#        return subprocess.Popen(self.cmd % (BASE_DIR, self.class_model, self.input_file, self.output_file), shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
#
#    def parse(self, sentence):
#        """
#        sentence: word list, str type
#        """
#        tags = []
#        with open(self.input_file, 'w') as fout:
#            for word in sentence:
#                fout.write('%s\n' % word)
#
#        for line in self.ner().stdout:
#            print line
#            arr = line.split('\t')
#            ans = self.tag[0]
#            max_conf = float(arr[2])
#            for i in range(1, 3):
#                conf = float(arr[(i + 1) * 2])
#                if conf > max_conf:
#                    max_conf = conf
#                    ans = self.tag[i]
#            tags.append(ans)
#        return tags

def main():
    posTagger = PosTagger()
    nerTagger = NerTagger()

    #text = '我和老妈是常客了，连服务员都认识我们了。我最喜欢的海草沙拉，老妈最喜欢的吞拿鱼鱼籽饭。还有最近半年出的榴莲卷！还有我最喜欢的芝士炸虾卷也总算在万国这家有得吃了。感谢上天，哈哈。以后不用走那么远了~还有炙烧系列！都是大爱~最后推荐一下铁板元贝和椰香红豆冰吧~芝士局三文鱼嘛我见很多人推荐，但是我个人觉得太油了点~'
    text = '8分钟一炉，一炉12个，8寸39，不算贵，轻芝士，口感很松软细腻'

    sentence = [x.encode('utf-8') for x in jieba.cut(text)]
    pos = get_pos_tag(posTagger, sentence)
    ner = get_ner_tag(nerTagger, sentence, pos)

    out_ls = []
    for i, word in enumerate(sentence):
        out_ls.append('%s/%s/%s' % (word, pos[i], ner[i]))
    print ' '.join(out_ls)
    #print pos
    #print ner

if __name__ == '__main__':
    main()
