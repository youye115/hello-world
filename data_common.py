#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
# 
# Copyright (c) 2016 Baidu.com, Inc. All Rights Reserved
# 
########################################################################
 
"""
File: data_common.py
Author: spider(spider@baidu.com)
Date: 2016/07/07 16:09:59
"""
import os
import sys
import json
import math
import re
import random
import pickle
#from numpy import * 
#from numpy import linalg as la
bin_path = os.path.abspath(os.path.dirname(__file__))
data_path = os.path.join(bin_path, '../data')

#filename = "../data/poiname_kind_right.out"
#filename = os.path.join(data_path, "poiname_kind_right.out")
pre_learn_path = os.path.join(data_path, "learn_data")
if not os.path.exists(pre_learn_path):
    os.mkdir(pre_learn_path)
pre_test_path = os.path.join(data_path, "test_data")
if not os.path.exists(pre_test_path):
    os.mkdir(pre_test_path)

raw_file = os.path.join(data_path, 'kinds_poiname_wordset')
file_extend_kinds = os.path.join(data_path, 'kinds_poiname_wordset_ex')
fn = 'kinds_poiname_wordset_ex'
learn_raw_filename = os.path.join(pre_learn_path, fn)
test_raw_filename = os.path.join(pre_test_path, fn)
file_tree_input_dataset = os.path.join(pre_learn_path, "tree_input2.data")
file_tree_word_set = os.path.join(pre_learn_path, "tree_word_set")
file_tree_label = os.path.join(pre_learn_path, "tree_learn_labels")
file_tree_kind = os.path.join(pre_learn_path, "tree_all_kinds")
file_exact_dict = os.path.join(data_path, "exact.data")
file_word_idf = os.path.join(data_path, "word_idf.data")
file_test_datas = os.path.join(pre_test_path, "tree_test.datas")
file_test_data_labels = os.path.join(pre_test_path, "tree_test.labels")
file_test_data_word = os.path.join(pre_test_path, "tree_test.word")
file_kind_levels_name = os.path.join(data_path, "kind_levels.txt")


def dumpData(data, filename):
    file = open(filename, 'w')
    pickle.dump(data, file)
    file.close()


def loadData(filename):
    file = open(filename, 'r')
    data = pickle.load(file)
    file.close()
    return data


def print_r(a):
    print json.dumps(a, ensure_ascii=False)
    return json.dumps(a, ensure_ascii=False)

def get_kls():
    file = open(file_kind_levels_name)
    dict_kind = {}
    for line in file.readlines()[1:]:
        (l1, l2, l3, l4, kind) = line.strip().split('\t')
        if kind in dict_kind:
            print line, "重复啦啦啦啦啦"
        dict_kind[kind] = (l1, l2, l3, l4)
    file.close()
    return dict_kind

def load_brand_map(dict_kind):
    dict_brand_kind = {}
    for kind, kl in dict_kind.items():
        if kl[3] != '':
            dict_brand_kind[kl[3]] = kind
    return dict_brand_kind


def loadFile(filename):
    list_x = []
    file = open(filename, 'r')
    for line in file:
        w = line.strip()
        if w == '':
            continue
        list_x.append(w.decode('utf-8'))
    return list_x 

def load_word_list():
    filename = os.path.join(data_path, 'white_list')
    #dict_word_kind = {}
    dict_s_word = {}
    for line in open(filename, 'r'):
        if line.strip() == '':
            continue
        arr = line.strip().decode('utf-8').split()
        word = arr[0]
        w = word[0]
        if w not in dict_s_word:
            dict_s_word[w] = []
        dict_s_word[w].append(word)

    filename_extend = os.path.join(data_path, 'word_set_uniq.txt')
    file = open(filename_extend, 'r') 
    for line in file:
        word = line.strip().decode('utf-8')
        w = word[0]
        if w not in dict_s_word:
            dict_s_word[w] = []
        dict_s_word[w].append(word)
    
    for w in dict_s_word:
        wl = dict_s_word[w]
        dict_wl_len = {word:len(word) for word in wl}
        wl_s = sorted(dict_wl_len.items(), key = lambda d:d[1], reverse=True)
        dict_s_word[w] = [i for i, l in wl_s]
    print len(dict_s_word)
    return dict_s_word 

def load_black_list():
    filename = os.path.join(data_path, 'black_list')
    black_word_set = loadFile(filename)
    black_word_set = set(black_word_set)
    return black_word_set

def load_white_list():
    filename = os.path.join(data_path, 'white_list')
    white_list = set(loadFile(filename))
    return white_list


def load_suffix_list():
    filename = os.path.join(data_path, 'need_merge_suffix.txt')
    suffix_list = loadFile(filename)
    suffix_list = set(suffix_list)
    return suffix_list
