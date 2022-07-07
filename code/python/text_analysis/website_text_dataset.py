from asyncio.base_subprocess import WriteSubprocessPipeProto
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

    def __init__(self):
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
        except TypeError:
            return "exception"

    ## Detection invalid website => Dataframe ##
    def add_is_valid_text(self, website_info: pd.DataFrame):

        website_info['is_valid_website'] = True
        domain_word_pos = website_info.text.str.lower().str.find('domain')
        bad_domain = np.all([domain_word_pos >= 0 , domain_word_pos < 100], axis=0)

        invalid_conditions = [
            bad_domain,
            website_info.text.str.contains('Internal Server', na=False),
            website_info.text.str.contains('BuyDomains.com', na=False),
            website_info.text.str.contains('This Web page is parked for FREE', na=False),
            website_info.text.str.contains(
                'Free business profile for provided by Network Solutions', na=False),
            website_info.text.str.contains(
                'The Sponsored Listings displayed above are served automatically', na=False),
            website_info.text.str.contains('Apache', na=False),
            website_info.text.str.contains('website is for sale', na=False),
            website_info.text.str.contains('This Web site coming soon', na=False),
            website_info.text.str.contains(
                'Welcome to the new website! Our site has been recently created', na=False),
            website_info.text.str.match('^Wayback Machine', na=False),
            website_info.text.str.match(
                'Wayback Machine See what s new with book lending', na=False),
            website_info.text.str.match('^AVAILABLE NOT FOUND', na=False),
            website_info.text.str.match('^DefaultHomePage', na=False),
            website_info.text.str.match(
                '^I?n?t?ernet Archive: Scheduled Mantenance', na=False),
            website_info.text.str.match('^The page cannot be found', na=False),
            website_info.text.str.match('^503', na=False),
            website_info.text.str.match('^5?0?3 Service Unavailable', na=False),
            website_info.text.str.lower().str.match('domain down', na=False),
            website_info.text.str.match('^Too Many Requests', na=False),
            website_info.text.str.match('^Your browser does not support', na=False),
            website_info.text.str.match('^New Server for COMPANYNAME', na=False),
            website_info.text.str.contains('this page is parked FREE', na=False),
            website_info.text.str.contains('domain name was recently registered', na=False),
            website_info.text.str.contains('placeholder for domain', na=False),
            website_info.text.str.contains('xtremedata.com  : Low cost', na=False),
            website_info.text.str.lower().str.contains('domain name registration', na=False),
            website_info.text.str.contains('Under Construction', na=False),
            website_info.text.str.contains('This Web site is currently under', na=False),
            website_info.text.str.contains('This domain name was recently', na=False),
            website_info.text.str.contains('This page is parked free', na=False),
            website_info.text.str.contains('turn JavaScript', na=False),
            website_info.text.str.match('^Microsoft VBScript runtime error', na=False),
            website_info.text.str.match('^WebFusion', na=False),
            website_info.text.str.match('^Register domain names', na=False),
            website_info.text.str.match('^Moved This page has moved', na=False),
            website_info.text.str.match('^Coming Soon', na=False),
            website_info.text.str.match('Site (is )?Temporarily Unavailable', na=False),
            website_info.text.str.match('^Under Construction', na=False),
            website_info.text.str.match('^cPanel', na=False),
            website_info.text.str.match('^Authorization Required', na=False),
            website_info.text.str.match(
                '^Top Web Search Directory Top Web Searches', na=False),
            website_info.text.str.match('^Web Searches', na=False),
            website_info.text.str.match('^Web Hosting', na=False),
            website_info.text.str.match(
                '^Search Directory Page Sponsored Listing', na=False),
            website_info.text.str.match('^coming soon', na=False),
            website_info.text.str.match(
                'This site is the default web server site', na=False),
            website_info.text.str.match('DF-1.4 %���� 0 obj< ', na=False),
            website_info.text.str.match('This page uses frames, but your brow', na=False),
            website_info.text.str.match('U N D E R C O N S T R U C T I O N', na=False),
            website_info.text.str.match(
                'We recommend you upgrade your browser to one of below free alternatives', na=False
            ),
            website_info.text.str.match('enable JavaScript', na=False),
            website_info.text.str.lower().str.match('under construction', na=False),
            website_info.text.str.match(
                'Page cannot be Please contact your service provider for more', na=False),
            website_info.text.str.match('^A WordPress Site', na=False),
            website_info.text.str.match('^Related Searches: Related Searches', na=False),
            website_info.text.str.match('^Welcome to IIS', na=False),

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

    def prep(self, website_info: pd.DataFrame):
        # it takes few minutes to detect language
        print("Detecting language.")
        website_info['lang'] = website_info.text.apply(website_text_dataset.detect_lang)
        print("Done.")

        print("Identify invalid website.")
        website_info = self.add_is_valid_text(website_info)
        print("Done")

        print("Identify duplicate websites")
        website_info['is_duplicated'] = website_info.duplicated()
        print("Done")
        return website_info

    def get_valid_index(website_info: pd.DataFrame):
        valid_index = np.all([
            website_info.is_valid_website == True,
            website_info.is_duplicated == False
        ],axis=0)

        return valid_index

    def save_file(self):
        self.website_info.to_csv(f'{path_data}/website_info_cleaned.csv')

if __name__ == "__main__":
    website_text = website_text_dataset()
    df = website_text.prep(website_text.website_info[:])
    idx = website_text_dataset.get_valid_index(df)
    website_text_cleaned = df.loc[idx]
    website_text_cleaned.to_csv(f'{path_data}/website_info_cleaned.csv')
