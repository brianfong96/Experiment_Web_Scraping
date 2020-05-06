from algoliasearch.search_client import SearchClient
from bs4 import BeautifulSoup
import datetime
import json
import multiprocessing 
import os
import re
import requests
import time 
import urllib

# Custom Imports
import Path_Manager as pm
import Workbook_Writer as ww

class Expired_Filter():
    def __init__(self):
        # desktop user-agent
        self.USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"

        # mobile user-agent
        self.MOBILE_USER_AGENT = "Mozilla/5.0 (Linux; Android 7.0; SM-G930V Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.125 Mobile Safari/537.36"
        self.headers = {"user-agent" : self.USER_AGENT}   #choose type of user

        # list of tuples (hit object, error message)
        self.hit_err = list(tuple())

        # list of tuples (index, hit object)
        self.i_hits = list(tuple())
        
        self.tmp_file = 'tmp.txt'
        self.init_tmp_file()

        self.pm = pm.Path_Manager()

        self.num_processes = multiprocessing.cpu_count()
        print('# of processes to run: ' + str(self.num_processes))

        print('Starting Timer for Expired Scraper')
        self.last_time = time.time()
        return

    def proc_print(self, msg):
        print(str(os.getpid())+':\t'+str(msg))
        return

    def print_unfiltered_jobs(self):
        for hit in self.i_hits:
            self.proc_print(hit[1])

    def check_full_sentence_in_set(self, string_sentence, set_of_words):
        in_set = True
        split = string_sentence.split(' ')
        for s in split:
            if not s in set_of_words:
                in_set = False
        return in_set

    def convert_to_set(self, soup):
        '''
        Turns a soup object to string
        Makes all letter lowercase
        changes all non alpha-numeric characters to ' ' and splits to list
        cast to set time and return
        '''
        return set(re.sub('[^0-9a-zA-Z]+', ' ', str(soup)).lower().split(' '))        

    def init_tmp_file(self):
        with open(self.tmp_file, 'w') as f:
            f.write('')
        return      

    def fill_hits(self, criteria_function = None):
        key_file = self.pm.get_path_to(os.path.join('keys','expired_filter.keys.json'))
        key_data = json.load(open(key_file))
        client = SearchClient.create(key_data['field'], key_data['key'])
        index = client.init_index(key_data['index'])

        i = 0
        self.i_hits = list()        
        self.proc_print("Going through hits...")        
        for hit in index.browse_objects({'query': ''}):
            if criteria_function:
                if criteria_function(hit):
                    self.i_hits.append((i, hit))
                    i += 1

        self.proc_print("Took "  + str(time.time()-self.last_time) + " seconds to iterate through index parse objects")
        self.last_time = time.time()
        self.proc_print("There were " + str(len(self.i_hits)) + " hits")
        return 

    def expire_check(self, hit):
        return hit['isExternal'] == True and hit['deletedAt'] == None and hit['expiresAt'][:-14] > str(datetime.date.today())

    def get_live_jobs(self):
        self.fill_hits(self.expire_check)
        return

    def filter_job(self, hit_tuple):

        return

if __name__ == "__main__":
    ef = Expired_Filter()
    ef.get_live_jobs()
    
    pass