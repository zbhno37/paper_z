#-*- coding:utf-8 -*-  

import word2vec
import time
from sklearn import cross_validation,linear_model
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
import numpy as np
import pickle

train_data_path = './pos_all.txt'
pu_arr = ['〉','〈','▽',' 。','，','、','；','：','？','！','“','”','.','.','【','】','[',']','"','"','（','）','(',')','%','$','@','#','!','?',',','&','*','<<','>>',':','_','-','+']
enum_arr = [1,2,3,4,5,6,7,8,9,0]
cnum_arr = ['一','二','三','四','五','六','七','八','九','十','零']

base_dir = '/home/b2/code/all/'
corpus_file = base_dir + 'all.txt'
model_file = base_dir+ 'model_400d.bin'
#model_file = base_dir + 'model_500d.bin'
cluster_txt = base_dir + 'cluster.txt'

def w2v_train():
    print '.....train word2vec start at ', time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    word2vec.word2vec(corpus_file, model_file,size=300, verbose=True,threads=30)
    print '.....finish training word2vec end at ', time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
def is_enum(w):
    for e in w:
        if e not in enum_arr:
            return 0
    return 1

def is_cnum(w):
    for i in xrange(len(w)/3):
        if w[3*i:3*(i+1)] not in cnum_arr:
            return 0
    return 1

def prefix(w):
    if w[0] in enum_arr:
        return 1
    if w[:3] in cnum_arr:
        return 2
    return 0
def suffix(w):
    if w[-1] in enum_arr:
        return 1
    if w[-3:] in cnum_arr:
        return 2
    return 0

def word_count(w):
    return len(w)/3

def load_w2vmodel():
    print '....loading word2vec model_400d at ', time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    model = word2vec.load(model_file)
    print '....finished loading model_400d at ', time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    return model

label_dic = pickle.load(open('ner_w2v/pos_label_dict1.pkl'))

# extract feature 
def pre_process(model, input_data):
    sent_arr = []
    train_set = []
    train_set_x = []
    train_set_y = []
    fopen = open(input_data)
    lines = fopen.readlines()
    fopen.close()
    unlogin_arr = []
    word_arr = []
    #cluster model
    cluster_model = word2vec.load_clusters(cluster_txt)

    for i in xrange(len(lines)):
        if lines[i]!='\n':
            arr = lines[i].split(" ")
            f = [0]*15
            #label of classes based on word2vec
            c_vec = [0]*100
            if arr[0] not in pu_arr : 
                word_arr.append(arr[0])
                f[1] = 1 if is_enum(arr[0])+is_cnum(arr[0])>0 else 0
                f[2],f[3] =(prefix(arr[0]), suffix(arr[0]))
                try:
                    f[4] = 1 if lines[i-1].split(' ')[0] in pu_arr else 0
                except Exception, e:
                    f[4] = 0
                try:
                    f[6] = 1 if lines[i+1].split(' ')[0] in pu_arr else 0
                except Exception, e:
                    f[6] = 0
                f[5] = 1 if f[4]+f[6]==0 else 0
                f[7+word_count(arr[0])] = 1
                #f[1],f[2],f[3],f[4] = (is_enum(arr[0]), is_cnum(arr[0]),prefix(arr[0]), suffix(arr[0]))
                pre_fvec,pre_fvec2,fvec,suf_fvec ,suf_fvec2= (None,None,None,None,None)
                try:
                    pre_fvec = model[lines[i-1].split(" ")[0]].tolist()
                except Exception, e:
                    pre_fvec = [0]*400
                try:
                    fvec = model[arr[0]].tolist()
                except Exception, e:
                    fvec = [0]*400
                    unlogin_arr.append(arr[0])
                
                try:
                    suf_fvec = model[lines[i+1].split(" ")[0]].tolist()
                except Exception, e:
                    suf_fvec = [0]*400
                '''
                try:
                    c_vec[cluster_model[arr[0]]] = 1
                except Exception, e:
                    c_vec = [-1]*100
                '''
                train_set_x.append(pre_fvec+fvec+f+suf_fvec)
                train_set_y.append(label_dic[arr[1].strip()])
            else:
                word_arr.append(arr[0])
                f[0] = 1
                train_set_x.append([0]*800+f+[0]*400)
                train_set_y.append(label_dic['PU'])
   
    #fx = open(input_data+'_x.pkl','w')
    #fy = open(input_data+'_y.pkl','w')
    #pickle.dump(train_set_x,fx)
    #fx.close()
    #pickle.dump(train_set_y,fy)
    #fy.close()
    train_set_x,train_set_y = (np.array(train_set_x),np.array(train_set_y))
    print input_data, ' size : ',len(train_set_x), 'unlogin word size: ',len(unlogin_arr)
    return [train_set_x,train_set_y,word_arr]

def train_model(train_set):
    kv = [0]*50
    for key in label_dic.keys():
        kv[int(label_dic[key])] = key
    clf1 = linear_model.LogisticRegression(C=2, penalty='l2', tol=1e-6)
    clf1.fit(train_set[0],train_set[1])
    model_file = open('/home/b2/code/Python/Theano/models/pos_model_new1','w')
    pickle.dump(clf1, model_file)
    model_file.close()

def comment_model_by_LR(train_set,test_set):
    #print train_set_x.shape
    #print train_set_y.shape
    kv = [0]*50
    for key in label_dic.keys():
        kv[int(label_dic[key])] = key
    print '....start train at ',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    clf1 = linear_model.LogisticRegression(C=2, penalty='l2', tol=1e-6)
    #clf.fit(train_set[0],train_set[1])
    #print '... finish train at ',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    #clf1 = RandomForestClassifier(n_estimators=200)
    #clf1 = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1,max_depth=1, random_state=0)
    clf1.fit(train_set[0],train_set[1])
    print '... finish train at ',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))  
    #clf1 = GradientBoostingClassifier(n_estimators=100, learning_rate=1.0,max_depth=1, random_state=0)
    #scores = cross_validation.cross_val_score(clf, train_set_x, train_set_y, cv=5)
    #scores1 = cross_validation.cross_val_score(clf1, train_set_x, train_set_y, cv=5)
    r = clf1.predict(test_set[0])
    c = 0
    for i in xrange(len(r)):
        if r[i]==test_set[1][i]:
            c+=1
            '''
            print test_set[2][i],test_set[1][i], r[i],
            try:
                print kv[int(test_set[1][i])],kv[int(r[i])]
            except Exception, e:
                continue
            '''
        '''
        else:
            try:
                print test_set[2][i],test_set[1][i], r[i], 
                print kv[int(test_set[1][i])],kv[int(r[i])]
                #print 'diff :', r[i], test_set[1][i]
            except Exception, e:
                continue
        '''
    print 'wrong num ',len(r)-c,' accuracy: ', float(c)/len(r)
    return float(c)/len(r)
    #scores = clf.score(test_set[0],test_set[1])
    #print 'LR scores: ', scores
    #print("Accuracy on LogisticRegression : %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
    #print '....finished at ', time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    #print 'GradientBoosting scores: ',scores1
    #print("Accuracy on RandomForest : %0.2f (+/- %0.2f)" % (scores1.mean(), scores1.std() * 2))
    #print '....finished at ', time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))


if __name__=="__main__":
    #w2v_train()
    #pre_process()
    model = load_w2vmodel()
    rs = 0.0
    
    cross_validate_path = '/home/b2/code/Python/Theano/pos_all.txt'
    train_set = pre_process(model, cross_validate_path)
    train_model(train_set)
    
    #cross_validate_path = '/home/b2/code/Python/Theano/pos_5_fold/pos.txt'
    #train_set = pre_process(model, cross_validate_path)
    #train_model(train_set)
    #for i in xrange(5):
    #    train_set = pre_process(model, cross_validate_path+'_train_'+str(i))
    #    test_set = pre_process(model, cross_validate_path+'_test_'+str(i))
    #    rs+=comment_model_by_LR(train_set, test_set)
    #print rs/5
    
