from os import listdir
import codecs
from bs4 import BeautifulSoup
import re
import pandas as pd
from tqdm import tqdm

import numpy as np
from langdetect import detect, LangDetectException

import os
import sys
#adding directory to path
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)

sys.path.append(parentdir+"/utils/")
from path import path_data, path_data_html

sys.path.append(parentdir+"/download/")
from data_reader import data_reader


class website_text_dataset:
    """
    (in construction)
    class to create analysis of html page
    """

    def __init__(self, path):
        self.website_info = data_reader.read_text_dataset()
    

    def prep(self, website_info: pd.DataFrame):

        print("Detecting language. This step takes a few minutes.")
        self.website_info['lang'] = self.website_info.text.apply(website_text_dataset.detect_lang)
        print("Done.")


        print("Identifying invalid website.")
        self.website_info = website_text_dataset.add_is_valid_text(self.website_info)

        print("Identify duplicated website")
        self.website_info['is_duplicated'] = self.website_info.duplicated(subset=['website'])
        print('Done.')

        return self.website_info

    ## Detection language ##
    def detect_lang(text: str):
        try:
            lang = detect(text)
            return lang
        except LangDetectException:
            return "exception"

    ## Detection invalid website => Dataframe ##
    def add_is_valid_text(self, website_info: pd.DataFrame):

        website_info['is_valid_website'] = True
        domain_word_pos = website_info.text.str.lower().str.find('domain')
        bad_domain = np.all([domain_word_pos >= 0 , domain_word_pos < 100], axis=0)

        invalid_conditions = [
            bad_domain,
            website_info.text.str.contains('Internal Server'),
            website_info.text.str.contains('BuyDomains.com'),
            website_info.text.str.contains('This Web page is parked for FREE'),
            website_info.text.str.contains(
                'Free business profile for provided by Network Solutions'),
            website_info.text.str.contains(
                'The Sponsored Listings displayed above are served automatically'),
            website_info.text.str.contains('Apache'),
            website_info.text.str.contains('website is for sale'),
            website_info.text.str.contains('This Web site coming soon'),
            website_info.text.str.contains(
                'Welcome to the new website! Our site has been recently created'),
            website_info.text.str.match('^Wayback Machine'),
            website_info.text.str.match(
                'Wayback Machine See what s new with book lending'),
            website_info.text.str.match('^AVAILABLE NOT FOUND'),
            website_info.text.str.match('^DefaultHomePage'),
            website_info.text.str.match(
                '^I?n?t?ernet Archive: Scheduled Mantenance'),
            website_info.text.str.match('^The page cannot be found'),
            website_info.text.str.match('^503'),
            website_info.text.str.match('^5?0?3 Service Unavailable'),
            website_info.text.str.lower().str.match('domain down'),
            website_info.text.str.match('^Too Many Requests'),
            website_info.text.str.match('^Your browser does not support'),
            website_info.text.str.match('^New Server for COMPANYNAME'),
            website_info.text.str.contains('this page is parked FREE'),
            website_info.text.str.contains('domain name was recently registered'),
            website_info.text.str.contains('placeholder for domain'),
            website_info.text.str.contains('xtremedata.com  : Low cost'),
            website_info.text.str.lower().str.contains('domain name registration'),
            website_info.text.str.contains('Under Construction'),
            website_info.text.str.contains('This Web site is currently under'),
            website_info.text.str.contains('This domain name was recently'),
            website_info.text.str.contains('This page is parked free'),
            website_info.text.str.match('^Microsoft VBScript runtime error'),
            website_info.text.str.match('^WebFusion'),
            website_info.text.str.match('^Register domain names'),
            website_info.text.str.match('^Moved This page has moved'),
            website_info.text.str.match('^Coming Soon'),
            website_info.text.str.contains('Site (is )?Temporarily Unavailable'),
            website_info.text.str.match('^Under Construction'),
            website_info.text.str.match('^cPanel'),
            website_info.text.str.match('^Authorization Required'),
            website_info.text.str.match(
                '^Top Web Search Directory Top Web Searches'),
            website_info.text.str.match('^Web Searches'),
            website_info.text.str.match('^Web Hosting'),
            website_info.text.str.match(
                '^Search Directory Page Sponsored Listing'),
            website_info.text.str.match('^coming soon'),
            website_info.text.str.match(
                'This site is the default web server site'),
            website_info.text.str.match('DF-1.4 %���� 0 obj< '),
            website_info.text.str.match('This page uses frames, but your brow'),
            website_info.text.str.match('U N D E R C O N S T R U C T I O N'),
            website_info.text.str.match(
                'We recommend you upgrade your browser to one of below free alternatives'
            ),
            website_info.text.str.match('enable JavaScript'),
            website_info.text.str.lower().str.match('under construction'),
            website_info.text.str.match(
                'Page cannot be Please contact your service provider for more'),
            website_info.text.str.match('^A WordPress Site'),
            website_info.text.str.match('^Related Searches: Related Searches'),
            website_info.text.str.match('^Welcome to IIS'),

            ### Language
            website_info.lang != 'en'
        ]

        #Some conditions by range of value in "find" method
        a= website_info.text.str.find("Go Daddy")
        invalid_conditions.append(np.logical_and(a>= 0 , a<200))
            
        a =  website_info.text.str.find("Wayback Machine")
        invalid_conditions.append(np.logical_and(a>= 0 , a<200))
            
        a =  website_info.text.str.find('This website is for sale')
        invalid_conditions.append(np.logical_and(a>= 0 , a<50))
            
        a =  website_info.text.str.find('Adobe Flash Player Download')
        invalid_conditions.append(np.logical_and(a>= 0 , a<30))

        website_info.at[np.any(invalid_conditions, axis=0), 'is_valid_website'] = False

        return website_info

    def get_valid_index(website_info: pd.DataFrame):
        valid_index = np.all([
            website_info.is_valid_website == True,
            website_info.is_duplicated == False
        ],axis=0)

        return valid_index