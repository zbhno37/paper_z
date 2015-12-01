#encoding=utf-8
import sys

t = [[600,800],[400,600],[200,400],[0,200]]

def load_from_file(file):
    lines = open(file).readlines()
    rs = []
    for line in lines:
        arr = line.split(' ')
        rs.append(arr)
    return rs

def load_pred_file(pred_file):
    lines = open(pred_file).readlines()
    rs = []
    tmp = []
    for line in lines:
        if line=='\n' and len(tmp)!=0:
            rs.append(tmp)
            tmp=[]
        else:
            tmp.append(line.strip())
    print len(rs)
    return rs
base_dir = '/home/b2/code/ljt/dianping_nlp/dish_sentiment'
evaluate_dir = base_dir+'/evaluate_set/'
pred_dir = base_dir+'/feature_VA_match_result/'
def load_crf_tag(file):
    lines = open(file).readlines()
    rs = []
    fd = {}
    if len(lines) > 1:
        for line in lines[1:]:
            arr = line.split(' ')
            #print arr
            tmp = []
            for e in arr:
                if e!='' and e!='\n':
                    tmp.append(e)
            if tmp :
                if fd.has_key(''.join(tmp).strip()):
                    continue
                else:
                    fd[''.join(tmp).strip()]=1
                    rs.append(tmp)
    '''
    if len(rs)>0:
        for e in rs:
            print len(e),' '.join(e) 
    '''
    return rs

def count(correct_tags, pred_tags):
    pred_c,pre_cc,test_c,test_cc = (0.0,0.0,0.0,0.0)
    pred_c = len(pred_tags)
    test_c = len(correct_tags)
    for arr in pred_tags:
        for cor in correct_tags:
            if ''.join(arr).strip()==''.join(cor).strip():
                pre_cc += 1
    for cor in correct_tags:
        for arr in pred_tags:
            if ''.join(cor).strip()==''.join(arr).strip():
                test_cc += 1
    #print pred_c,pre_cc,test_c,test_cc
    return (pred_c,pre_cc,test_c,test_cc)

#according sentence puction split review to sentences
sentence_pu = ['。','！','？','；','～']
def split_to_sentence(word_arr, pred_arr):
    rs = []
    word_rs, pred_rs = ([],[])
    b, l= 0,0
    for ind,ch in enumerate(word_arr):
        if ch in sentence_pu :
            if b < ind:
                word_rs.append(word_arr[b:ind+1])
                pred_rs.append(pred_arr[b:ind+1])
            l = ind
            b = ind + 1
    if l < len(word_arr):
        word_rs.append(word_arr[l:])
        pred_rs.append(pred_arr[l:])
    return (word_rs,pred_rs)

def parse_pred_ls(word_ls, pred_ls):
    if len(word_ls)!=len(pred_ls):
        print 'wrong num between word ls and pred ls' ,len(word_ls), len(pred_ls)
        print ' '.join(word_ls),word_ls
        print ' '.join(pred_ls)
        sys.exit(0)
    s_word_ls, s_pred_ls = split_to_sentence(word_ls, pred_ls)
    pred_tags = []
    for cur in xrange(len(s_pred_ls)):
        cur_sentence = s_word_ls[cur]
        cur_pred_ls = s_pred_ls[cur]
        food_ls ,nn_ls, e2, e3= ([],[],[],[])
        for ind, p in enumerate(cur_pred_ls):
            if p=='F':
                food_ls.append(cur_sentence[ind])
            elif p=='N':
                nn_ls.append(cur_sentence[ind])
            elif p=='E2':
                e2.append(cur_sentence[ind])
            elif p=='E3':
                e3.append(cur_sentence[ind])
        if len(food_ls)!=0:
            for f in food_ls:
                tmp = []
                for e in e2:
                    tmp.append(f)
                    tmp.append(e)
                if len(tmp)==2:
                    pred_tags.append(tmp)
                '''
                tmp = []
                for e in e3:
                    tmp.append(f)
                    tmp.append(e)
                if len(tmp)==2:
                    pred_tags.append(tmp)
                '''
                for n in nn_ls:
                    tmp1 = []
                    for ee in e3:
                        tmp1.append(f)
                        tmp1.append(n)
                        tmp1.append(ee)
                    if len(tmp1)==3:
                        pred_tags.append(tmp1)
                
    return pred_tags

if __name__=='__main__':
    num = sys.argv[1]
    word_lines = load_from_file('merge_dish_word_line.txt')    
    ap,ar,af = (0.0,0.0,0.0)
    '''
    pc,pcc,tc,tcc = (0.0,0.0,0.0,0.0)
    for i in xrange(int(num)):
        #pc,pcc,tc,tcc = (0.0,0.0,0.0,0.0)
        c_tags = load_crf_tag(evaluate_dir+str(i))
        p_tags = load_crf_tag(pred_dir+str(i))
        pn,pcn,tn,tcn = count(c_tags,p_tags)
        pc += pn
        pcc += pcn
        tc += tn
        tcc += tcn
    ap = pcc/pc
    ar = tcc/tc
    af = (2*ap*ar)/(ap+ar)
    print 'test count: %s precision: %f  recall:  %f  f-measure:  %f'%(num,ap,ar,af)
    '''
    for i in xrange(int(num)):
        b,e = t[i]
        pred_lines = load_pred_file('crf_test_%d.txt'%(i))
        k=0
        pc,pcc,tc,tcc = (0.0,0.0,0.0,0.0)
        for j in xrange(b,e):
            #print 'j:%d,k:%d'%(j,k)
            c_tags = load_crf_tag(evaluate_dir+str(j))
            p_tags = parse_pred_ls(word_lines[j], pred_lines[k])
            k += 1
            pred_num, pred_correct_num, test_num, test_correct_num = count(c_tags,p_tags)
            pc += pred_num
            pcc += pred_correct_num
            tc += test_num
            tcc += test_correct_num
        print 'all count: ',pc,pcc,tc,tcc
        p = pcc/pc
        r = tcc/tc
        f = 2*(p*r)/(p+r)
        print '----------------\ntest %s :  precision %f   recall : %f  f_measure : %f'%(i,p,r,f)
        ap += p
        ar += r
        af += f
    print 'all : precision: %f  recall: %f  f_measure: %f '%(ap/int(num),ar/int(num),af/int(num))
