#encoding=utf-8



import sys
from cal_phrase_score import cal_phrase_score





def merge_dish(word_ls, pos_label_ls, ner_label_ls):
    """
        将ner_label中B_food I_food合成一个词，pos_label做出相应的改变，把这个词标记成NN
    """
    ner_out_ls = []
    pos_out_ls = []
    word_out_ls = []
    if len(ner_label_ls) != len(pos_label_ls):
        sys.stderr.write('ner_label_ls length != pos_label_ls length')
        exit()

    size = len(ner_label_ls)
    i = 0
    dish_start_index = -1
    is_dish_word = False
    tmp_word_ls = []
    while i < size:
        if i > 0 and  ner_label_ls[i] == 'I_food' and ner_label_ls[i-1] == 'O':# 只有一个单独的I_food出现
            ner_label_ls[i] = 'B_food'
        
        if ner_label_ls[i] == 'B_food':
            if is_dish_word:
                word_out_ls.append(''.join(word_ls[dish_start_index:i]))
                pos_out_ls.append('NN')
                ner_out_ls.append('@food')
            dish_start_index = i
            is_dish_word = True
            i = i + 1
        elif ner_label_ls[i]  == 'I_food':
            i = i + 1
        else:
            if is_dish_word:
                word_out_ls.append(''.join(word_ls[dish_start_index:i]))
                pos_out_ls.append('NN')
                ner_out_ls.append('@food')
            is_dish_word = False
            word_out_ls.append(word_ls[i])
            ner_out_ls.append(ner_label_ls[i])
            pos_out_ls.append(pos_label_ls[i])
            i = i + 1
            
    if is_dish_word:#评论的最后是菜
        word_out_ls.append(''.join(word_ls[dish_start_index:i]))
        pos_out_ls.append('NN')
        ner_out_ls.append('@food')

    return (word_out_ls, pos_out_ls, ner_out_ls)


def get_noun_phrase_ls(word_ls, pos_ls ):
    '''
        找出名词性短语，只包含简单的情况：鱼的味道，鸭 血不错, 同位语
        [[口感，卖相]
        只考虑顿号、和
        问题：黄色的很好吃，巧克力味的很好吃
              口感和卖相都不错
        pattern: NN DEG NN
                 NN DEG Word1 NN
                 NN DEG  word1 Word2 NN
                 NN NN
        同位语：卖相和口感， 一份拉面、一份剁椒鱼头和苹果，【东北大拉皮】、【地三鲜】经典的东北菜
        现在只处理最简单的：
        return ls
    '''
    if len(word_ls) != len(pos_ls):
        print "word_ls length not equal pos_ls"
        exit()

    length = len(word_ls)
    start_end_pair_ls = []

    i=0
    while i < length:
        end=i
        de_pos = -1 
        if pos_ls[end] == 'JJ' and end+1 < length and pos_ls[end+1] == 'NN':
            end += 2
        while  end < length and pos_ls[end] == 'NN':
            end = end + 1
        
        if  end > i and end < length and word_ls[end] == '的':#的前面一定是名词
            de_pos = end 

            if de_pos +2< length and pos_ls[de_pos+1] == 'JJ' and pos_ls[de_pos+2] == 'NN':
                end += 3
                while  end < length and pos_ls[end] == 'NN':
                    end = end + 1
                start_end_pair_ls.appen((i, end))
                i = end
            elif de_pos + 1 < length and pos_ls[de_pos+1] == 'NN':
                end +=2
                while  end < length and pos_ls[end] == 'NN':
                    end = end + 1
                start_end_pair_ls.append((i, end))
                i = end
            else:
                start_end_pair_ls.append((i,de_pos))
                i = de_pos + 1


        else: 
            if end > i: #找到名词
                start_end_pair_ls.append((i, end))
                i = end 
            else:
                i +=1
            
    return start_end_pair_ls
            
            

def get_tongwei_noun_phrase_ls(word_ls, pos_ls):
    '''bad cases:
       蛋糕和其他的东西都很不错
       点了一份牛肉、香肠、辣椒，还有牛排，味道都不错

       粉蒸肉和排骨卖相和味道都不错
       粉蒸肉和排骨味道不错
       点 了 壶 茶 和 店员 推荐 的 红豆布丁沙冰

       和、跟、同

    '''
    tongwei_noun_phrase_ls = []
    start_end_pair_ls = get_noun_phrase_ls(word_ls, pos_ls)

    last_noun_index = 0
    tmp_pair_ls = []
    if not start_end_pair_ls:#如果包含的名词为空，返回空列表
        return tmp_pair_ls
    tmp_pair_ls.append(start_end_pair_ls[0])

    quoted_punctuation_ls = ["】", "【", "#"]

    while last_noun_index < len(start_end_pair_ls) -1:
        last_end = start_end_pair_ls[last_noun_index][1]
        if last_end in quoted_punctuation_ls:
            last_end = last_end + 1
        if word_ls[last_end] == '、' or  word_ls[last_end] == '和' or word_ls[last_end] == '与' or word_ls[last_end] == '还有' or word_ls[last_end] == '&' or word_ls[last_end] == '+':#并列连接词
            last_end = last_end + 1
            if pos_ls[last_end] == 'CD' and pos_ls[last_end+1] == 'M':
                last_end = last_end + 2
            if   start_end_pair_ls[last_noun_index +1][0] == last_end:#并列词后面是个名词
                tmp_pair_ls.append(start_end_pair_ls[last_noun_index+1])
                last_noun_index += 1
                continue
        tongwei_noun_phrase_ls.append(tmp_pair_ls)
        tmp_pair_ls = []
        tmp_pair_ls.append(start_end_pair_ls[last_noun_index + 1])
        last_noun_index += 1
            
        
        
    tongwei_noun_phrase_ls.append(tmp_pair_ls)
    return tongwei_noun_phrase_ls
    
    


def split_review(word_ls, pos_ls, ner_ls):
    signs = "，。！～？；…"
    last_pos = 0 
    last_dun_hao_pos =0
    word_out_ls = [] 
    pos_out_ls = [] 
    ner_out_ls = [] 
    for pos,word in enumerate(word_ls):
        if word in signs:
            if pos > last_pos:
                word_out_ls.append(word_ls[last_pos:pos+1])
                pos_out_ls.append(pos_ls[last_pos:pos+1])
                ner_out_ls.append(ner_ls[last_pos:pos+1])
            last_pos = pos +1
            last_dun_hao_pos = last_pos
        """
        if word == u'、':
            if pos - last_dun_hao_pos >= 6:
                yield "".join(sentence[last_pos:pos]).strip()
                last_pos = pos +1
            last_dun_hao_pos = pos + 1 
        """
    

    if last_pos < len(word_ls):
        word_out_ls.append(word_ls[last_pos:pos+1])
        pos_out_ls.append(pos_ls[last_pos:pos+1])
        ner_out_ls.append(ner_ls[last_pos:pos+1])
    return (word_out_ls, pos_out_ls, ner_out_ls)

def get_dish_pos(ner_label_ls):
    position_ls = []
    for i,label in ner_label_ls:
        if label == '@food':
            position_ls.append(i)
    return position_ls




def get_last_noun_phrase(tongwei_noun_phrase_ls, end_index, last_phrase_ls_index = -1, start_index = 0):
    """
        从last_phrase_ls_index 开始往前查找， 如果找到范围在 start_index 和 end_index 之间第一个名词的id， 如果返回一个字符串, 代表没有找到
    """
    
    start_idx = len(tongwei_noun_phrase_ls) * -1

    idx = last_phrase_ls_index

    while idx >= start_idx:
        phrase_ls_start = tongwei_noun_phrase_ls[idx][0][0]
        phrase_ls_end = tongwei_noun_phrase_ls[idx][-1][1]
        if phrase_ls_end <= end_index and phrase_ls_start >= start_index:
            return idx
        else:
            idx = idx -1
    if idx == start_idx -1:
        return ""
        
def get_next_noun_phrase(tongwei_noun_phrase_ls, start_index, end_index):
    """
         从左往右查找，范围在 start_index 和 end_index 之间第一个名词的id， 如果返回一个字符串, 代表没有找到
    """
    
    idx = 0 
    end_idx = len(tongwei_noun_phrase_ls)

    while idx < end_idx:
        phrase_ls_start = tongwei_noun_phrase_ls[idx][0][0]
        phrase_ls_end = tongwei_noun_phrase_ls[idx][-1][1]
        if phrase_ls_end <= end_index and phrase_ls_start >= start_index:
            return idx
        else:
            idx += 1
    if idx == end_idx:
        return ""

def is_int(num):
    try:
        int(num)
        return True
    except ValueError:
        return False
        

         


de_word_ls = ['的', '地', '得', '之']
def get_next_sentence_VA_features(word_ls, pos_ls, ner_ls, start_index, end_index, tongwei_noun_phrase_ls, VA_word_dict):
    """
        得到下一个句子， VA_feature, 和它最近的名词。如果前面没有名词，就用“”替代
        问题：牛角包，很喜欢丹麦系列，
        喜欢这些先跟后面结合，再跟前面结合
    """
    noun_VA_phrase_pair_ls = []
    if len(word_ls) != len(pos_ls):
        print "word_ls length not equal pos_ls"
        exit()

    length = len(word_ls)

    VA_phrase_ls = []
    VA_feature_ls = []
    i = end_index -1
    while i >= start_index:
        if word_ls[i] in VA_word_dict:
            #很不错 非常的不错
            start = i - 1
            if i-1 >= start_index and word_ls[i-1] in de_word_ls:
                start == i-2
            while start >= start_index and pos_ls[start] == 'AD':
                start = start -1
            VA_phrase_ls.append(word_ls[start+1:i+1])
            if i+2 < end_index and word_ls[i +1] == '的' and pos_ls[i+2] =='NN':#最好吃的玉米
                tongwei_idx = get_next_noun_phrase(tongwei_noun_phrase_ls, i+2, end_index)
            else:
                tongwei_idx = get_last_noun_phrase(tongwei_noun_phrase_ls, start +1,  -1, 0) 
            if not is_int(tongwei_idx): #没有找到名词
                VA_feature_ls.append(("", (start+1, i+1)))
            else:
                if tongwei_noun_phrase_ls[tongwei_idx][0][0] >= start_index:#名词的最左端要大于start_index
                    VA_feature_ls.append((tongwei_idx, (start+1, i+1)))
                else:
                    VA_feature_ls.append(("", (start+1, i+1)))

            
            #鱼的味道很不错，口感很不错， 鱼味道不错, 卖相和口感都不错, “宫爆鸡丁”不错，味道么不错， 一个人看看也不错

            i = start
        else:
            i = i-1
    return VA_feature_ls

negative_word_ls =['不', '不怎么', '不太', '不算', '不是', '说不上', '算不得', '算不上', '不算是', '不见得', '算不上', '谈不上', '唔', '吾', '没有', '不够', '没什么', '没啥', '没有', '木有', '么有', '没', '无', '不至于', '不会', '不如']
def cal_VA_phrase_score(word_ls, start_index, end_index, base_score, neg_word):
    """
        计算VA_phrase, 情感词的强弱。只考虑VA词，前面的3个副词
    """
    if end_index - start_index > 3:
        if neg_word == "": # 如果没有否定词， 查看start_index 到end-index -3 中是否有否定词
            for word in word_ls[start_index:end_index-3]:
                if word in negative_word_ls:
                    neg_word = word
                    break
        start_index = end_index -3

    out_score = base_score
    i = end_index - 1
    while i >= start_index:
        word = word_ls[i]
        out_score = cal_phrase_score(word, base_score)
        i -= 1
    if neg_word:#neg_word   不为空
        out_score = cal_phrase_score(neg_word, base_score)
    return out_score
        
            
def get_VA_feature_names(word_ls, pos_ls, ner_ls,  start_index, end_index, tongwei_noun_phrase_ls, VA_feature_ls, VA_word_dict):
    """
        从前面按顺序，找到VA_feature pair 加到list中
        得到下一个句子中的VA_word， 返回一个列表
        卖相和口感都很不错， 很不错， 环境很不错
        return ls [(卖相， 不错), (口感，不错), ("", 不错), (环境, 不错)]
    """
    #查看句子中有没有否定词，如果有否定词， 则找到离它最近的VA_phrase，进行否定
    VA_idx_word_dict = {} #key: VA_idx  neg_word
    j = len(VA_feature_ls) - 1
    
    i = start_index
    VA_start = -1
    VA_end = -1
    while i < end_index:
        word = word_ls[i]
        if word in negative_word_ls:
            #从前面找到VA_end 大于它的第一个VA_phrase
            while i >= VA_end and j > 0:
                j -= 1
                tongwei_idx, VA_phrase_idx_pair = VA_feature_ls[j]
                VA_start, VA_end = VA_phrase_idx_pair
            if i < VA_start:
                VA_idx_word_dict[j] = word_ls[i]
                i += 1
            elif i < VA_end:
                i = VA_end
            else:#句子中可能没有VA_phrase, 跳出结束
                break
        else:
            i += 1
                
    noun_VA_phrase_ls = []
    i = len(VA_feature_ls) - 1
    while i >= 0:
        tongwei_idx, VA_phrase_idx_pair = VA_feature_ls[i]
        VA_start, VA_end = VA_phrase_idx_pair
        VA_word = word_ls[VA_end-1]
        base_score = float(VA_word_dict[VA_word])
        neg_word = ""
        if i in VA_idx_word_dict:
            neg_word = VA_idx_word_dict[i]
            VA_phrase =VA_idx_word_dict[i] +"".join(word_ls[VA_start:VA_end])
        else:
            VA_phrase = "".join(word_ls[VA_start:VA_end])
        VA_score = cal_VA_phrase_score(word_ls, VA_start, VA_end-1, base_score, neg_word)
        
        for j in range(VA_start, VA_end):
            if word_ls[j] in negative_word_ls:
                neg_word = word_ls[j]
                VA_start = j+1
                break

        VA_phrase_ls = word_ls[VA_start:VA_end]
        if len(VA_phrase_ls) == 0:
            print " ".join(word_ls)
            print  ' ' + VA_phrase
        if is_int(tongwei_idx):
            for start, end in  tongwei_noun_phrase_ls[tongwei_idx]:
                #处理鱼的味道很不错， 鱼味道不错
                j = end - 1
                while j >= start:
                    if ner_ls[j] == '@food':
                        break
                    j -= 1
                if j+1 < end and word_ls[j+1] == '的':
                    j +=1
                start = j + 1
                noun_phrase = "".join(word_ls[start:end])
                noun_VA_phrase_ls.append((noun_phrase, VA_phrase, VA_score, VA_phrase_ls, neg_word))
        else:
            noun_VA_phrase_ls.append(("", VA_phrase, VA_score, VA_phrase_ls, neg_word))
            
        i -= 1
    out_ls = []
    if len(out_ls) > 0:
        pass
#         print ' '.join(word_ls)
#        print '\t'.join(out_ls)
#        print ""
    return  noun_VA_phrase_ls 

def print_noun_VA_phrase_ls( noun_VA_phrase_ls):
    out_ls = []
    for fields in noun_VA_phrase_ls:
        noun_phrase =  fields[0]
        VA_phrase = fields[1]
        out_ls.append(noun_phrase+'::'+VA_phrase)
    if len(out_ls) > 0:
        print ' '.join(out_ls)

def combine_dish_noun_VA_phrase_ls(dish_ls, noun_VA_phrase_ls, exclude_dict, find_exclude_words):
    dishes_features_ls = []
    filtered_ls = []
    find_exclude_words = False

    for fields in noun_VA_phrase_ls:
        noun_phrase = fields[0]
        VA_phrase = fields[1]
        in_exclude_dict = False
        if len(noun_phrase) > 0:
            #如果名词短语中有"环境、装修"这些词，排除在外
            for phrase in exclude_dict:
               if noun_phrase.endswith(phrase): 
                   in_exclude_dict = True
                   find_exclude_words = True
                   break
        #如果名词短语中含有排除的词，break掉
        if in_exclude_dict:
            break
        filtered_ls.append(fields)
    for dish_name in dish_ls:
        new_ls = filtered_ls[:]
        dishes_features_ls.append((dish_name, new_ls)) 
    return dishes_features_ls

def get_tongwei_dish_index(tongwei_noun_phrase_ls, ner_label_ls):
    '''
        同位语中[[跺脚牛肉，羊肉], [苹果]] 名词中含有dish的index
    '''
    index_ls = []
    for index,phrase_ls in enumerate(tongwei_noun_phrase_ls):
        is_append = False
        for start_end_pair in phrase_ls:
            start, end = start_end_pair
            for i in range(start, end):
                if ner_label_ls[i] == '@food':
                    index_ls.append(index)
                    is_append = True
                    break
            if is_append:
                break

        
    return index_ls
        
def get_dish_name_ls(word_ls, pos_ls, ner_ls, tongwei_noun_phrase_ls, tongwei_dish_index_ls):       
    dish_out_ls = []
    #得到句子中菜名的集合。例如：返回[[红烧肉，回锅肉], [摩卡，红酒]]
    for tongwei_noun_phrase_ls_idx in tongwei_dish_index_ls:
        tongwei_dish_phrase_ls = tongwei_noun_phrase_ls[tongwei_noun_phrase_ls_idx]
        dish_ls = []
        for start, end in tongwei_dish_phrase_ls:
            while start < end:
                if (ner_ls[start] == '@food'):
                    if  start +2 < end and word_ls[start + 1 ] == '的' and ner_ls[start + 2] == '@food':
                        dish_ls.append(''.join(word_ls[start:start+3]))
                    else:
                        dish_ls.append(''.join(word_ls[start:start+1]))
                    break
                else:
                    start +=1
        dish_out_ls.append(dish_ls)
    return dish_out_ls

def get_dish_name_set(word_ls, pos_ls, ner_ls, replace = True):
    """
        返回句子中的菜，如果一个菜是另一个菜的后缀，则将word_ls中相应的菜做替换。替换时只把后面的替换成前面的。前面的不会替换成后面的。
        [白菜乌东面，鱼肉，面]
    """
    dish_ls = []
    new_word_ls = []
    for i, word in enumerate(word_ls):
        if ner_ls[i] =='@food':
            in_dish_ls = False
            for dish in dish_ls:
                if dish.endswith(word):
                    in_dish_ls = True
                    new_word_ls.append(dish)
                    break
            if not in_dish_ls:
                dish_ls.append(word)
                new_word_ls.append(word)
        else:
            new_word_ls.append(word)
    if replace:
        word_ls = new_word_ls
    return dish_ls, word_ls

def print_dish_name_ls(dish_out_ls):
    for dish_ls in dish_out_ls:
        print '('+' '.join(dish_ls)+')'
        
    


def print_dishes_features_ls( dishes_features_ls):
    for dish, noun_VA_phrase_pair_ls in dishes_features_ls:
        out_ls=[]
        out_ls.append(dish)
        for noun_phrase, VA_phrase in noun_VA_phrase_pair_ls:
            out_ls.append(noun_phrase + VA_phrase)
        if len(out_ls) > 0:
            print ' '.join(out_ls)
            

    
def merge_dish_features_dict(dish_features_dict, dishes_features_ls):
    """
        将一个标准的dish_features, merge到dict中
    """
    for dish, features_ls in dishes_features_ls:
        if dish in dish_features_dict:
            dish_features_dict[dish].extend(features_ls)
        else:
            dish_features_dict[dish] = features_ls


def cal_VV_phrase_score(word_ls, start_index, end_index, base_score):
    return cal_VA_phrase_score(word_ls, start_index, end_index, base_score, "")

def find_before_VV_features(word_ls, pos_ls, ner_ls, tongwei_noun_phrase_ls,  start_index, end_index, VV_word_dict):
    """
        找到之前的VV_feature, 如果这些词出现在@food前，则这个food是表示喜欢的
        问题： 可能包含否定词

    """
    VV_feature_ls = []
    i =  end_index -1
    while i >= start_index:
        word = word_ls[i]
        if word == '推荐':
            if i + 1 < end_index and word_ls[i+1] == '的':
                i -= 1
                continue
        if word in VV_word_dict:
            index = i -1
            while index >=start_index and  pos_ls[index] == 'AD':
                index -= 1
            VV_phrase_start = index + 1
            VV_phrase_end = i+1
            base_score = float(VV_word_dict[word_ls[VV_phrase_end -1]])
            score = cal_VV_phrase_score(word_ls, VV_phrase_start, VV_phrase_end -1, base_score)
            VV_phrase = "".join(word_ls[VV_phrase_start:VV_phrase_end])
            VV_feature_ls.append(("", VV_phrase, score))
            i = index
        else:
            i -= 1

    return VV_feature_ls


def find_multi_dishes_features(word_ls, pos_ls, ner_ls, tongwei_noun_phrase_ls, tongwei_dish_index_ls, VA_word_dict, VV_word_dict, exclude_dict, find_exclude_words, dish_VA_features_dict, dish_VV_features_dict):
    dish_name_ls = get_dish_name_ls(word_ls, pos_ls, ner_ls, tongwei_noun_phrase_ls, tongwei_dish_index_ls)
    cur_dish_index = 0
    
    cur_dish_start_index = tongwei_noun_phrase_ls[tongwei_dish_index_ls[cur_dish_index ]][0][0]
    cur_dish_end_index = tongwei_noun_phrase_ls[tongwei_dish_index_ls[cur_dish_index ]][-1][1]
    cur_dish_ls= dish_name_ls[cur_dish_index]

    cur_dish_VV_features_ls = find_before_VV_features(word_ls, pos_ls, ner_ls, tongwei_noun_phrase_ls, 0, cur_dish_start_index, VV_word_dict)
    dishes_VV_features_ls = combine_dish_noun_VA_phrase_ls(cur_dish_ls, cur_dish_VV_features_ls, exclude_dict, find_exclude_words)
    merge_dish_features_dict(dish_VV_features_dict, dishes_VV_features_ls)

    dishes_VA_features_ls = []
    while cur_dish_index < len(tongwei_dish_index_ls) -1:
        next_dish_start_index = tongwei_noun_phrase_ls[tongwei_dish_index_ls[cur_dish_index + 1]][0][0]
        next_dish_end_index = tongwei_noun_phrase_ls[tongwei_dish_index_ls[cur_dish_index + 1]][-1][1]
        next_dish_ls= dish_name_ls[cur_dish_index + 1]
        #问题可能是否定形式
        VV_feature_ls = []
        cur_search_end_index = next_dish_start_index
        i =  cur_search_end_index -1
        start_index = cur_dish_end_index + 1
        while i >= cur_dish_end_index + 1:
            word = word_ls[i]
            if word == '推荐':
                if i + 1 < next_dish_start_index and word_ls[i+1] == '的':
                    break
            if word in VV_word_dict:
                index = i -1
                while index >=start_index and  pos_ls[index] == 'AD':
                    index -= 1
                VV_phrase_start = index + 1
                VV_phrase_end = i+1
                base_score = float(VV_word_dict[word_ls[VV_phrase_end -1]])
                score = cal_VV_phrase_score(word_ls, VV_phrase_start, VV_phrase_end -1, base_score)
                VV_phrase = "".join(word_ls[VV_phrase_start:VV_phrase_end])
                VV_feature_ls.append(("", VV_phrase, score))
                i = index + 1
                break
            else:
                i -= 1

        dishes_VV_features_ls = combine_dish_noun_VA_phrase_ls(next_dish_ls, VV_feature_ls, exclude_dict, find_exclude_words)
        merge_dish_features_dict(dish_VV_features_dict, dishes_VV_features_ls)

#start_index = cur_dish_end_index + 1
        start_index = cur_dish_start_index 
        if i == cur_dish_end_index:
            end_index = next_dish_start_index
        else:
            end_index = i 
        noun_VA_phrase_pair_ls = get_next_sentence_VA_features(word_ls, pos_ls, ner_ls, start_index, end_index, tongwei_noun_phrase_ls, VA_word_dict)
        noun_VA_phrase_ls =  get_VA_feature_names(word_ls, pos_ls, ner_ls,  start_index, end_index, tongwei_noun_phrase_ls, noun_VA_phrase_pair_ls, VA_word_dict)
        VA_dishes_features_ls = combine_dish_noun_VA_phrase_ls(cur_dish_ls, noun_VA_phrase_ls, exclude_dict, find_exclude_words)
        merge_dish_features_dict(dish_VA_features_dict, VA_dishes_features_ls)
        cur_dish_index += 1
        cur_dish_ls = next_dish_ls
    
    start_index = next_dish_start_index
    end_index = len(word_ls)
    noun_VA_phrase_pair_ls = get_next_sentence_VA_features(word_ls, pos_ls, ner_ls, start_index, end_index, tongwei_noun_phrase_ls, VA_word_dict)
    noun_VA_phrase_ls =  get_VA_feature_names(word_ls, pos_ls, ner_ls, start_index, end_index,  tongwei_noun_phrase_ls, noun_VA_phrase_pair_ls, VA_word_dict)
    VA_dishes_features_ls = combine_dish_noun_VA_phrase_ls(cur_dish_ls, noun_VA_phrase_ls, exclude_dict, find_exclude_words)
    merge_dish_features_dict(dish_VA_features_dict, VA_dishes_features_ls)


def print_dish_features_dict(dish_features_dict):

    for dish in dish_features_dict:
        out_ls = []
        features_ls = dish_features_dict[dish]
        for fields in features_ls:
            noun= fields[0]
            phrase = fields[1]
            score = str(fields[2])
            out_ls.append( noun+phrase+'::'+score)
        print dish + ' ' + ' '.join(out_ls)
        

def print_features_ls(features_ls):

    out_ls = []
    for fields in features_ls:
        noun= fields[0]
        phrase = fields[1]
        score = str(fields[2])
        out_ls.append( noun+phrase+'::'+score)
#out_ls.append( noun+phrase)
    print  ' '.join(out_ls)

#规则： 1.如果句子中只有一个菜名，把句子中相关的特征词，赋予这个菜。
#           1.1 判断相邻的下一个句子。如果下一个句子中还有菜， 判断它们之间的关系。如果有关联，还是前面的菜，否则是新的菜。
#           1.2. 继续判断下一个句子。
#   强制排除词：环境、服务
#   肯定词：鱼皮、丸子很好吃。 牛肉丸， 鱼肉。 
#
#       2. 
def get_cur_sentence_dish_features(word_sentence, pos_sentence, ner_sentence, VA_word_dict, VV_word_dict, exclude_dict, find_exclude_words, dish_VA_features_dict, dish_VV_features_dict):
    '''
        如果句子中同位语菜的数量： 为1的话，找到名词
        先后匹配，然后前匹配。
        粉蒸肉中的肉、粉蒸肉里面有、粉蒸肉里面的、粉蒸肉外面的
    '''
    tongwei_noun_phrase_ls = get_tongwei_noun_phrase_ls(word_sentence, pos_sentence)
    dishes_features_ls = []

    tongwei_dish_index_ls = get_tongwei_dish_index(tongwei_noun_phrase_ls, ner_sentence)
    dish_name_ls = get_dish_name_ls(word_sentence, pos_sentence, ner_sentence, tongwei_noun_phrase_ls, tongwei_dish_index_ls)
    if len(tongwei_dish_index_ls) == 1:#只有一个菜的情况下
        find_exclude_words = False
        start_index = 0
        end_index = tongwei_noun_phrase_ls[tongwei_dish_index_ls[0]][0][0] 
        VV_features_ls = find_before_VV_features(word_sentence, pos_sentence, ner_sentence, tongwei_noun_phrase_ls, start_index, end_index, VV_word_dict)
        dishes_VV_features_ls = combine_dish_noun_VA_phrase_ls(dish_name_ls[0], VV_features_ls, exclude_dict, find_exclude_words)

        merge_dish_features_dict(dish_VV_features_dict, dishes_VV_features_ls)
        
        #find VA_features
#start_index = tongwei_noun_phrase_ls[tongwei_dish_index_ls[0]][-1][1] 
        start_index = tongwei_noun_phrase_ls[tongwei_dish_index_ls[0]][0][0] 
        end_index = len(word_sentence)
        noun_VA_phrase_pair_ls = get_next_sentence_VA_features(word_sentence, pos_sentence, ner_sentence, start_index, end_index, tongwei_noun_phrase_ls, VA_word_dict)
        noun_VA_phrase_ls =  get_VA_feature_names(word_sentence, pos_sentence, ner_sentence, start_index, end_index, tongwei_noun_phrase_ls, noun_VA_phrase_pair_ls, VA_word_dict)
        dishes_features_ls = combine_dish_noun_VA_phrase_ls(dish_name_ls[0], noun_VA_phrase_ls, exclude_dict, find_exclude_words)
        merge_dish_features_dict(dish_VA_features_dict, dishes_features_ls)
        
        """
        out_ls = []
        for tple in VV_features_ls:
            VV_phrase = tple[1]
            out_ls.append(VV_phrase)
        if len(out_ls) > 0:
            print " ".join(word_sentence)
            print " ".join(dish_name_ls[0]) + ' '+ ' '.join(out_ls)
        """
        
       
    elif len(tongwei_dish_index_ls) > 1:#有多个菜的情况下 
#        dish_VA_features_dict = {}
#        dish_VV_features_dict = {}
        find_multi_dishes_features(word_sentence, pos_sentence, ner_sentence, tongwei_noun_phrase_ls, tongwei_dish_index_ls,  VA_word_dict, VV_word_dict, exclude_dict, find_exclude_words, dish_VA_features_dict, dish_VV_features_dict)
#        print " ".join(word_sentence)
#       print_dish_features_dict(dish_VA_features_dict)
#        print_dish_features_dict(dish_VV_features_dict)
        pass


        
    else:
        pass
    


#总称菜
low_level_dish_ls = ['凉菜', '热菜', '川菜', '生菜', '熟菜', '招牌菜', '冷菜', '点心', '甜品']
def find_main_dish_ls(word_ls, pos_ls, ner_ls, dish_num):
    """如果一个句子中含有多个菜，尝试找到菜中的主菜
        石磨小豆腐：豆腐很入味
        粉蒸肉中的虾仁很不错，
        外形像回锅肉
        豆腐脑甜品, 那个甜品倒是挺不错的。
        点了牛肉丸、和粉条。丸子倒是不错。
    """
    main_dish_ls = []
    if len(word_ls) == 0:
        return main_dish_ls

    #预处理， 如果菜名前是 "像", 做预处理
    #去除冷菜、热菜、菜、这些通称词
    new_ner_ls = []
    for i,word in enumerate(word_ls):
        if word in low_level_dish_ls and ner_ls[i] == '@food':
            new_ner_ls.append('NN')
            dish_num -= 1
        else:
            new_ner_ls.append(ner_ls[i])
            if ner_ls[i] == '@food':
                main_dish_ls.append(word)
            
    if dish_num == 1:#此时只剩下一个菜
        return main_dish_ls

    main_dish_ls = []
    if ner_ls[0] == '@food':#开头是一个菜名
        main_dish_ls.append(word_ls[0])
    elif ner_ls[-2] == '@food':#除去标点符号，最后一个是菜名
        if word_ls[-3] == '像' or word_ls[-4] == '像':#菜名前有像要排除
            pass
        else:
            main_dish_ls.append(word_ls[-2])
    else:#可以优化的地方，最后是一个VA_phrase,  豆腐很好吃
        #取最后一个菜名：的作为main_dish
        i = len(word_ls) -2 
        while i >=0:
            if ner_ls[i] == '@food' and word_ls[i+1] == '：':
                main_dish_ls.append(word_ls[i])
            i -= 1

    return main_dish_ls
        
            
        
        
        


def print_VA_VV_NN_word(word_ls, pos_ls, ner_ls):
    for i,word in enumerate(word_ls):
        if pos_ls[i] == 'NN' and ner_ls[i] !='@food':
#            print word+'\t'+'NN'
            pass
        elif pos_ls[i] == 'VV':
#            print word+'\t'+'VV'
            pass
        elif pos_ls[i] == 'VA':
            print word +'\t'+'VA'
        else:
            pass


punctuation_ls=['。', '！' , '？' , '；']
def get_dish_feature(word_sentence_ls, pos_sentence_ls, ner_sentence_ls, VA_word_dict, VV_word_dict, exclude_dict, dish_VA_features_dict,  dish_VV_features_dict):
    sentence_index = 0
    sentence_num = len(ner_sentence_ls)
    while sentence_index < sentence_num:
        cur_ner_sentence = ner_sentence_ls[sentence_index]
        cur_word_sentence = word_sentence_ls[sentence_index]
        cur_pos_sentence = pos_sentence_ls[sentence_index]
        
        #check how many dish in this sentence
        cur_tongwei_noun_phrase_ls = get_tongwei_noun_phrase_ls(cur_word_sentence, cur_pos_sentence)
        cur_tongwei_dish_index_ls = get_tongwei_dish_index(cur_tongwei_noun_phrase_ls, cur_ner_sentence)

        has_next_sentence = False
        if sentence_index < sentence_num -1:
            has_next_sentence = True
        
            next_ner_sentence = ner_sentence_ls[sentence_index+1]
            next_word_sentence = word_sentence_ls[sentence_index+1]
            next_pos_sentence = pos_sentence_ls[sentence_index+1]

            next_tongwei_noun_phrase_ls = get_tongwei_noun_phrase_ls(next_word_sentence, next_pos_sentence)
            next_tongwei_dish_index_ls = get_tongwei_dish_index(next_tongwei_noun_phrase_ls, next_ner_sentence)
        has_2_next_sentence= False
        if sentence_index < sentence_num - 2:
            has_2_next_sentence = True
            next_2_ner_sentence = ner_sentence_ls[sentence_index+2]
            next_2_word_sentence = word_sentence_ls[sentence_index+2]
            next_2_pos_sentence = pos_sentence_ls[sentence_index+2]

            next_2_tongwei_noun_phrase_ls = get_tongwei_noun_phrase_ls(next_2_word_sentence, next_2_pos_sentence)
            next_2_tongwei_dish_index_ls = get_tongwei_dish_index(next_2_tongwei_noun_phrase_ls, next_2_ner_sentence)

        dish_name_set, new_word_sentence = get_dish_name_set(cur_word_sentence, cur_pos_sentence, cur_ner_sentence, True) 
        cur_word_sentence = new_word_sentence
        if len(cur_tongwei_dish_index_ls) == 1 or len(dish_name_set) == 1:#如果句子中只有一个菜, 合并菜(如果菜名一样)
            cur_sentence_find_exclude_words = False
            dish_name_ls = get_dish_name_ls(cur_word_sentence, cur_pos_sentence, cur_ner_sentence, cur_tongwei_noun_phrase_ls, cur_tongwei_dish_index_ls)
            
            get_cur_sentence_dish_features(cur_word_sentence, cur_pos_sentence, cur_ner_sentence, VA_word_dict, VV_word_dict, exclude_dict, cur_sentence_find_exclude_words, dish_VA_features_dict, dish_VV_features_dict)
            noun_VA_phrase_ls = []
            has_next_sentence_dishes_features_ls  = False
            has_next_2_sentence_dishes_features_ls  = False
            print_VA_VV_NN_word(cur_word_sentence, cur_pos_sentence, cur_ner_sentence)
            if has_next_sentence and len(next_tongwei_dish_index_ls) == 0 and cur_word_sentence[-1] not in punctuation_ls and not cur_sentence_find_exclude_words :#下一句中菜的名字的个数为0, 并且标点符号不为句号， 而且上一句话中没有发现要排除的词
                next_sentence_find_exclude_words = False

                start_index = 0
                end_index = len(next_word_sentence)
                noun_VA_phrase_pair_ls = get_next_sentence_VA_features(next_word_sentence, next_pos_sentence, next_ner_sentence, start_index, end_index, next_tongwei_noun_phrase_ls, VA_word_dict)
                noun_VA_phrase_ls =  get_VA_feature_names(next_word_sentence, next_pos_sentence, next_ner_sentence,  start_index, end_index, next_tongwei_noun_phrase_ls, noun_VA_phrase_pair_ls, VA_word_dict)
                next_sentence_dishes_features_ls = combine_dish_noun_VA_phrase_ls(dish_name_ls[0], noun_VA_phrase_ls, exclude_dict, next_sentence_find_exclude_words)
                merge_dish_features_dict(dish_VA_features_dict, next_sentence_dishes_features_ls)
                if noun_VA_phrase_ls:
                    has_next_sentence_dishes_features_ls = True
                #不需要分析这个句子了
                sentence_index += 1
                print_VA_VV_NN_word(next_word_sentence, next_pos_sentence, next_ner_sentence)
                
                if has_2_next_sentence  and len(next_2_tongwei_dish_index_ls) == 0  and next_word_sentence[-1] not in punctuation_ls and not  next_sentence_find_exclude_words:#第二句话中包含的对菜名的评价
                    next_2_sentence_find_exclude_words = False

                    start_index = 0
                    end_index = len(next_2_word_sentence)
                    noun_VA_phrase_pair_ls = get_next_sentence_VA_features(next_2_word_sentence, next_2_pos_sentence, next_2_ner_sentence, start_index, end_index,  next_2_tongwei_noun_phrase_ls, VA_word_dict)
                    noun_VA_phrase_ls =  get_VA_feature_names(next_2_word_sentence, next_2_pos_sentence , next_2_ner_sentence, start_index, end_index, next_2_tongwei_noun_phrase_ls, noun_VA_phrase_pair_ls, VA_word_dict)
                    next_2_sentence_dishes_features_ls = combine_dish_noun_VA_phrase_ls(dish_name_ls[0], noun_VA_phrase_ls, exclude_dict, next_2_sentence_find_exclude_words)
                    merge_dish_features_dict(dish_VA_features_dict, next_2_sentence_dishes_features_ls)
                    if noun_VA_phrase_ls:
                        has_next_2_sentence_dishes_features_ls = True
                    #不需要分析这个句子了
                    sentence_index += 1
                    print_VA_VV_NN_word(next_2_word_sentence, next_2_pos_sentence, next_2_ner_sentence)
            else:#下一个菜可能是包含关系, 例如：里面的豆腐很好吃, 中的
                pass
                
            """    
            #打印同位语 noun_VA_phrase_ls
            if  dishes_features_ls and has_2_next_sentence and  has_next_2_sentence_dishes_features_ls:
                print " ".join(cur_word_sentence) + " " + " ".join(next_word_sentence) + " " +" ".join(next_2_word_sentence)
                print_dishes_features_ls(dishes_features_ls)
                print_dishes_features_ls(next_sentence_dishes_features_ls)
                print_dishes_features_ls(next_2_sentence_dishes_features_ls)
                print ""
            elif  dishes_features_ls and has_next_sentence and  has_next_sentence_dishes_features_ls:
                print " ".join(cur_word_sentence) + " " + " ".join(next_word_sentence)
                print_dishes_features_ls(dishes_features_ls)
                print_dishes_features_ls(next_sentence_dishes_features_ls)
                print ""
            elif  dishes_features_ls:
                print " ".join(cur_word_sentence)
                print_dishes_features_ls(dishes_features_ls)
                print ""
            else:
                pass
            """
        elif len(cur_tongwei_dish_index_ls) >= 2 :#句子中菜的个数大部分等于两个
            pass
            cur_sentence_find_exclude_words = False
            get_cur_sentence_dish_features(cur_word_sentence, cur_pos_sentence, cur_ner_sentence, VA_word_dict, VV_word_dict, exclude_dict, cur_sentence_find_exclude_words, dish_VA_features_dict, dish_VV_features_dict)
            main_dish_ls = find_main_dish_ls(cur_word_sentence, cur_pos_sentence, cur_ner_sentence, 2)
            noun_VA_phrase_ls = []
            has_next_sentence_dishes_features_ls  = False
            has_next_2_sentence_dishes_features_ls  = False
            if  main_dish_ls:
                if has_next_sentence and len(next_tongwei_dish_index_ls) == 0 and cur_word_sentence[-1] not in punctuation_ls and not cur_sentence_find_exclude_words :#下一句中菜的名字的个数为0, 并且标点符号不为句号， 而且上一句话中没有发现要排除的词
                    next_sentence_find_exclude_words = False

                    start_index = 0
                    end_index = len(next_word_sentence)
                    noun_VA_phrase_pair_ls = get_next_sentence_VA_features(next_word_sentence, next_pos_sentence, next_ner_sentence, start_index, end_index, next_tongwei_noun_phrase_ls, VA_word_dict)
                    noun_VA_phrase_ls =  get_VA_feature_names(next_word_sentence, next_pos_sentence, next_ner_sentence,  start_index, end_index, next_tongwei_noun_phrase_ls, noun_VA_phrase_pair_ls, VA_word_dict)
                    next_sentence_dishes_features_ls = combine_dish_noun_VA_phrase_ls(main_dish_ls, noun_VA_phrase_ls, exclude_dict, next_sentence_find_exclude_words)
                    merge_dish_features_dict(dish_VA_features_dict, next_sentence_dishes_features_ls)
                    if noun_VA_phrase_ls:
                        has_next_sentence_dishes_features_ls = True
                    #不需要分析这个句子了
                    sentence_index += 1
                    
                    if has_2_next_sentence  and len(next_2_tongwei_dish_index_ls) == 0  and next_word_sentence[-1] not in punctuation_ls and not  next_sentence_find_exclude_words:#第二句话中包含的对菜名的评价
                        next_2_sentence_find_exclude_words = False

                        start_index = 0
                        end_index = len(next_2_word_sentence)
                        noun_VA_phrase_pair_ls = get_next_sentence_VA_features(next_2_word_sentence, next_2_pos_sentence, next_2_ner_sentence, start_index, end_index,  next_2_tongwei_noun_phrase_ls, VA_word_dict)
                        noun_VA_phrase_ls =  get_VA_feature_names(next_2_word_sentence, next_2_pos_sentence, next_2_ner_sentence, start_index, end_index, next_2_tongwei_noun_phrase_ls, noun_VA_phrase_pair_ls, VA_word_dict)
                        next_2_sentence_dishes_features_ls = combine_dish_noun_VA_phrase_ls(main_dish_ls, noun_VA_phrase_ls, exclude_dict, next_2_sentence_find_exclude_words)
                        merge_dish_features_dict(dish_VA_features_dict, next_2_sentence_dishes_features_ls)
                        if noun_VA_phrase_ls:
                            has_next_2_sentence_dishes_features_ls = True
                        #不需要分析这个句子了
                        sentence_index += 1
                else:#下一个菜可能是包含关系, 例如：里面的豆腐很好吃, 中的
                    pass
            """
            is_print = True
            if len(main_dish_ls) == 1:
                is_print = False
            if has_next_sentence and is_print:
                print " ".join(cur_word_sentence)+" " + " ".join(next_word_sentence) 
            else:
                if is_print:
                    print " ".join(cur_word_sentence)
            """
        else:
            cur_sentence_find_exclude_words = False
            get_cur_sentence_dish_features(cur_word_sentence, cur_pos_sentence, cur_ner_sentence, VA_word_dict, VV_word_dict, exclude_dict, cur_sentence_find_exclude_words, dish_VA_features_dict, dish_VV_features_dict)
        sentence_index += 1

        
def get_review_dishes_features(word_ls, pos_ls, ner_ls, VA_word_dict, VV_word_dict, exclude_dict, dish_VA_features_dict, dish_VV_features_dict):
    word_ls, pos_ls, ner_ls = merge_dish(word_ls, pos_ls, ner_ls)
    word_sentence_ls, pos_sentence_ls, ner_sentence_ls = split_review(word_ls, pos_ls, ner_ls)
    get_dish_feature(word_sentence_ls, pos_sentence_ls, ner_sentence_ls, VA_word_dict, VV_word_dict, exclude_dict, dish_VA_features_dict, dish_VV_features_dict)

        
def test_get_dish_feature(word_line_ls,  pos_line_ls, ner_line_ls, VA_word_dict, VV_word_dict, exclude_dict):
    for i in range(100):
        word_ls, pos_ls, ner_ls = merge_dish(word_line_ls[i], pos_line_ls[i], ner_line_ls[i])
        word_line_ls[i] = word_ls
        pos_line_ls[i] = pos_ls
        ner_line_ls[i] = ner_ls
        print " ".join(word_ls)
        dish_VA_features_dict = {}
        dish_VV_features_dict = {}
        word_sentence_ls, pos_sentence_ls, ner_sentence_ls = split_review(word_line_ls[i], pos_line_ls[i], ner_line_ls[i])
        get_dish_feature(word_sentence_ls, pos_sentence_ls, ner_sentence_ls, VA_word_dict, VV_word_dict, exclude_dict, dish_VA_features_dict, dish_VV_features_dict)
        print_dish_features_dict(dish_VA_features_dict)
 #       print_dish_features_dict(dish_VV_features_dict)

def get_line_ls_from_file(file_name, out_ls):
    for line in open(file_name, 'rb'):
        fields = line.rstrip().split(' ')
        out_ls.append(fields)

def test_merge_dish(word_line_ls,  pos_line_ls, ner_line_ls):
    for i in range(5):
        print ' '.join(word_line_ls[i])
        print ' '.join(pos_line_ls[i])
        print ' '.join(ner_line_ls[i])
        word_ls, pos_ls, ner_ls = merge_dish(word_line_ls[i], pos_line_ls[i], ner_line_ls[i])
        word_line_ls[i] = word_ls
        pos_line_ls[i] = pos_ls
        ner_line_ls[i] = ner_ls
        print ' '.join(word_line_ls[i])
        print ' '.join(pos_line_ls[i])
        print ' '.join(ner_line_ls[i])

        
def test_split_review(word_line_ls):
    for i in range(2):
        print ' '.join(word_line_ls[i])
        word_sentence_ls, pos_sentence_ls, ner_sentence_ls = split_review(word_line_ls[i])
        for word_ls in sentence_ls:
            print ' '.join(word_ls)


def test_tongwei_noun_phrase(word_line_ls, pos_line_ls, ner_line_ls):
    for i in range(20):
        word_ls, pos_ls, ner_ls = merge_dish(word_line_ls[i], pos_line_ls[i], ner_line_ls[i])
        tongwei_noun_phrase_ls = get_tongwei_noun_phrase_ls(word_ls, pos_ls)
        print ' '.join(word_ls)
        print ' '.join(pos_ls)
        out_ls = []
        for phrase_ls in tongwei_noun_phrase_ls:
            tmp_ls = []
            for start_end_pair in phrase_ls:
                start, end = start_end_pair
                tmp_ls.append(''.join( word_ls[start:end]))
            out_ls.append('&&'.join(tmp_ls))
        print ' '.join(out_ls)

        
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
        
def get_dict_from_file(my_dict, file_name):
    for line in open(file_name, 'rb'):
        line = line.strip()
        fields = line.split(' ')
        if is_number(fields[1]):
            my_dict[fields[0]] = fields[1]
    return 

def get_set_from_file(my_dict, file_name):
    for line in open(file_name, 'rb'):
        line = line.strip()
        my_dict[line] = ""
        
    return 


def find_after_VA_features(word_ls, pos_ls, ner_ls, tongwei_noun_phrase_ls, start_index, end_index, VA_word_dict):
    """
        VA featue 要在start_index和end_index之间
    """
    if len(word_ls) != len(pos_ls):
        print "word_ls length not equal pos_ls"
        exit()

    length = len(word_ls)

    
    VA_feature_ls =[]
    VA_phrase_ls = []
    i = end_index -1
    while i >= start_index:
        if word_ls[i] in VA_word_dict:
            #很不错 非常的不错
            start = i - 1
            if word_ls[i-1] in de_word_ls:
                start == i-2
            while pos_ls[start] == 'AD':
                start = start -1
            VA_phrase_ls.append(word_ls[start+1:i+1])
            tongwei_idx = get_last_noun_phrase(tongwei_noun_phrase_ls, start +1,  -1, 0) 
            if not is_int(tongwei_idx): #没有找到名词
                pass
            else:
                VA_feature_ls.append((tongwei_idx, (start+1, i+1)))
            
            #鱼的味道很不错，口感很不错， 鱼味道不错, 卖相和口感都不错, “宫爆鸡丁”不错，味道么不错， 一个人看看也不错

            i = start
        else:
            i = i-1

    out_ls = []
    for tongwei_idx, VA_phrase_idx_pair in VA_feature_ls:
        phrase_ls =[]
        for start_end_pair in tongwei_noun_phrase_ls[tongwei_idx]:
            start,end = start_end_pair
            phrase_ls.append(''.join(word_ls[start:end]))
        VA_start, VA_end = VA_phrase_idx_pair
        out_ls.append( '&&'.join(phrase_ls)+' '+ ''.join(word_ls[VA_start:VA_end]))
    if len(out_ls) > 0:
        pass
#         print ' '.join(word_ls)
#        print '\t'.join(out_ls)
#        print ""
    return VA_feature_ls

def transform_VA_feature(word_ls, pos_ls, ner_ls, tongwei_noun_phrase_ls, tongwei_dish_index_ls, tongwei_dish_index_idx, VA_pair_feature_ls, exclude_dict, find_exclude_words ): 
    #提取VA_feature, [(红烧肉， [("", 不错), ("", 不腻)， (肉质, 新鲜)]), (水煮牛肉， [("", 很好吃)，(味道, 蛮不错)])]
    #暴风雪系列的抹茶
    #红烧鱼的味道不错， 铁板鱿鱼和红烧鱼味道不错, 铁板鱿鱼和红烧鱼不错
    dishes_features_ls = []
    tongwei_dish_phrase_ls = tongwei_noun_phrase_ls[tongwei_dish_index_ls[tongwei_dish_index_idx]]
    tongwei_dish_idx = tongwei_dish_index_ls[tongwei_dish_index_idx]
    find_exclude_words = False

    # 找到 具体包含哪些 dish， 有可能两个dish
    dish_ls =[]
    for start_end_pair in tongwei_dish_phrase_ls:
        start, end = start_end_pair
        while start < end:
            if (ner_ls[start] == '@food'):
                if  start +2 < end and word_ls[start + 1 ] == '的' and ner_ls[start + 2] == '@food':
                    dish_ls.append(''.join(word_ls[start:start+3]))
                else:
                    dish_ls.append(''.join(word_ls[start:start+1]))
                break
            else:
                start +=1

    #处理鱼的味道不错， 鱼味道不错
    tongwei_noun= ""
    last_start_end_pair = tongwei_dish_phrase_ls[-1]
    start, end = last_start_end_pair
    i = end - 1
    while i >= start:
        if ner_ls[i] == '@food':
            break
        i -= 1
    if i+1 < end and word_ls[i+1] == '的':
        i +=1
    tongwei_noun_feature = ''.join( word_ls[ i+1:end])
        

    #反序遍历VA_feature_ls, 如果发现不符合的例子，break 掉, 并且bad_match 返回 
    find_bad_match = False
    VA_phrase_feature_ls = []
    i = len(VA_pair_feature_ls) - 1
    while i >= 0:
        tongwei_idx, VA_phrase_idx_pair = VA_pair_feature_ls[i]
        VA_start, VA_end = VA_phrase_idx_pair
        #check 找到的pair中是否包含，环境不错、服务不错
        for start_end_pair in tongwei_noun_phrase_ls[tongwei_idx]:
            start, end = start_end_pair
            for index in range(start, end):
                if word_ls[index] in exclude_dict:
                    find_bad_match = True
                    break
            if find_bad_match:
                break
        if find_bad_match:
            break


        VA_phrase = ''.join(word_ls[VA_start:VA_end])
        if (len(tongwei_noun_phrase_ls) + tongwei_idx) == tongwei_dish_idx:
            VA_phrase_feature_ls.append((tongwei_noun_feature, VA_phrase))
        else:
            for start_end_pair in tongwei_noun_phrase_ls[tongwei_idx]:
                start, end = start_end_pair
                VA_phrase_feature_ls.append((''.join(word_ls[start:end]), VA_phrase))
        i -= 1
    find_exclude_words = find_bad_match

    for dish  in dish_ls:
        if VA_phrase_feature_ls:
            dishes_features_ls.append((dish, VA_phrase_feature_ls))
    return dishes_features_ls
if __name__== '__main__':
    word_line_ls = []
    pos_line_ls = []
    ner_line_ls = []
    get_line_ls_from_file('word_line.txt', word_line_ls)
    get_line_ls_from_file('pos_line.txt', pos_line_ls)
    get_line_ls_from_file('ner_line.txt', ner_line_ls)
#   test_merge_dish(word_line_ls, pos_line_ls, ner_line_ls)
#    test_split_review(word_line_ls)
#    test_tongwei_noun_phrase(word_line_ls, pos_line_ls, ner_line_ls)
    VA_word_dict = {}
    VV_word_dict = {}
    exclude_word_dict = {}
    get_dict_from_file(VA_word_dict, 'VA_word_dict')
    get_dict_from_file(VV_word_dict, 'VV_word_dict')
    get_set_from_file(exclude_word_dict, 'exclude_noun_words')
    test_get_dish_feature(word_line_ls, pos_line_ls, ner_line_ls, VA_word_dict, VV_word_dict, exclude_word_dict)
    
