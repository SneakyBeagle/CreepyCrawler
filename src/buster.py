from src.colours import clr

import sys
import os
import requests
import time
from urllib3.exceptions import InsecureRequestWarning
from threading import Thread

class Buster():
    __urls: dict # Found urls with status codes

    def __init__(self, *args, baseurl, depth=1, exclude=None, **kwargs):
        """
        """
        self.__parse_kwargs(*args, depth, exclude, **kwargs)

        self.init_url(url=baseurl)

        self.term_width = os.get_terminal_size().columns

        self.read_wordlist()

    def init_url(self, url):
        if url.startswith('http://'):
            self.protocol = 'http://'
            self.host = (url.split('http://')[1]).split('/')[0]
        elif url.startswith('https://'):
            self.protocol = 'https://'
            self.host = (url.split('https://')[1]).split('/')[0]
        else:
            self.protocol = 'https://'
            self.host = url.split('/')[0]
        self.tld = self.host.split('.')[-1]
        self.domain = self.host.split('.')[-2]
        self.port = url.split(':')[-1]

    def run(self, url, verify=True, nr_threads=4, timeout=2,
            user_agent=None, bad_code='404'):

        url = self.prepare_url(url)
        self.term_width = os.get_terminal_size().columns
        try:
            lists = self.__divide_list(wordlist=self.wordlist, nr=nr_threads)
            threads=[]
            print('starting', len(lists), 'threads')
            for l in lists:
                threads.append(Thread(target=self.run_thread, args=(url, l, verify,
                                                                    timeout, user_agent,
                                                                    bad_code,)))
                threads[-1].start()
            sys.exit(0)
        except KeyboardInterrupt:
            print('')
            print('Stopping')
        for i,t in enumerate(threads):
            print('Joining thread', i)
            t.join()

        self.term_width = os.get_terminal_size().columns
        print(' '*self.term_width)

    def run_thread(self, url, wordlist, verify=True, timeout=2, user_agent=None, bad_code='404'):
        #print('thread started')
        for index, word in enumerate(wordlist):
            t = self.join(url, word)
            string='Visiting'+' ['+str(self.vis_nr+1)+'/'+str(len(self.wordlist))+']: '+str(t)
            fill = (self.term_width-len(string))*' '
            print(string+fill, end='\r')
            self.get(url=t, verify=verify, timeout=timeout,
                     user_agent=user_agent, bad_code=bad_code)

    def get(self, url, verify=True, printerror=False, timeout=2, user_agent=None, bad_code='404'):
        '''
        Try GET request to URL and save the response in visited_urls.
        '''
        headers=requests.utils.default_headers()
        if user_agent:
            headers.update({'User-Agent': user_agent})
        try:
            if not(url in self.visited_urls):
                st=time.time()
                res = requests.get(url, verify=verify, timeout=timeout, headers=headers)
                end="%.4f"%(time.time()-st)
                if not(str(res.status_code)==bad_code):
                    if str(res.status_code)=='200':
                        string=str(url)+' --> '+clr.GREEN+str(res.status_code)+clr.RESET+' ['+str(end)+'s]'
                    else:
                        string=str(url)+' --> '+clr.YELLOW+str(res.status_code)+clr.RESET+' ['+str(end)+'s]'
                    fill = (self.term_width-len(string))*' '
                    print(string+fill)
                self.visited_urls[url] = {'html': res.text,
                                          'headers': res.headers,
                                          'status': res.status_code,
                                          'length': len(res.text),
                                          'time': end}
                if url in self.__urls:
                    if str(self.__urls[url]['status']) != '200':
                        self.__urls[url]['status'] = res.status_code
                        self.__urls[url]['length'] = len(res.text)
                        self.__urls[url]['headers'] = res.headers

                self.vis_nr+=1
                return res.text
        except requests.exceptions.Timeout as e:
            self.vis_nr+=1
            if printerror:
                print('[Warning], could not do GET request to', url, '->', e, file=sys.stderr)
        except Exception as e:
            self.vis_nr+=1
            print('[ERROR], could not do GET request to', url, '->', e, file=sys.stderr)
            return None

    def join(self, *args, **kwargs):
        res=''
        res = '/'.join([str(a) for a in args])
        return self.prepare_url(res)

    def read_wordlist(self):
        self.wordlist=[]
        if not(os.path.exists(self.wordlist_file)):
            raise ValueError("Wordlist does not exist or is not readable.")
        with open(self.wordlist_file, 'r') as fd:
            lines = fd.readlines()
            for line in lines:
                self.wordlist.append(line.split('\n')[0])

    def prepare_url(self, url):
        if url.endswith('/'):
           url=url[:-1]
        if not(url.startswith('http://') or url.startswith('https://')):
            url='https://'+url

        return url

    def __divide_list(self, wordlist, nr):
        if nr > len(wordlist):
            return [wordlist]
        nr_words = len(wordlist)//nr
        #print(len(wordlist), nr_words, nr, nr*nr_words)
        div = []
        for i in range(nr):
            start=i*nr_words
            end=(i+1)*nr_words
            if i == (nr-1):
                end=len(wordlist)
            div.append(wordlist[start:end])
        return div
            
    def __parse_kwargs(self, *args, depth=1, exclude=None, **kwargs):
        self.__urls = {}
        self.visited_urls = {}
        self.vis_nr=0
        self.url_nr=0
        self.emails = {}
        self.ip_v = {}
        self.depth=depth
        self.exclude=exclude
        if 'timeout' in kwargs:
            self.timeout=kwargs['timeout']
        if 'user_agent' in kwargs:
            self.user_agent=kwargs['user_agent']
        if 'wordlist' in kwargs:
            self.wordlist_file=kwargs['wordlist']
        else:
            self.wordlist_file='/usr/share/creepycrawler/common.txt'

        if not(self.depth):
            self.depth=1000000000
            
