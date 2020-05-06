from algoliasearch.search_client import SearchClient
import argparse
from bs4 import BeautifulSoup
import datetime
import multiprocessing 
import os
import re
import requests
import time 
import urllib
import yaml

# Custom Imports
import Path_Manager as pm
import Workbook_Writer as ww

class Expired_Filter():
    def __init__(self, num_processes = 0):
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
        self.disable_print = False        
        self.num_processes = multiprocessing.cpu_count()
        if num_processes != 0:
            self.num_processes = num_processes
        self.proc_print('# of processes to run: ' + str(self.num_processes))

        self.proc_print('Starting Timer for Expired Scraper')
        self.last_time = time.time()
        return

    def proc_print(self, msg):
        if not self.disable_print:
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
                return False
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
        with open(key_file) as file:
            key_data = yaml.load(file, Loader=yaml.BaseLoader)
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
        hit = hit_tuple[1]
        err = self.parse_job(hit)
        if err:
            with open(self.tmp_file, 'a') as f:
                f.write(str(hit_tuple[0])+'\t'+err+'\n')
        return

    def parse_job(self, hit):
        last_time = time.time()
        url = hit['externalURL']
        title = hit['title']        
        try: 
            resp = requests.get(url, headers=self.headers)
        except requests.exceptions.SSLError:
            self.proc_print("This URL failed: " + url)
            pass    
        else:        
            if resp.status_code == 200:
                content = BeautifulSoup(resp.content, "html.parser")            
                words_set = self.convert_to_set(content)                
                if "indeed.com" in str(url):
                    indeed_checks = ["this job has expired"]
                    indeed_search = ["This job has expired"]                

                    for i in range(len(indeed_checks)):                        
                        if self.check_full_sentence_in_set(indeed_checks[i], words_set):
                            results = content.find_all(string=re.compile('.*{0}.*'.format(indeed_search[i])), recursive=True)
                            if results:
                                return indeed_search[i]                    
                    self.proc_print('Indeed.com Parsing: Took ' + str(time.time()-last_time)+' seconds')

                elif content.body:
                    body_checks = ["this job filled", "the job you are looking for is no longer open", "this job posting has expired"]
                    pass_check = False
                    for check in body_checks:
                        if self.check_full_sentence_in_set(check, words_set):
                            pass_check = True
                    if not pass_check:
                        self.proc_print("Stopped early because failed all checks. Took " + str(time.time()-last_time) + " seconds")
                        return None
                    title = title
                    results = content.find_all(string=re.compile('.*{0}.*'.format(re.escape(title))), recursive=True)
                    if results:                        
                        body_search = ["This job has been filled", "The job you are looking for is no longer open", "This job posting has expired"]
                        
                        for i in range(len(body_checks)):
                            if self.check_full_sentence_in_set(body_checks[i], words_set):
                                results = content.find_all(string=re.compile('.*{0}.*'.format(body_search[i])), recursive=True)
                                if results:
                                    return body_search[i]                    
                        self.proc_print('Content Body Parsing: Took ' + str(time.time()-last_time)+' seconds')                    
                    else:
                        return "no title found"                        
                else:
                    return "no content.body found"
            else:
                return str("Status Code: " + str(resp.status_code))

        self.proc_print('Finished Function: stopped after ' + str(time.time()-last_time)+' seconds')
        return None

    def multiprocess_filter(self):
        if not self.i_hits:
            self.proc_print('There are no hits to filter. Please run Get Live Jobs first')
            return

        self.last_time = time.time()        
        self.proc_print("Using " + str(self.num_processes) + " processes")
        p = multiprocessing.Pool(self.num_processes)
        p.map(self.filter_job, self.i_hits)
        
        time_took = time.time()-self.last_time
        self.proc_print("Took "  + str(time_took) + " seconds to concurrent job search")
        return

    def write_to_ww(self):
        self.last_time = time.time()
        self.hit_err = list()        
        self.column_names = ['URL', 'Title', 'Company', 'Date Posted', 'Result']
        self.ww = ww.Workbook_Writer('ExpiredJobs.xlsx', self.column_names)

        row_values = list()
        with open(self.tmp_file, 'r') as f:
            for line in f:
                if line != '\n':
                    line = line.split('\t')
                    i = int(line[0])
                    hit = self.i_hits[i][1]
                    err = line[1]
                    row_values.append([hit['externalURL'], hit['title'], hit['companyName'], hit['createdAt'][:-14], err])
        self.ww.Write(row_values)
        self.ww.End()
        self.proc_print("Writing to Excell took " + str(time.time()-self.last_time) +" seconds")
        return

    def full_run(self):
        self.get_live_jobs()
        self.multiprocess_filter()
        self.write_to_ww()
        return

if __name__ == "__main__":   
    parser = argparse.ArgumentParser(description="Just a job scraping script")
    parser.add_argument('-np', "--num_processes", type=int, default=0 , help="number of processes to use") 
    args = parser.parse_args()

    ef = Expired_Filter(num_processes=args.num_processes)
    ef.full_run()
    pass