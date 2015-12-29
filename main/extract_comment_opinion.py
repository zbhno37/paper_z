#encoding=utf-8

import sys
import os
import re
import jieba
sys.path.append('../xiaoyang/dianping_nlp/pos/python/')
sys.path.append('../xiaoyang/dianping_nlp/dish_sentiment/')

from pos_tagger_stdin import PosTagger
from ner_tagger_reducer import NerTagger
import extract_dish_features_opinion_words as OpinionExtractor
import extract_dish_sentiment as SentimentExtractor

BASE_DIR = '/home/zhangbaihan/lizz/xiaoyang/dianping_nlp'
DISH_SENTIMENT_DIR = '../xiaoyang/dianping_nlp/dish_sentiment/'

replacer = re.compile(r':[^:]*$')

jieba.load_userdict('../data/2_char_dishes')

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

def main():
    posTagger = PosTagger()
    nerTagger = NerTagger()

    for text in sys.stdin:
        sentence = [x.encode('utf-8') for x in jieba.cut(text)]
        pos = get_pos_tag(posTagger, sentence)
        ner = get_ner_tag(nerTagger, sentence, pos)

        #out_ls = []
        #for i, word in enumerate(sentence):
            #out_ls.append('%s/%s/%s' % (word, pos[i], ner[i]))
        #print ' '.join(out_ls)

        VA_word_dict = {}
        VV_word_dict = {}
        exclude_word_dict = {}
        OpinionExtractor.get_dict_from_file(VA_word_dict, os.path.join(DISH_SENTIMENT_DIR, 'VA_word_dict'))
        OpinionExtractor.get_dict_from_file(VV_word_dict, os.path.join(DISH_SENTIMENT_DIR, 'VV_word_dict'))
        OpinionExtractor.get_set_from_file(exclude_word_dict, os.path.join(DISH_SENTIMENT_DIR, 'exclude_noun_words'))
        OpinionExtractor.test_get_dish_feature([sentence], [pos], [ner], VA_word_dict, VV_word_dict, exclude_word_dict)
        SentimentExtractor.test_get_dish_feature([sentence], [pos], [ner], VA_word_dict, VV_word_dict, exclude_word_dict)
if __name__ == '__main__':
    main()
