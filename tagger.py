# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 14:45:09 2015

@author: shubham
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import string
import nltk
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
from collections import Counter
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from collections import defaultdict
import re

class Tagger(object):
    def __init__(self, filename):
        self.data = []
        with open('data/' + filename) as f:
            for line in f:
                self.data.append(json.loads(line))
            f.close()    
        
        self.positive = defaultdict(lambda:False)
        self.negative = defaultdict(lambda:False)
        with open('positive.txt') as f:
            for line in f:
                self.positive[line.split('\n')[0]] = True
            f.close()
        
        with open('negative.txt') as f:
            for line in f:
                self.negative[line.split('\n')[0]] = True
        self.positive['pros'] = True
        self.negative['cons'] = True
        self.stopwords = stopwords.words('english')
        self.product_tag = {'camera':['camera','megapixel', 'ppi', 'front', 'rear', 'resolution' ],
                            'battery': ['battery','charging','charge','charger', 'longlasting', 'backup', 'internal'],
                            'sound': ['sound','audio','music', 'loud', 'voice', 'volume', 'headphone', 'head phone', 'microphone', 'mic'],
                            'display': ['display', 'touch','screen', 'bright', 'large', 'touchscreen', 'clear'],
                            'specs': ['specs', 'memory','heat', 'ram','bluetooth','android','performance','app', 'cdma', 'repair', 'software'],
                            'build': ['durabl', 'durabil', 'look','color', 'weight','heavy','light', 'lightweight','metal','matte','plastic', 'solid', 'build', 'button']
}
        self.price_tag = ['budget','price','expensive','cheap', 'cost']
        self.delivery_tag = ['delivery','delivered','deliver', 'fast','quick', 'on time', 'service']
        self.warranty_tag = ['warranty']
        self.seller_tag = ['seller', 'vendor']
        
        self.tags = {'product': self.product_tag, 'price': self.price_tag,
                     'seller': self.seller_tag, 'warranty': self.warranty_tag,
                     'delivery': self.delivery_tag}
        self.tagged_data = {}
    def compute_avg_rating(self):
        '''Stores the average rating value in data'''
        for phone in self.data:
            avg = sum(float(review[0]) for review in phone['reviews'])
            if len(phone['reviews'])!=0:
                avg = avg/len(phone['reviews'])
            phone['avg_rating'] = float(avg)
        
    def remove_punc(self, text):
        '''returns the text without any punctuations'''
        return ''.join([t for t in text if t not in string.punctuation and t not in '0123456789' and ord(t)<128])
        
    def clean_data(self, joint=False):
        '''Strips the data of all stopwords, punctuations and tokenizes reviews'''
        for phone in self.data:
            for i, review in enumerate(phone['reviews']):
                review = str(self.remove_punc(review[3].lower().encode('utf-8')))
                tokens = [word for word in nltk.word_tokenize(review) if word not in self.stopwords]
                if joint == True:
                    tokens = ' '.join(tokens)
                phone['reviews'][i].append(tokens)
                
    def get_tag_list(self):
        '''Returns all the tags in a list format. Just a helper function'''
        tag_list = []
        for tag_type, tags in self.tags.items():
            if tag_type!='product':
                tag_list.extend(tags)
            else:
                for attr, attr_tags in self.tags[tag_type].items():
                    tag_list.append(attr)
                    tag_list.extend(attr_tags)
        return tag_list
            
    def filter_bad_reviews(self):
        self.tag_list = self.get_tag_list()
        for phone in self.data:
            phone['noise'] = []
            for i, review in enumerate(phone['reviews']):
                found = False
                for word in self.tag_list:
                    if word in review[4] or word in review[1]:
                        found = True
                        break
                if found == False:
                    phone['noise'].append(review) 
                    phone['reviews'].pop(i)
                    
    def noise_filter(self) :
        list_review_word = []
        ls = SnowballStemmer('english')
        for  phone in self.data:
            phone_reviews = []
            for i , content in enumerate(phone['noise']):
                review = content[4]
                list_words = nltk.word_tokenize(review)
                list_stem_words = [ ls.stem(word) for word in list_words]
                phone_reviews.extend(list_stem_words)
            list_review_word.extend(phone_reviews)
        self.noise_count = Counter(list_review_word)
        
    def tag_data(self):
        '''Tag all the reviews into diff categories and store them under phone titles
        '''
        for phone in self.data:
            self.tagged_data[phone['title']] = {'product':{'camera':set(),'battery':set(), 
                                                            'sound':set(), 'display':set(),
                                                            'build':set(),'specs':set()},
                                                 'delivery':set(),'warranty':set(),
                                                'seller':set(), 'price':set()}
            for i, review in enumerate(phone['reviews']):
                for tag in self.delivery_tag:
                    if tag in review[4] or tag in review[1]:
                        self.tagged_data[phone['title']]['delivery'].add(tuple(review))
                        
                for tag in self.seller_tag:
                    if tag in review[4] or tag in review[1]:
                        self.tagged_data[phone['title']]['seller'].add(tuple(review))
                        
                for tag in self.warranty_tag:
                    if tag in review[4] or tag in review[1]:
                        self.tagged_data[phone['title']]['warranty'].add(tuple(review))
                        
                for tag in self.price_tag:
                    if tag in review[4] or tag in review[1]:
                        self.tagged_data[phone['title']]['price'].add(tuple(review))
                        
                for tag in self.product_tag:
                    for attr in self.product_tag[tag]:
                        if attr in review[4] or attr in review[1]:
                            self.tagged_data[phone['title']]['product'][tag].add(tuple(review))
                        
    def store_mobile_list(self):
        '''Stores a list of all mobile titles in the class'''
        self.phone_list = self.tagged_data.keys()
        self.phone_list.sort()
                    
    def get_mobile_reviews(self, mobile_name, tag = None, attr = None, limit=10):
        '''Returns reviews with specific tags for the input mobile title.'''
        similar_phones = process.extract(mobile_name, self.phone_list, limit = limit)
        print similar_phones
        matched_phone = similar_phones[0][0]
        if tag != None:
            if tag in self.tags.keys():
                if attr==None:
                    return self.tagged_data[matched_phone][tag]
                if attr in self.product_tag.keys() and tag=='product':
                    return self.tagged_data[matched_phone][tag][attr]
                else:
                    return "Attribute not found"
            else:
                return "Tag not found"
        return self.tagged_data[matched_phone]
        
    def review_category(self, review):
        '''Returns the tags of the input review with their sentiment
        '''
        review = str(self.remove_punc(review.lower().encode('utf-8')))
        tokens = [word for word in nltk.word_tokenize(review) if word not in self.stopwords]
        tokens = ' '.join(tokens)
        rev_dict = {'product':{'camera':False,'battery':False,
                               'sound':False, 'display':False,
                               'build':False,'specs':False},
                    'delivery':False,
                    'warranty':False,
                    'seller':False,
                    'price':False}
        
        for category in self.tags:
            if category != 'product':
                count = 0
                countChanged = False
                for tag in eval('self.' + category + '_tag'):
                    nearby_words = []
                    if tag in tokens:
                        #print 'entering tag in token'
                        #print tag
                        rev_dict[category] = True
                        tag_pos = [pos.start() for pos in re.finditer(tag, tokens)]
                        for position in tag_pos:
                            before = tokens[:position].split()
                            after = tokens[position:].split()
                            #print before, after
                            if len(before) > 0:
                                nearby_words.extend([before[-1]])
                                if len(before) > 1:
                                    nearby_words.extend([before[-2]])
                            if len(after) > 1:
                                nearby_words.extend([after[1]])
                                if len(after) > 2:
                                    nearby_words.extend([after[2]])
                    for word in nearby_words:
                        if self.positive[word] == True:
                            count +=1
                            countChanged= True
                        if self.negative[word] == True:
                            count -=1
                            countChanged = True
                #Assigning a sentiment to the specific category            
                if count>0:
                    rev_dict[category] = 'positive'
                elif count<0:
                    rev_dict[category] = 'negative'
                elif count==0 and countChanged==True:
                    rev_dict[category] = 'neutral'
                    
            else:
                for attrs in self.product_tag:
                    count = 0
                    countChanged = False
                    nearby_words = []
                    for tag in self.product_tag[attrs]:
                        if tag in tokens:
                            rev_dict['product'][attrs] = True
                            tag_pos = [pos.start() for pos in re.finditer(tag, tokens)]
                            for position in tag_pos:
                                before = tokens[:position].split()
                                after = tokens[position:].split()
                                if len(before) > 0:
                                    nearby_words.extend([before[-1]])
                                    if len(before) > 1:
                                        nearby_words.extend([before[-2]])
                                if len(after) > 1:
                                    nearby_words.extend([after[1]])
                                    if len(after) > 2:
                                        nearby_words.extend([after[2]])
                    for word in nearby_words:
                        if self.positive[word] == True:
                            count +=1
                            countChanged = True
                        if self.negative[word] == True:
                            count -=1
                            countChanged = True
                            
                    if count>0:
                        rev_dict['product'][attrs] = 'positive'
                    elif count<0:
                        rev_dict['product'][attrs] = 'negative'
                    elif count ==0 and countChanged == True:
                        rev_dict['product'][attrs] = 'neutral'
                        
        return rev_dict    

if __name__=='__main__':
    amazon = Tagger('review.json')
#    amazon.clean_data(True)
#    amazon.filter_bad_reviews()
#    amazon.tag_data()
#    a = amazon.data[0]['reviews'][0][3]
#    amazon.store_mobile_list()
    #print amazon.tagged_data[a]['product']
    
                  
                    
                
                    
            
        
        
        
        
        
        
        
        
        
        
        
        
        