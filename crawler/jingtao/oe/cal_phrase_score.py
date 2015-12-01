#!/usr/bin/python
#encoding=utf-8

import sys

grade_ls_1 = [u'超级', u'超', u'特别', u'非常', u'忒', u'越来越', u'十分', u'极为', u'极其',  u'巨', u'暴', u'一级', u'格外', u'相当', u'倍儿', u'尤为', u'倍感', u'分外', u'极度', u'及其', u'贼', u'奇', u'异常', u'爆', u'极']
grade_ls_2= [u'很', u'挺', u'几', u'蛮', u'满',u'蠻',u'瞒', u'真的', u'确实', u'的确', u'真是', u'真心', u'真够', u'颇', u'颇为', u'甚为', u'甚', u'太太', u'狠', u'这么', u'那么', u'很是', u'实在是', u'好', u'老']
grade_ls_3 = [u'太', u'越做越']
#较为
grade_ls_4 = [u'比较', u'比价', u'较', u'还算',  u'较为', u'更为']
grade_ls_5 = [u'有点',u'有点儿', u'略', u'略显', u'稍微', u'稍', u'稍嫌', u'略为', u'稍为', u'略偏', u'偏']
#不会 没有什么 算不得 不能算 不能
n_grade_ls = [u'不', u'不怎么', u'不太', u'不算', u'不是', u'说不上', u'算不得', u'算不上', u'不算是', u'不见得', u'算不上', u'谈不上', u'唔', u'吾', u'没有', u'不够', u'没什么', u'没啥', u'没有', u'木有', u'么有', u'没', u'无', u'不至于', u'不会']

def cal_phrase_score(AD_word, base_score, low_score_limit = 0, high_score_limit = 5.0):
    u_word_1 = unicode(AD_word, 'utf-8')
    out_score = 0.0
    if base_score == 3.0:
        #超级咸、很咸、太咸
        if u_word_1 in grade_ls_1 or u_word_1 in grade_ls_2 or u_word_1 in grade_ls_3:
            out_score = 2.5
#elif u_word_1 in grade_ls_4 or u_word_1 in grade_ls_5:
#            out_score = 2.75
        else:
            out_score = 3
    elif base_score > 3.0 and base_score  < 4.0:
        #很爽滑、很爽口：
            if u_word_1 in grade_ls_1:
                out_score = base_score + 0.5
            elif u_word_1 in grade_ls_2  or u_word_1 in grade_ls_3:
                out_score = base_score + 0.25
            elif u_word_1 in n_grade_ls:
                out_score = 2.5
            else:
                out_score = 3.5
    elif base_score >= 4.0:
            if u_word_1 in grade_ls_1:
                out_score = base_score +1
            elif u_word_1 in grade_ls_2  or u_word_1 in grade_ls_3:
                out_score = base_score + 0.5
            elif u_word_1 in grade_ls_4 or u_word_1 in grade_ls_5:
                out_score = base_score - 0.25
            elif u_word_1 in n_grade_ls:
                out_score = 2.0
            else:
                out_score = base_score

    elif base_score < 3.0 and base_score > 2.0:
            if u_word_1 in grade_ls_1:
                out_score = base_score - 0.5
            elif u_word_1 in grade_ls_2  or u_word_1 in grade_ls_3 or u_word_1 in grade_ls_4 or u_word_1 in grade_ls_5:
                out_score = base_score - 0.25
            elif u_word_1 in n_grade_ls:
                out_score = 3.25
            else:
                out_score = base_score
        
    elif base_score <= 2.0:
            if u_word_1 in grade_ls_1:
                out_score = base_score - 1
            elif u_word_1 in grade_ls_2  or u_word_1 in grade_ls_3:
                out_score = base_score - 0.5
            elif u_word_1 in n_grade_ls:
                out_score = 3.5
            else:
                out_score = base_score
    if out_score > high_score_limit:
        out_score = high_score_limit
    if out_score < low_score_limit:
        out_score = low_score_limit
    return out_score

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

de_word_ls = ['的', '地', '得', '之']
def get_score_from_line(line, VA_word_score_dict, AD_set):
    line = line.strip()
    fields = line.split(' ')
    out_ls = []
    i = len(fields)-1
    while i > 0:
        word = fields[i]
        u_word = unicode(fields[i], 'utf-8')
        
        if word in VA_word_score_dict:
            base_score = float(VA_word_score_dict[word])
            VA_phrase_len = 1
            start = i - 1
            end = i
            if start >= 0  and fields[start] in de_word_ls:
                end =  i -1
                start = start -1

            if start >=0  and fields[start] in AD_set:
                VA_phrase_len = VA_phrase_len + 1
                start = start - 1
            if start >=0  and fields[start] in AD_set:
                VA_phrase_len = VA_phrase_len + 1
                start = start -1
    
            score = cal_phrase_score(fields[start+1:end], base_score, VA_phrase_len -1)
        
            if not score:
                score = base_score
            if start+1  == i-1 and end < i:
                out_ls.append(''.join(fields[start+2:i+1]) + ' ' +str(score))
            else:
                
                out_ls.append(''.join(fields[start+1:i+1]) + ' ' +str(score))
                
            i = start 
                
        else:
            i = i-1
    print "\t".join(out_ls)
            



def test():
    VA_word_score_dict = {}
    AD_ls = [u'非常', u'很', u'比较', u'挺', u'太', u'蛮', u'满', u'超级', u'超',u'超级', u'超', u'特别', u'非常', u'忒', u'越来越', u'十分', u'极为',u'极其', u'巨', u'暴', u'一级', u'格外', u'相当',u'倍儿', u'尤为', u'倍感', u'分外', u'极度', u'及其', u'贼', u'奇', u'异常', u'爆', u'极' , u'很', u'挺', u'几', u'蛮', u'满',u'蠻',u'瞒', u'真的', u'确实', u'的确', u'真是', u'真心', u'真够', u'颇', u'颇为', u'甚为', u'甚', u'太太', u'狠', u'这么', u'那么', u'太', u'越做越', u'比较', u'比价', u'较', u'还算',  u'较为', u'更为', u'有点',u'有点儿', u'略', u'略显', u'稍微', u'稍', u'稍嫌', u'略为', u'稍为', u'略偏', u'偏', u'不', u'不怎么', u'不太', u'不算', u'说不上', u'算不得', u'算不上', u'不算是', u'不见得', u'算不上', u'谈不上', u'唔', u'吾', u'没有', u'不够', u'没什么', u'没啥', u'没有', u'木有', u'么有', u'没', u'无', u'不至于', u'不是', u'很是', u'好', u'老']
    AD_set = set()
    for word in AD_ls:
        AD_set.add(word.encode('utf-8'))
    get_dict_from_file(VA_word_score_dict, 'VA_word_dict')
    for line in sys.stdin:
        get_score_from_line(line, VA_word_score_dict, AD_set)

if __name__ == '__main__':
    test()
