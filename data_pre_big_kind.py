#!/usr/bin/env python
# encoding: utf-8
# 访问 http://tool.lu/pyc/ 查看更多信息
'''
File: judge.py
Author: caoxuehui(caoxuehui@baidu.com)
Date: 2016/07/01 15:00:49
'''
import os
import sys
import json
import math
import re
import random
from data_common import *

KIND_LEVEL = 4
dict_word = {}
dict_kind = {}
dict_poikind = {}
list_feature = []
KIND_NUMS = 500
WORD_IDITF = 0.01
topNFeat = 200

dict_kind_levels = get_kls()
dict_brand_kind = load_brand_map(dict_kind_levels)

def word_add(word, kind, dict_word, dict_word_kindcount):
    if word not in dict_word:
        dict_word[word] = [1, [kind]]
        dict_word_kindcount[word] = {kind:1}
    else:
        dict_word[word][0] += 1
        if kind not in dict_word[word][1]:
            dict_word[word][1].append(kind)
        if kind not in dict_word_kindcount[word]:
            dict_word_kindcount[word][kind] = 1
        else:
            dict_word_kindcount[word][kind] += 1

black_word_set = load_black_list()
def filter_raw_word(w):
    """
    """
    if w in black_word_set:
        return True
    else:
        return False

num_pattern = re.compile('\d+$')
word_pattern = re.compile('\w$')
def trans_raw_word(w):
    """
    @function : 将数字转换成(\d+)表达， 单个字母转换成(\w)表示
    @input:     w
    @output:    wn
    """
    if re.match(num_pattern, w):
        return '(\d+)'
    if re.match(word_pattern, w):
        return '(\w)'
    if w == "（":
        return '('
    if w == "）":
        return ')' 
    return w 

suffix_list = load_suffix_list()
def merge_suffix(word_list):
    if len(word_list) > 1:
        if word_list[-1] in suffix_list:
            word_list[-2] += word_list[-1]
            word_list.remove(word_list[-1])
            return word_list
    return word_list


white_list = load_white_list()
def merge_wordlist(word_list):
    len_w = len(word_list)
    i = len_w -1
    while i >= 1:
        if word_list[i-1] + word_list[i] in white_list:
            word_list[i-1] = word_list[i-1] + word_list[i]

            word_list.remove(word_list[i])

        i -= 1
    return word_list



def filter_wordlist(word_list):
    """
    """
    word_list = [trans_raw_word(w) for w in word_list]
    if word_list.count("(") > 0  and  word_list.count(")") > 0:
        tmp_word_list  = word_list[:word_list.index("(")]
        tmp_word_list.extend(word_list[word_list.index(")")+1:])
        word_list = tmp_word_list
    word_list = [w.decode('utf-8') for w in word_list if not filter_raw_word(w)]
    nword_list = merge_suffix(word_list)
    nword_list = merge_wordlist(nword_list)
    """
    len_w = len(word_list)
    nword_list = []
    i = len_w -1
    while i >= 0:
        last_word = None
        if len(word_list[i]) == 1:
            if i == len_w-1:
                i -= 1
                continue
            if i-2>=0 and (word_list[i-2] == '(\d+)' or word_list[i-2] == '(\w)'):
                nword_list.append(word_list[i-2] + word_list[i-1] + word_list[i])
                i -= 2
            elif i-1 >=0:
                nword_list.append(word_list[i-1] + word_list[i])
                i -= 1
        else:
            nword_list.append(word_list[i])
        i -= 1
    """
    
    if len(nword_list) >0:
        nword_list.append( nword_list[-1] + "$")
    # 不在最后一个的单字过滤掉
    word_list = [w.encode('utf-8') for w in nword_list] 
    #word_list = [w for w in nword_list if len(w.decode('utf-8')) > 1] 
    return word_list

        
def loadRawData(filename):
    dict_word = {}
    dict_kind_name = {}
    dict_kind_word = {}
    dict_word_kindcount = {} #每个单词在kind中出现的次数
    dict_kind_count = {} 
    file = open(filename, 'r')
    lines = file.readlines()
    file.close()
    list_data = []
    print len(lines)
    line_count = 0
    for line in lines:
        line_count += 1
        if line_count % 100000 == 0:
            print line_count
        (k1, k2, k3, k4, kd, poiname, poiname_seg) = line.strip().split('\t')
        kl = (k1, k2, k3, k4, kd)
        kind = kl[KIND_LEVEL]
        word_list = poiname_seg.split()
        word_list = filter_wordlist(word_list)
        if len(word_list) == 0:
            continue
        list_data.append((word_list, kind)) 
        for word in word_list:
            word_add(word, kind, dict_word, dict_word_kindcount)

        if kind in dict_kind_name:
            dict_kind_count[kind] += 1
            dict_kind_name[kind].append(poiname)
            for word in word_list: 
                dict_kind_word[kind].add(word)
        else:
            dict_kind_count[kind] = 1
            dict_kind_name[kind] = [poiname]
            dict_kind_word[kind] = set(word_list)
   
    ##防止样本不均匀
    for w, dk in dict_word_kindcount.items():
        for k in dk:
            dk[k] = float(dk[k]) / dict_kind_count[k]
        
    return list_data, dict_word, dict_kind_name, dict_kind_word, dict_word_kindcount

def getDataList(list_data, list_labels, dict_kind_word):
    list_vec = []
    list_kind = []
    len_label = len(list_labels)
    for (word_list, kind) in list_data:
        vec = [0]*len_label
        for i in range(len_label):
            label = list_labels[i]
            for w in word_list:
                if w in dict_kind_word[label]:
                    vec[i] += 1
        list_vec.append(vec)
        list_kind.append(kind)
    return list_vec, list_kind
   
def loadRawFile(filename):
    data_list = []
    file = open(filename, 'r')
    lines = file.readlines()
    file.close()
    for line in lines:
        (k1, k2, k3, k4, kd, poiname, poiname_seg) = line.strip().split('\t')
        kl = (k1, k2, k3, k4, kd)
        kind = kl[KIND_LEVEL]
        word_list = poiname_seg.split()
        word_list = filter_wordlist(word_list)
        data_list.append((kind, word_list, poiname))
    return data_list

        
def calTF_IDF(dict_word, kind_count):
    word_count = 0
    for w, (c, kl) in dict_word.items():
        word_count += c
    word_count = float(word_count)
    print "all word count is " , word_count
    kind_count = float(kind_count)
    dict_word_tfidf = {}
    dict_special_word = {}
    for word in dict_word:
        if filter_raw_word(word):
            continue
        wc = dict_word[word][0]
        wk = len(dict_word[word][1])
        tf = wc / word_count
        idf = math.log((kind_count + 1 )/ (wk + 1))
    
        word_tf_idf = round((tf + 1) * idf * 10000, 4)# * len(word.decode('utf-8'))
        dict_word_tfidf[word] = word_tf_idf
        if wk == 1:
            word_tf_idf = word_tf_idf * 2
        try:
            if word.decode('utf-8')[-1] == u'$':
                dict_word_tfidf[word] = word_tf_idf * 3
            elif word.decode('utf-8')[-1] == u'#':
                dict_word_tfidf[word] = word_tf_idf * 2
            else:
                dict_word_tfidf[word] = word_tf_idf 
        except Exception as e:
            print e
            print word

    return dict_word_tfidf


def createVec(word_set, word_list, dict_word_tfidf):
    len_word = len(word_set)
    data_tmp = [0] * len_word
    is_in = False
    for w in word_list:
        if w in word_set:
            iw = word_set.index(w)
            data_tmp[iw] = 1 
            is_in = True
            continue
    return (is_in, data_tmp)


def createInput(word_set, dict_kind, dict_word_tfidf):
    '''
    '''
    list_data = []
    len_word = len(word_set)
    i = 0
    list_kind = []
    list_labels = dict_kind.keys()
    for (kind, poiname_seg_list) in dict_kind.items():
        for poiname_seg in poiname_seg_list[:KIND_NUMS]:
            word_list = poiname_seg.split()
            word_list[-1] += "$"
            (is_in, data_tmp) = createVec(word_set, word_list, dict_word_tfidf)
            if is_in:
                i += 1
                list_data.append(data_tmp)
                list_kind.append(kind)
                continue

    return (list_data, list_kind)


def word_label(word_set, data):
    list_word = []
    len_s = len(word_set)
    for i in range(len_s):
        if data[i] != 0:
            list_word.append(word_set[i])
            continue
    return list_word


def get_vec_weight(data, dict_word_tfidf, word_set):
    weight = 0
    len_s = len(word_set)
    for i in range(len_s):
        if data[i] != 0:
            weight += dict_word_tfidf[word_set[i]]
            continue
    return weight


def norm_wordkindcount():
    #归一化
    pass

def brand_map(poiname):
    """
    @function : 查找poi是否直接对应 品牌名称
    @input    : poiname
    @output   : kind or None
    """
    if poiname in dict_brand_kind:
        return dict_brand_kind[poiname]
    for brand, kind in dict_brand_kind.items():
        if poiname.find(brand) != -1:
            return kind
    return None

def predict_kind(poiname, word_list, dict_kind_word, dict_word_kindcount, dict_word_tfidf, dict_test_kind):
    """
    @function : 预测分类
    @input    : poiname, ...
    @output   : is_word_pre---是否可分类
                wl------------分类的概率
    """
    is_word_pre = False
    wl = []
    bk = brand_map(poiname)
    if bk is not None:
        is_word_pre = True
        wl.append({poiname:(bk, 1.0, 1.0)})
        return is_word_pre, wl
    for word in word_list:
        for k, ws in dict_kind_word.items():
            if word in ws and word in dict_word_tfidf:
                kw = math.log(1+float(dict_word_kindcount[word][k])) * 10
                tfidf = math.log(1+dict_word_tfidf[word]) * 10
                dict_test_kind[k] += kw * tfidf 
                is_word_pre = True
                wl.append({word:(k, dict_word_tfidf[word], kw)})
    return is_word_pre, wl

def get_test_datas(dict_word_tfidf, dict_kind_word, dict_word_kindcount):
    
    data_list = loadRawFile(test_raw_filename)
    kind_list = dict_kind_word.keys()
    right_num = 0
    all_num = 0
    
    top_count = 3
    for (kind, word_list, poiname) in data_list:
        dict_test_kind = {}.fromkeys(kind_list, 0)
        all_num += 1
        if len(word_list) == 0 :
            continue
        is_word_pre, wl = predict_kind(poiname, word_list, dict_kind_word, dict_word_kindcount, dict_word_tfidf, dict_test_kind)
        if not is_word_pre: 
            last_word = word_list[0].decode('utf-8')
            if len(last_word) > 2 :
                word_list.append(last_word[-2:].encode('utf-8'))
            is_word_pre, wl = predict_kind(poiname, word_list, dict_kind_word, dict_word_kindcount, dict_word_tfidf, dict_test_kind)
            
        sort_k_w = sorted(dict_test_kind.items(), key = lambda d:d[1], reverse=True)
        is_right = False
        for i in range(top_count):
            pre_kind = sort_k_w[i][0]
            if kind == pre_kind:
                is_right = True
                break
        if is_right:
            right_num += 1
        else:
            wins = []
            for w in wl:
                wins.extend(w.keys())
            wins = set(wins)
            pre_kind = sort_k_w[0][0]
            print "word: %s , real_kind: %s , pre_kind: %s" % (poiname, kind, pre_kind)
            print "real kind levles : %s" % json.dumps(dict_kind_levels[kind], ensure_ascii=False)
            print "pre kind levels is %s" % json.dumps(dict_kind_levels[pre_kind], ensure_ascii=False)

            print "sort kind weight is %s" % json.dumps(sort_k_w[:10], ensure_ascii=False)
            print "seg word is 【%s】 , in wordset word is 【%s】" % (" ".join(word_list), " ".join(list(wins)))

            #print "in pre word list is %s" % (json.dumps(wl, ensure_ascii=False))
            print "---"*10
    print "right num is %s , total num is %s, right per is %.2f %%" % \
        (right_num, all_num, (float(right_num)/all_num)*100)

def main():
    list_data, dict_word, dict_kind_name, dict_kind_word, dict_word_kindcount = loadRawData(learn_raw_filename)
    list_labels = dict_kind_word.keys()
    dict_word_tfidf = calTF_IDF(dict_word, len(list_labels))
    return dict_word_tfidf, dict_kind_word, dict_word_kindcount
    
if __name__ == '__main__':
    print "kind_level", KIND_LEVEL
    dict_word_tfidf,  dict_kind_word, dict_word_kindcount = main()
    get_test_datas(dict_word_tfidf, dict_kind_word, dict_word_kindcount)
