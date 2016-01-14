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

class DishOpinionExtractor:
    def __init__(self):
        self.posTagger = PosTagger()
        self.nerTagger = NerTagger()
        self.VA_word_dict = {}
        self.VV_word_dict = {}
        self.exclude_word_dict = {}
        SentimentExtractor.get_dict_from_file(self.VA_word_dict, os.path.join(DISH_SENTIMENT_DIR, 'VA_word_dict'))
        SentimentExtractor.get_dict_from_file(self.VV_word_dict, os.path.join(DISH_SENTIMENT_DIR, 'VV_word_dict'))
        SentimentExtractor.get_set_from_file(self.exclude_word_dict, os.path.join(DISH_SENTIMENT_DIR, 'exclude_noun_words'))


    def extract(self, sentence):
        """
        return format
        [
            [w1, w2, w3],
            [w4, w5, w6],
        ]
        """
        sentence = [x.encode('utf-8') for x in jieba.cut(sentence)]
        pos = get_pos_tag(self.posTagger, sentence)
        ner = get_ner_tag(self.nerTagger, sentence, pos)
        word_ls, pos_ls, ner_ls = SentimentExtractor.merge_dish(sentence, pos, ner)
        word_sentence_ls, pos_sentence_ls, ner_sentence_ls = SentimentExtractor.split_review(word_ls, pos_ls, ner_ls)
        dish_VA_features_dict = {}
        dish_VV_features_dict = {}
        SentimentExtractor.get_dish_feature(word_sentence_ls, pos_sentence_ls, ner_sentence_ls, self.VA_word_dict, self.VV_word_dict, self.exclude_word_dict, dish_VA_features_dict, dish_VV_features_dict)
        res = []
        # VA feature
        for dish in dish_VA_features_dict:
            features_ls = dish_VA_features_dict[dish]
            for fields in features_ls:
                out_ls = []
                noun= fields[0]
                phrase = fields[1]
                VA_phrase_ls = fields[3]
                VA_word = VA_phrase_ls[-1]
                neg_word = fields[4]
                out_ls.append(dish)
                out_ls.append(noun)
                out_ls.append(VA_word)
                out_ls.append(neg_word)
                res.append(out_ls)
        # VV feature
        for dish in dish_VV_features_dict:
            features_ls = dish_VV_features_dict[dish]
            for fields in features_ls:
                out_ls = []
                noun= fields[0]
                phrase = fields[1]
                out_ls.append(dish)
                out_ls.append(noun)
                out_ls.append(phrase)
                res.append(out_ls)
        return res

def main():
    posTagger = PosTagger()
    nerTagger = NerTagger()

    #for text in sys.stdin:
    if True:
        text = '我很喜欢她家的星冰乐,味道真的不错，酸菜鱼一般。'
        #sentence = [x.encode('utf-8') for x in jieba.cut(text)]
        #pos = get_pos_tag(posTagger, sentence)
        #ner = get_ner_tag(nerTagger, sentence, pos)
        #print pos
        #print ner
        ##out_ls = []
        ##for i, word in enumerate(sentence):
            ##out_ls.append('%s/%s/%s' % (word, pos[i], ner[i]))
        ##print ' '.join(out_ls)

        #VA_word_dict = {}
        #VV_word_dict = {}
        #exclude_word_dict = {}
        #OpinionExtractor.get_dict_from_file(VA_word_dict, os.path.join(DISH_SENTIMENT_DIR, 'VA_word_dict'))
        #OpinionExtractor.get_dict_from_file(VV_word_dict, os.path.join(DISH_SENTIMENT_DIR, 'VV_word_dict'))
        #OpinionExtractor.get_set_from_file(exclude_word_dict, os.path.join(DISH_SENTIMENT_DIR, 'exclude_noun_words'))
        #OpinionExtractor.test_get_dish_feature([sentence], [pos], [ner], VA_word_dict, VV_word_dict, exclude_word_dict)
        #print '#######'
        #SentimentExtractor.test_get_dish_feature([sentence], [pos], [ner], VA_word_dict, VV_word_dict, exclude_word_dict)
        dish_extractor = DishOpinionExtractor()
        for res in dish_extractor.extract(text):
            print ','.join(res)

if __name__ == '__main__':
    main()
