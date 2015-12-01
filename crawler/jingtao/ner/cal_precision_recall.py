#!/usr/bin/python
#encoding=utf-8

import sys

def cal(correct, pred):
    #script, test_file = sys.argv

    #fr_test = open(test_file, 'rb')
    #fr_predicted = open(predicted_file, 'rb')
    ner_label_dict = {'1':'O','2':'B_food','3':'I_food'}
    true_label_ls = correct
    predicted_label_ls = pred
    '''
    for line in fr_test:
        if line!='\n':
            fields = line.strip().split('\t')
            #print fields
            if len(fields)>=2:
                true_label_ls.append(ner_label_dict[fields[0]])
                predicted_label_ls.append(ner_label_dict[fields[1]])
    
    for line in fr_test:
        if line!='\n':
            fields = line.strip().split('\t')
            if len(fields)>=3:
                predicted_label_ls.append(fields[2])
    '''
    if len(true_label_ls) != len(predicted_label_ls):
        print len(true_label_ls), len(predicted_label_ls)
        print "test and predicted label file length not equal "
        exit()

    true_label_total_count = 0.0
    true_label_corrected_count = 0.0
    predicted_label_total_count = 0.0
    predicted_label_corrected_count =0.0

    start_pos = -1
    end_pos = -1

    i=0
    while i< len(true_label_ls):
        if int(true_label_ls[i]) == 1:
            start_pos = i
            i += 1
            while( int(true_label_ls[i]) == 2 ):
                i+=1
            end_pos = i
            true_label_total_count += 1
            all_equal = True
            for j in range(start_pos, end_pos):
                if true_label_ls[j] != predicted_label_ls[j]:
                    all_equal = False
            if all_equal:
                true_label_corrected_count += 1

        else:
            i += 1

        
    i=0
    while i< len(true_label_ls):
        if int(predicted_label_ls[i]) == 1:
            start_pos = i
            i += 1
            while( int(true_label_ls[i]) == 2 ):
                i+=1
            end_pos = i
            predicted_label_total_count += 1
            all_equal = True
            for j in range(start_pos, end_pos):
                if true_label_ls[j] != predicted_label_ls[j]:
                    all_equal = False
            if all_equal:
                predicted_label_corrected_count += 1

        else:
            i += 1
    #print 'precision: %f  %f  \n recall:  %f   %f'%(predicted_label_total_count,  predicted_label_corrected_count, true_label_total_count, true_label_corrected_count)
    
    precision = predicted_label_corrected_count/predicted_label_total_count
    recall = true_label_corrected_count/true_label_total_count
    print 'precision: %f  %f  %f'%(predicted_label_total_count,  predicted_label_corrected_count,  precision)
    print 'recall: %f  %f  %f'%(true_label_total_count,  true_label_corrected_count, recall)
    print "F-measure: %f "%( 2*(precision * recall)/(precision + recall))
    return (precision, recall, 2*(precision * recall)/(precision + recall))
    
