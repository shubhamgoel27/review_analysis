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

class Tagger(object):
    def __init__(self, filename):
        self.data = []
        with open('data/' + filename) as f:
            for line in f:
                self.data.append(json.loads(line))
        self.stopwords = stopwords.words('english')
        self.product_tag = {'camera':['megapixel', 'ppi', 'front', 'rear', ],
                            'battery': ['charge', 'longlasting', 'backup'],
                            'sound': ['music', 'loud'],
                            'display': ['bright', 'large', 'touchscreen', 'clear'],
                            'specs': ['heat', 'ram','bluetooth',],
                            'looks': ['color', 'weight','heavy','light', 'lightweight','metal','matte','plastic', 'solid', 'build']
}
        self.price_tag = ['price','expensive','cheap']
        self.delivery_tag = ['fast','quick', 'on time', 'service']
        self.warranty_tag = ['warranty']
        self.seller_tag = ['seller', 'vendor']
        
        self.tags = {'product': self.product_tag, 'price': self.price_tag,
                     'seller': self.seller_tag, 'warranty': self.warranty_tag,
                     'delivery': self.seller_tag}
        
    def compute_avg_rating(self):
        '''Stores the average rating value in data'''
        for phone in self.data:
            avg = sum(float(review[0]) for review in phone['reviews'])
            if len(phone['reviews'])!=0:
                avg = avg/len(phone['reviews'])
            phone['avg_rating'] = float(avg)
        
    def remove_punc(self, text):
        '''returns the text without any punctuations'''
        return ''.join([t for t in text if t not in string.punctuation and t not in '0123456789'])
        
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
            
                
if __name__ =='__main__' :
    amazon = Tagger("review.json")
    amazon.clean_data(joint=True)
            
        
        
        
        
        
        
        
        
        
        
        
        
        