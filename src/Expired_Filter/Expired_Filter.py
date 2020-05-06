from algoliasearch.search_client import SearchClient
from bs4 import BeautifulSoup
import datetime
import multiprocessing 
import os
import re
import requests
import time 
import urllib


class Expired_scraper():
    def __init__(self):
        # desktop user-agent
        self.USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"

        # mobile user-agent
        self.MOBILE_USER_AGENT = "Mozilla/5.0 (Linux; Android 7.0; SM-G930V Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.125 Mobile Safari/537.36"
        self.headers = {"user-agent" : self.USER_AGENT}   #choose type of user
        # list of tuples (hit object, error message)
        self.hit_err = list()
        # list of tuples (index, hit object)
        self.i_hits = list()
        self.start_time = time.time()
        self.tmp_file = 'tmp.txt'

    def proc_print(self, msg):
        print(str(os.getpid())+':\t'+msg)

    def check_full_sentence_in_set(self, string_sentence, set_of_words):
        in_set = True
        split = string_sentence.split(' ')
        for s in split:
            if not s in set_of_words:
                in_set = False
        return in_set

    if __name__ == "__main__":
        pass