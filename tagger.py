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

class Tagger(object):
    def __init__(self, filename):
        self.data = []
        with open('data/' + filename) as f:
            for line in f:
                self.data.append(json.loads(line))
        self.stopwords = stopwords.words('english')
        self.product_tag = {'camera':['megapixel', 'ppi', 'front', 'rear', 'resolution' ],
                            'battery': ['charging','charge','charger', 'longlasting', 'backup', 'internal'],
                            'sound': ['music', 'loud', 'voice', 'volume'],
                            'display': ['touch','screen', 'bright', 'large', 'touchscreen', 'clear'],
                            'specs': ['memory','heat', 'ram','bluetooth','android','performance','app', 'cdma', 'repair', 'software'],
                            'looks': ['look','color', 'weight','heavy','light', 'lightweight','metal','matte','plastic', 'solid', 'build', 'button']
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
                phone['reviews'][i][3] = tokens
                
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
                    if word in review[3] or word in review[1]:
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
                rating = content[0]
                title = content[1]
                author = content[2]
                review = content[3]
                list_words = nltk.word_tokenize(review)
                list_stem_words = [ ls.stem(word) for word in list_words]
                phone_reviews.extend(list_stem_words)
            list_review_word.extend(phone_reviews)
        self.noise_count = Counter(list_review_word)
        
    def tag_data(self):
        for phone in self.data:
            self.tagged_data[phone['title']] = {'product':{'camera':set(),'battery':set(), 
                                                            'sound':set(), 'display':set(),
                                                            'looks':set(),'specs':set()},
                                                 'delivery':set(),'warranty':set(),
                                                'seller':set(), 'price':set()}
            for i, review in enumerate(phone['reviews']):
                for tag in self.delivery_tag:
                    if tag in review[3] or tag in review[1]:
                        self.tagged_data[phone['title']]['delivery'].add(tuple(review))
                        
                for tag in self.seller_tag:
                    if tag in review[3] or tag in review[1]:
                        self.tagged_data[phone['title']]['seller'].add(tuple(review))
                        
                for tag in self.warranty_tag:
                    if tag in review[3] or tag in review[1]:
                        self.tagged_data[phone['title']]['warranty'].add(tuple(review))
                        
                for tag in self.price_tag:
                    if tag in review[3] or tag in review[1]:
                        self.tagged_data[phone['title']]['price'].add(tuple(review))
                        
                for tag in self.product_tag:
                    for attr in self.product_tag[tag]:
                        if attr in review[3] or attr in review[1]:
                            self.tagged_data[phone['title']]['product'][tag].add(tuple(review))
                        
if __name__=='__main__':
    amazon = Tagger('review.json')
    amazon.clean_data(True)
    amazon.filter_bad_reviews()
    amazon.tag_data()
    a = amazon.data[51]['title']
    print amazon.tagged_data[a]['product']
                  
                    
                
                    
            
        
        
        
        
        
        
        
        
        
        
        
        
        