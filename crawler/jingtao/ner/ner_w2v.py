#-*- coding:utf-8 -*-  

import word2vec
import time 
from sklearn import cross_validation,linear_model,svm, lda, naive_bayes, tree, qda
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier, GradientBoostingClassifier
import numpy 
import pickle
import cal_precision_recall
from sklearn.neural_network import BernoulliRBM
from sklearn import preprocessing
from sklearn.pipeline import Pipeline

train_data_path = './pos_all.txt'
pu_arr = ['〉','〈','▽',' 。','，','、','；','：','？','！','“','”','.','.','【','】','[',']','"','"','（','）','(',')','%','$','@','#','!','?',',','&','*','<<','>>',':','_','-','+']
#pu_arr = [' 。','，','、','；','：','？','！','“','”','.','.','【','】','[',']','"','"','(',')','%','$','@','#','!','?',',','&','*','<<','>>',':','_','-','+']
enum_arr = [1,2,3,4,5,6,7,8,9,0]
cnum_arr = ['一','二','三','四','五','六','七','八','九','十','零']

base_dir = '/home/b2/code/all/'
corpus_file = '/home/b2/code/all/all.txt'
model_file = '/home/b2/code/all/model_500d.bin'
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
    print '....loading word2vec model at ', time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    model = word2vec.load(model_file)
    print '....finished loading model at ', time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    return model

label_dic = pickle.load(open('/home/b2/code/Python/Theano/ner_w2v/pos_label_dict1.pkl'))

# extract feature 
    
label_ner_dict = {'O':0,'B_food':1,'I_food':2}

def preprocess(w2v_model,input_data, ind):
    sent_arr = []
    train_set = []
    train_set_x = []
    train_set_y = []
    fopen = open(input_data+ind+"_df")
    lines = fopen.readlines()
    fopen.close()
    cluster_model = word2vec.load_clusters(cluster_txt)
    unlogin_arr = []
    word_arr = []
    #load fan2jan dict
    fj_dic = pickle.load(open('fj_dic.pkl'))
    #load w2v
    #w2v_arr = pickle.load(open(input_data+ind+"_w2v.pkl"))
    w2v_arr = pickle.load(open(input_data+ind+'_x1_400.pkl'))
    #load pos tag
    pos_arr = pickle.load(open(input_data+"pos_"+ind+'.pkl'))
    if len(lines)!=len(w2v_arr) or len(lines)!=len(pos_arr):
        print 'wrong num of sample! word: %d w2v_arr: %d pos_arr: %d '%(len(lines),len(w2v_arr),len(pos_arr))
        return None
    #cluster model
    #cluster_model = word2vec.load_clusters(cluster_txt)

    for i in xrange(len(lines)):
        if len(lines[i].split(' '))==3:
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
                
                f[-1] = 1 if int(arr[1])==1 else -1
                #f[1],f[2],f[3],f[4] = (is_enum(arr[0]), is_cnum(arr[0]),prefix(arr[0]), suffix(arr[0]))
                pre_fvec,pre_fvec2,fvec,suf_fvec ,suf_fvec2= (None,None,None,None,None)
                pos_pre_vec ,pos_suf_vec= (None,None)
                pre_c_vec,c_vec,suf_c_vec = ([0]*100,[0]*100,[0]*100)
                try:
                    pre_fvec = w2v_arr[i-1]
                    #pre_fvec = w2v_model[lines[i-1].split(' ')[0]].tolist()
                    pos_pre_vec = [0]*34
                    pos_pre_vec[int(pos_arr[i-1])] = 1
                    f[-2] = 1 if int(lines[i-1].split(' ')[1])==1 else -1
                    #pre_c_vec[cluster_model[lines[i-1].split(' ')]] = 1
                except Exception, e:
                    pre_fvec = [0]*200
                    pos_pre_vec = [0]*34
                
                try:
                    suf_fvec = w2v_arr[i+1]
                    #suf_fvec = w2v_model[lines[i+1].split(' ')[0]].tolist()
                    pos_suf_vec = [0]*34
                    pos_suf_vec[int(pos_arr[i+1])] = 1
                    f[-3] = 1 if int(lines[i+1].split(' ')[1]) == 1 else -1
                    #suf_c_vec[cluster_model[lines[i+1].split(' ')]] = 1
                except Exception, e:
                    suf_fvec = [0]*400
                    pos_suf_vec = [0]*34
                
                #try:
                #    c_vec[cluster_model[arr[0]]] = 1
                #except Exception, e:
                #    c_vec[0] = 0
                
                fvec = w2v_arr[i]
                #fvec = [0]*400
                '''
                try:
                    fvec = w2v_model[arr[0]].tolist()
                except Exception, e:
                    tp = arr[0]
                    if fj_dic.has_key(arr[0]):
                        tp = fj_dic[arr[0]]
                    try:
                        fvec = w2v_model[tp].tolist()
                    except Exception, e:
                        unlogin_arr.append(lines[i])
                '''
                pos_fvec = [0]*34
                try:
                    pos_fvec[int(pos_arr[i])] = 1
                except Exception, e:
                    pos_fvec = [0]*34
                #plus_arr = pre_fvec+fvec
                #print type(pre_fvec),type(fvec),type(suf_fvec),type(f)
                train_set_x.append(pre_fvec+fvec+suf_fvec+f+pos_pre_vec+pos_fvec+pos_suf_vec)
                try:
                    #LR
                    train_set_y.append(label_ner_dict[arr[-1].strip()])
                    #neural
                    #train_set_y.append([label_ner_dict[arr[-1].strip()]])
                except Exception, e:
                    print arr[-1].strip()
            else:
                word_arr.append(arr[0])
                f[0] = 1
                pos_fvec = [0]*34
                pos_fvec[label_dic['PU']] = 1
                train_set_x.append([0]*1200+f+[0]*34+pos_fvec+[0]*34)
                train_set_y.append(label_ner_dict['O'])
                #train_set_y.append([label_ner_dict['O']])
    '''
    fx = open(input_data+ind+'_x1_400.pkl','w')
    fy = open(input_data+ind+'_y1_400.pkl','w')
    pickle.dump(train_set_x,fx)
    fx.close()
    pickle.dump(train_set_y,fy)
    fy.close()
    '''
    train_set_x,train_set_y = (numpy.array(train_set_x),numpy.array(train_set_y))
    print input_data, ind,' size : ',len(train_set_x), ' shape:',train_set_x.shape ,' unlogin word size: ',len(unlogin_arr)
    return [train_set_x,train_set_y,unlogin_arr]

reverse_label_ner = {0:"O",1:"B_food",2:"I_food"}

def train_model(train_set):
    clf = linear_model.LogisticRegression(C=2.0, penalty='l2', tol=1e-6)
    clf.fit(train_set[0],train_set[1]) 
    model_file = open('/home/b2/code/opinions-mining/models/ner_model','w')
    pickle.dump(clf, model_file)
    model_file.close()

def ner_model_by_LR(train_set,test_set):
    print '....start train ner_model[LR:with dict feature] at ',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    #clf = linear_model.LogisticRegression(C=2.0, penalty='l2', tol=1e-6)
    clf = pickle.load(open('/home/b2/code/opinions-mining/models/ner_model1'))
    #clf = linear_model.Perceptron(penalty='l2')
    #clf = tree.DecisionTreeClassifier()
    #clf = lda.LDA()
    #clf = qda.QDA(reg_param=-0.1)
    #clf = naive_bayes.MultinomialNB()
    #clf = svm.SVC(C=500.0,kernel='rbf',tol=1e-7)
    #clf = linear_model.SGDClassifier()
    #clf = svm.LinearSVC(C=1.2, penalty='l2', tol=1e-6)
    #clf = AdaBoostClassifier()
    #clf = RandomForestClassifier(n_estimators=10)
    #clf.fit(train_set[0],train_set[1]) 
    #save_model = open('NER_model.pkl','w')
    #pickle.dump(clf,save_model)
    #save_model.close()
    #svm.libsvm.fit(train_set[0],train_set[1])
    print '... finish train ner_model[LR:with dict feature] at ',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    print '... predicting'
    ner_rs = clf.predict(test_set)
    print ner_rs[0],ner_rs[1]
    print '... finish predicting test set at ',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    return ner_rs

def normalization(dataset):
    min_max_scaler = preprocessing.MinMaxScaler()
    result = min_max_scaler.fit_transform(dataset)
    print 'after normalization, shape : ',result.shape
    return result

def rbm_lr(train_set,test_set):
    logistic = linear_model.LogisticRegression(C=1000.0,penalty='l1',tol=1e-6)
    rbm = BernoulliRBM(random_state=0, verbose=True,learning_rate=0.6,n_iter = 5,n_components = 256)
    perce = linear_model.Perceptron()
    classifier = Pipeline(steps=[('Percetron', perce), ('logistic', logistic)])
    print '....start training ner_model[RBM->LR] at ',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    classifier.fit(train_set[0], train_set[1])
    print '....finished training ner_model[Percetron->LR] at ',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    print '..predicting'
    ner_rs = classifier.predict(test_set)
    print ner_rs[0],ner_rs[1]
    print '....finished predicting ner_model[Percetron->LR] at ',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    return ner_rs

def revise(rs):
    nrs = rs[:]
    for i in xrange(len(nrs)):
        if rs[i]==2:
            try:
                if nrs[i-1]!=1:
                    nrs[i] = 0
            except Exception, e:
                c = 0
    return nrs

base_dir = '/home/b2/code/ljt/dianping_nlp/'
pos_data_path = base_dir+'pos_data/five_fold/pos.txt'
ner_data_path = base_dir+'ner_data/five_fold/ner.txt'

if __name__=="__main__":
    model = load_w2vmodel()
    
    #pos_model = pickle.load(open('pos_model.plk','r'))
    precision, recall, f_value = (0.0,0.0,0.0)
    iter = 5
    print '\n'
    for i in xrange(iter):
        print '----------------------------------------------------------'
        ner_train_set = preprocess(model, ner_data_path+'_train_',str(i))
        ner_test_set = preprocess(model, ner_data_path+'_test_',str(i))
        #print numpy.array(ner_test_set[0]).shape
        #print numpy.array(ner_train_set[0]).shape() ,numpy.array(ner_train_set[1]).shape(),numpy.array(ner_test_set[0]).shape()
        #pipe of rbm and lr    
        #nor_ner_train_set_x = normalization(ner_train_set[0])
        #nor_ner_test_set_x = normalization(ner_test_set[0])
        #predict_rs = rbm_lr(ner_train_set, ner_test_set[0])
        #LR
        #predict_rs = ner_model_by_LR([nor_ner_train_set_x,ner_train_set[1]],nor_ner_test_set_x)
        predict_rs = ner_model_by_LR(ner_train_set, ner_test_set[0])
        (p,r,f) = cal_precision_recall.cal(ner_test_set[1],predict_rs)
        #p1,r1,f1 = cal_precision_recall.cal(ner_test_set[1], predict_rs)
        precision += p
        recall += r
        f_value += f
        '''
        for e in ner_train_set[2]:
            print e
        print '**********'
        for e in ner_test_set[2]:
            print e
        '''
        '''
        if len(ner_test_set[2])==len(predict_rs):
            for j in xrange(len(predict_rs)):
                print '%s %s %s'%(ner_test_set[2][j],reverse_label_ner[ner_test_set[1][j]],reverse_label_ner[predict_rs[j]])
        '''
    print 'precision: ',precision/iter, ' recall: ',recall/iter,' F-measure: ',f_value/iter
        
        
    
