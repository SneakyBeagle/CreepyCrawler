from src.patterns import *

import sys
import os
import requests
import re
import time
from urllib3.exceptions import InsecureRequestWarning
from threading import Thread

class Crawler():
    __urls: dict # Found urls with status codes, length, evidence and regex that found it
    visited_urls: dict # Urls that have been visited already
    crawling_urls: list # Urls that are currently being crawled
    next_urls: list # Next urls in line to visit
    emails: list # Found email adresses
    ips: dict
    versions: dict
    names: dict
    host: str # Host as derived from the provided base url
    protocol: str # Protocol as derived from the provided base url

    # Link patterns
    links_patt = link_patterns[:]

    # email patterns
    mail_patt = mail_patterns[:]

    # IP addresses and version numbers
    ips_patt = ip_patterns[:]

    # Version patterns
    vers_patt = version_patterns[:]

    # Name patterns
    names_patt = name_patterns[:]

    def __init__(self, *args, baseurl, depth=1, exclude=None, **kwargs):
        """
        Initialise the Crawler by setting members. Also determines the hostname 
        and the used protocol.

        Parameters
        ----------
        baseurl: str
            The url to start crawling from (currently only supports the root web dir).
        dept: int (default = 1)
            The depth to crawl. It is recommended to keep this low, as otherwise it will 
            all take a long long time to complete. Sets to a very high number if 0 is provided,
            essentially crawling until there are no more links to follow.
        exclude: str (default = None)
            If this parameter is provided, the crawler will compare this string to the
            found URLs. If there is a match, that URL will be excluded from further requests.
        """
        self.__parse_kwargs(*args, depth, exclude, **kwargs)
        
        self.term_width = os.get_terminal_size().columns

        self.init_url(url=baseurl)

    def init_url(self, url):
        """
        Initialise the url, set the host, protocol, tld, domain and port

        Parameters
        ----------
        url: str
            The url to use for initialisation
        """
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

        if not self.port:
            if self.protocol=='https://':
                self.port='443'
            else:
                self.port='80'

    def get_host(self):
        """
        Get the host

        Returns
        -------
        self.host: str
            The host in format -> domain.tld
        """
        return self.host

    def get_domain(self):
        """
        Get the domain, without tld

        Returns
        -------
        self.domain: str
            The domain without tld
        """
        return self.domain

    def get_protocol(self):
        """
        Get the protocol (http:// or https://)

        Returns
        -------
        self.protocol: str
            http:// or https://
        """
        return self.protocol

    def run_single(self, url, verify=True, timeout=2, user_agent=None):
        """
        Run the crawler on a single url to analyse it for sensitive information

        Parameters
        ----------
        url: str
        verify: bool
        timeout: int
        user_agent: str
        """
        # Set some members
        self.verify=verify
        self.timeout=timeout

        url=self.prepare_url(url=url)
        
        # Request
        print('Getting url', url)
        resp = self.get(url=url, verify=verify, printerror=True, timeout=self.timeout,
                        user_agent=user_agent)
        if not(resp):
            print('[ERROR], cannot GET baseurl', url, '...')
            print('Exiting')
            sys.exit(1)
        print('Retrieving links')
        self.__retrieve_links(html=resp, baseurl=url)
        print('Retrieving emails')
        self.__retrieve_emailaddr(html=resp, baseurl=url)        
        
    def run(self, url, verify=True, nr_threads=4, timeout=2, user_agent=None):
        """
        Run creepycrawler on specified url.

        Parameters
        ----------
        url: str
        verify: bool
        nr_threads: int
        timeout: int
        user_agent: str
        """
        # Set some members
        self.verify=verify
        self.timeout=timeout

        url=self.prepare_url(url=url)
        
        # Initial request
        print('Getting baseurl', url)
        resp = self.get(url=url, verify=verify, printerror=True, timeout=self.timeout,
                        user_agent=user_agent)
        if not(resp):
            print('[ERROR], cannot GET baseurl', url, '...')
            print('Exiting')
            sys.exit(1)
        print('Retrieving links')
        self.__retrieve_links(html=resp, baseurl=url)
        print('Retrieving emails')
        self.__retrieve_emailaddr(html=resp, baseurl=url)

        threads=[]

        try:
            print('Start of crawling')
            i=1
            while (i<=self.depth):
                i+=1
                self.crawling_urls = self.next_urls[:]
                nr_links = len(self.crawling_urls)
                if nr_threads > nr_links:
                    nr_running = nr_links
                else:
                    nr_running = nr_threads

                try:
                    nr_links_t = nr_links//nr_running # Zero division means no more links
                except Exception as e:
                    print('\nNo more links')
                    return

                nr_links_rem = nr_links-(nr_links_t*nr_running)
                print('\nStarting', nr_running, 'threads for', nr_links, 'links')
                self.next_urls=[]
                for div in range(0, nr_running):
                    start=div*nr_links_t
                    end=(div+1)*nr_links_t
                    if div==(nr_running-1):
                        end=nr_links
                    crawl_urls=self.crawling_urls[start:end]
                    threads.append(Thread(target=self.__visit_next_urls, args=(crawl_urls,
                                                                               user_agent,)))
                    threads[-1].start()

                for thread in threads:
                    thread.join()
                threads=[]
        except KeyboardInterrupt:
            for thread in threads:
                thread.join()
            print('\nStopping')
        except Exception as e:
            for thread in threads:
                thread.join()
            print('Error Crawler.run():', e, file=sys.stderr)
                
        print('\nVisited', len(self.visited_urls))

    def __visit_next_urls(self, crawl_urls, user_agent):
        for link in crawl_urls:
            if self.exclude and not(self.exclude in link):
                string = 'Visiting: '+link
                self.term_width = os.get_terminal_size().columns
                print(string+((self.term_width-len(string))*' '), end='\r')
                resp = self.get(url=link, verify=self.verify, timeout=self.timeout,
                                user_agent=user_agent)
                if resp:
                    self.__retrieve(resp=resp, baseurl=link)
                    #self.__retrieve_links(html=resp, baseurl=link)
                    #self.__retrieve_emailaddr(html=resp, baseurl=link)
                    #self.__retrieve_ips(text=resp, baseurl=link)
                    #self.__retrieve_versions(text=resp, baseurl=link)
            elif not(self.exclude):
                string = 'Visiting: '+link
                self.term_width = os.get_terminal_size().columns
                print(string+((self.term_width-len(string))*' '), end='\r')
                resp = self.get(url=link, verify=self.verify, timeout=self.timeout,
                                user_agent=user_agent)
                if resp:
                    self.__retrieve(resp=resp, baseurl=link)
                    #self.__retrieve_links(html=resp, baseurl=link)
                    #self.__retrieve_emailaddr(html=resp, baseurl=link)
                    #self.__retrieve_ips(text=resp, baseurl=link)
                    #self.__retrieve_versions(text=resp, baseurl=link)
                

    def get(self, url, verify=True, printerror=True, timeout=2, user_agent=None):
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
                        
                self.__retrieve_ips(text=res.headers, baseurl=url+' (headers)')
                self.__retrieve_versions(text=res.headers, baseurl=url+' (headers)')

                return res.text
        except requests.exceptions.Timeout as e:
            if printerror:
                print('[Warning], could not do GET request to', url, '->', e, file=sys.stderr)
        except Exception as e:
            print('[ERROR], could not do GET request to', url, '->', e, file=sys.stderr)
            return None
    

    def get_links(self):
        return self.next_urls

    def get_urls(self):
        #return self.visited_urls
        return self.__urls

    def get_int_urls(self):
        """
        Get internal urls
        """
        int_urls = {}
        for url,items in self.__urls.items():
            if self.is_internal(url=url):#url.startswith(self.protocol+self.host):
                int_urls[url]=items
        return int_urls

    def get_ext_urls(self):
        """
        """
        ext_urls = {}
        for url,items in self.__urls.items():
            if self.is_external(url=url):# not(url.startswith(self.protocol+self.host)):
                ext_urls[url]=items
        return ext_urls

    def get_subdomains(self):
        """
        """
        subdom_url = {}
        for url,items in self.__urls.items():
            if self.is_subdomain(url=url):
                subdom_url[url]=items
        return subdom_url

    def get_emails(self, as_dict=True):
        if as_dict:
            return self.emails
        else:
            mails = []
            for url,item in self.emails.items():
                if item:
                    mails+=item
            return self.__rm_dupl(mails)

    def get_ips(self, as_dict=True):
        if as_dict:
            return self.ips
        else:
            ips = []
            for url,item in self.ips.items():
                if item:
                    ips+=item['ips']
            return self.__rm_dupl(ips)

    def get_versions(self, as_dict=True):
        if as_dict:
            return self.versions
        else:
            versions = []
            for url,item in self.versions.items():
                if item:
                    versions+=item['versions']
            return self.__rm_dupl(versions)

    def is_internal(self, url):
        """
        """
        return (url.startswith(self.protocol+self.host) or \
                url.startswith(self.protocol+'www.'+self.host))

    def is_subdomain(self, url):
        """
        """
        r = ((self.domain+'.'+self.tld) in url) and not(self.is_internal(url))
        return r

    def is_external(self, url):
        """
        """
        return not(self.is_internal(url) or self.is_subdomain(url))

    def __retrieve(self, resp, baseurl):
        """
        """
        self.__retrieve_links(html=resp, baseurl=baseurl)
        self.__retrieve_emailaddr(html=resp, baseurl=baseurl)
        self.__retrieve_ips(text=resp, baseurl=baseurl)
        self.__retrieve_versions(text=resp, baseurl=baseurl)

    def __retrieve_ips(self, text, baseurl):
        """
        Retrieve IP addresses based on regular expressions
        """
        if not baseurl in self.ips:
            self.ips[baseurl] = {}

        self.ips[baseurl]['ips']=[]
        if not(type(text) == str):
            contents = []
            for head, cont in text.items():
                for patt in self.ips_patt:
                    if re.findall(patt, cont):
                        self.ips[baseurl]['ips'] += re.findall(patt, cont)
                        self.ips[baseurl]['evidence'] = cont
                        self.ips[baseurl]['regex'] = patt
        else:
            for patt in self.ips_patt:
                if re.findall(patt, text):
                    self.ips[baseurl]['ips'] += re.findall(patt, text)
                    self.ips[baseurl]['evidence'] = text
                    self.ips[baseurl]['regex'] = patt

        if 'ips' in self.ips[baseurl]:
            self.ips[baseurl]['ips'] = self.__rm_dupl(self.ips[baseurl]['ips'])

    def __retrieve_versions(self, text, baseurl):
        """
        Retrieve version numbers based on regular expressions
        """
        if not baseurl in self.versions:
            self.versions[baseurl] = {}

        self.versions[baseurl]['versions']=[]
        if not(type(text) == str):
            contents = []
            for head, cont in text.items():
                for patt in self.vers_patt:
                    if re.findall(patt, cont):
                        self.versions[baseurl]['versions'] += re.findall(patt, cont)
                        self.versions[baseurl]['evidence'] = cont
                        self.versions[baseurl]['regex'] = patt
        else:
            for patt in self.vers_patt:
                if re.findall(patt, text):
                    self.versions[baseurl]['versions'] += re.findall(patt, text)
                    self.versions[baseurl]['evidence'] = text
                    self.versions[baseurl]['regex'] = patt

        if 'versions' in self.versions[baseurl]:
            self.versions[baseurl]['versions'] = self.__rm_dupl(self.versions[baseurl]['versions'])

    def __retrieve_names(self, text, baseurl):
        """
        Retrieve NAME addresses based on regular expressions
        """
        if not baseurl in self.names:
            self.names[baseurl] = {}

        self.names[baseurl]['names']=[]
        if not(type(text) == str):
            contents = []
            for head, cont in text.items():
                for patt in self.names_patt:
                    if re.findall(patt, cont):
                        self.names[baseurl]['names'] += re.findall(patt, cont)
                        self.names[baseurl]['evidence'] = cont
                        self.names[baseurl]['regex'] = patt
        else:
            for patt in self.names_patt:
                if re.findall(patt, text):
                    self.names[baseurl]['names'] += re.findall(patt, text)
                    self.names[baseurl]['evidence'] = text
                    self.names[baseurl]['regex'] = patt

        if 'names' in self.names[baseurl]:
            self.names[baseurl]['names'] = self.__rm_dupl(self.names[baseurl]['names'])

    def __retrieve_emailaddr(self, html, baseurl):
        """
        Retrieve email addresses from HTML based on regular expressions
        """
        for mail_patt in self.mail_patt:
            self.emails[baseurl] = re.findall(mail_patt, html)

        self.emails[baseurl] = self.__rm_dupl(self.emails[baseurl])

    def __retrieve_links(self, html, baseurl):
        """
        Retrieve links from HTML based on regular expressions.
        """
        html = html.split(' ')
        tmp_html = []
        for i in range(len(html)):
            tmp_html += html[i].split(';')
            tmp_tmp_html = []
            for j in range(len(tmp_html)):
                tmp_tmp_html += tmp_html[j].split('\n')
            

        html = [part for part in tmp_tmp_html if part]

        links=[]
        for line in html:
            if '/' in line or '.' in line:
                for patt in self.links_patt:
                    match = re.search(patt, line)
                    
                    if match:
                        evidence = match.string 
                        span = match.span() 
                        if match['link'].startswith('http://') or match['link'].startswith('https://'):
                            links.append(match['link'])
                        else:
                            if match['link'].startswith('//'):
                                links.append(baseurl.split('//')[0]+match['link'])
                            elif match['link'].startswith('/'):
                                links.append(self.protocol+self.host+match['link'])
                            else:
                                links.append(baseurl+'/'+match['link'])
                        if links and not(links[-1] in self.__urls):
                            self.__urls[links[-1]] = {'evidence':evidence, 'span':span,
                                                      'status':'Not visited',
                                                      'length':'Not visited',
                                                      'regex':patt}
                        elif links:
                            self.__urls[links[-1]]['evidence']=evidence
                            self.__urls[links[-1]]['span']=span
                            self.__urls[links[-1]]['regex']=patt
                            self.__urls[links[-1]]['baseurl']=baseurl
                    

        links = self.__rm_dupl(links)
        for link in links:
            if self.is_internal(link) and not(link in self.visited_urls or link in self.crawling_urls):
                self.next_urls.append(link)

        return links

    def prepare_url(self, url):
        if url.endswith('/'):
           url=url[:-1]
        if not(url.startswith('http://') or url.startswith('https://')):
            url='https://'+url

        return url
    
    def __rm_dupl(self, l):
        return list(dict.fromkeys(l))

    def __parse_kwargs(self, *args, depth=1, exclude=None, **kwargs):
        self.__urls = {}
        self.visited_urls = {}
        self.crawling_urls = []
        self.next_urls = []
        self.emails = {}
        self.ips = {}
        self.versions = {}
        self.depth=depth
        self.exclude=exclude
        if 'timeout' in kwargs:
            self.timeout=kwargs['timeout']
        if 'user_agent' in kwargs:
            self.user_agent=kwargs['user_agent']

        if not(self.depth):
            self.depth=1000000000
