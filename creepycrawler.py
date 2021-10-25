#!/usr/bin/env python3

import sys
import os
import argparse
import requests
import re
from urllib3.exceptions import InsecureRequestWarning

from threading import Thread

class Crawler():
    external_urls: list # Found urls that link to external pages
    __urls: dict # Found urls with status codes, length, evidence and regex that found it
    visited_urls: dict # Urls that have been visited already
    crawling_urls: list # Urls that are currently being crawled
    next_urls: list # Next urls in line to visit
    emails: list # Found email adresses
    ip_v: dict
    host: str # Host as derived from the provided base url
    protocol: str # Protocol as derived from the provided base url

    # Link patterns
    links_patt = [
        '^.*(?P<link>http[s]{0,1}\:\/\/[^\"]+\.[^\"^\<^\>^\']+).*$', #general links
        '^(.*(href|link|action|value|src|srcset)\=\"(?P<link>[^\"^\<^\>]+)\".*)+$', # links in tags
        '.*(?P<link>g.co/[^\^\<^\>"]*)$' # google specific link often embedded in text, not in tags
    ]

    # email patterns
    mail_patt = [
        '[A-z][0-9A-z\-\_\.]+\@[0-9A-z\-\_\.]+[a-z]'
    ]

    # IP addresses and version numbers
    ip_v_patt = [
        '[A-z0-9\-\_]*\d[\d\.]+\.\d+' # Possible IPv4 adresses and version numbers
    ]
    

    def __init__(self, baseurl, depth=1, exclude=None):
        self.external_urls = {}
        self.__urls = {}
        self.visited_urls = {}
        self.crawling_urls = []
        self.next_urls = []
        self.emails = {}
        self.ip_v = {}
        self.depth=depth
        self.exclude=exclude
        
        if not(self.depth):
            self.depth=1000000000
        self.term_width = os.get_terminal_size().columns

        if baseurl.startswith('http://'):
            self.protocol = 'http://'
            self.host = (baseurl.split('http://')[1]).split('/')[0]
        elif baseurl.startswith('https://'):
            self.protocol = 'https://'
            self.host = (baseurl.split('https://')[1]).split('/')[0]
        else:
            self.protocol = ''
            self.host = baseurl.split('/')[0]

        print('PROTOCOL:', self.protocol)
        print('HOST:', self.host)

    def run(self, url, verify=True, nr_threads=4, timeout=2):
        """
        Run creepycrawler on specified url.
        """
        # Set some members
        self.verify=verify
        self.timeout=timeout
        
        # Initial request
        print('Getting baseurl', url)
        resp = self.get(url=url, verify=verify, printerror=True, timeout=self.timeout)
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
                    threads.append(Thread(target=self.__visit_next_urls, args=(crawl_urls,)))
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

    def __visit_next_urls(self, crawl_urls):
        for link in crawl_urls:
            if self.exclude and not(self.exclude in link):
                string = 'Visiting: '+link
                self.term_width = os.get_terminal_size().columns
                print(string+((self.term_width-len(string))*' '), end='\r')
                resp = self.get(url=link, verify=self.verify, timeout=self.timeout)
                if resp:
                    self.__retrieve_links(html=resp, baseurl=link)
                    self.__retrieve_emailaddr(html=resp, baseurl=link)
                    self.__retrieve_ip_v(text=resp, baseurl=link)
            elif not(self.exclude):
                string = 'Visiting: '+link
                self.term_width = os.get_terminal_size().columns
                print(string+((self.term_width-len(string))*' '), end='\r')
                resp = self.get(url=link, verify=self.verify, timeout=self.timeout)
                if resp:
                    self.__retrieve_links(html=resp, baseurl=link)
                    self.__retrieve_emailaddr(html=resp, baseurl=link)
                    self.__retrieve_ip_v(text=resp, baseurl=link)
                

    def get(self, url, verify=True, printerror=False, timeout=2):
        '''
        Try GET request to URL and save the response in visited_urls.
        '''
        try:
            if not(url in self.visited_urls):
                res = requests.get(url, verify=verify, timeout=timeout)
                self.visited_urls[url] = {'html': res.text,
                                          'headers': res.headers,
                                          'status': res.status_code,
                                          'length': len(res.text)}
                if url in self.__urls:
                    self.__urls[url]['status'] = res.status_code
                    self.__urls[url]['length'] = len(res.text)
                    self.__urls[url]['headers'] = res.headers
                    self.__retrieve_ip_v(text=res.headers, baseurl=url+' (headers)')

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

    def get_ip_v(self, as_dict=True):
        if as_dict:
            return self.ip_v
        else:
            ip_v = []
            for url,item in self.ip_v.items():
                if item:
                    ip_v+=item['ip_v']
            return self.__rm_dupl(ip_v)

    def is_internal(self, url):
        """
        """
        return (url.startswith(self.protocol+self.host) or \
                url.startswith(self.protocol+'www.'+self.host))

    def is_subdomain(self, url):
        """
        """
        return (self.host in url) and not(self.is_internal(url))

    def is_external(self, url):
        """
        """
        return not(self.is_internal(url) or self.is_subdomain(url))

    def __retrieve_ip_v(self, text, baseurl):
        """
        Retrieve IP addresses and version numbers based on regular expressions
        """
        if not baseurl in self.ip_v:
            self.ip_v[baseurl] = {}

        if not(type(text) == str):
            contents = []
            for head, cont in text.items():
                for patt in self.ip_v_patt:
                    if re.findall(patt, cont):
                        self.ip_v[baseurl]['ip_v'] = re.findall(patt, cont)
                        self.ip_v[baseurl]['evidence'] = cont
                        self.ip_v[baseurl]['regex'] = patt
        else:
            for patt in self.ip_v_patt:
                if re.findall(patt, text):
                    self.ip_v[baseurl]['ip_v'] = re.findall(patt, text)
                    self.ip_v[baseurl]['evidence'] = text
                    self.ip_v[baseurl]['regex'] = patt

        if 'ip_v' in self.ip_v[baseurl]:
            self.ip_v[baseurl]['ip_v'] = self.__rm_dupl(self.ip_v[baseurl]['ip_v'])

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

        html = [part for part in tmp_html if part]

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
                            elif match['link'].startswith('/'):# or match['link'].startswith('#'):
                                links.append(baseurl+match['link'])
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
                    

        self.external_urls[baseurl] = []
        links = self.__rm_dupl(links)
        for link in links:
            if self.is_internal(link) and not(link in self.visited_urls or link in self.crawling_urls):
                self.next_urls.append(link)
            else: # obsolete
                self.external_urls[baseurl].append(link) # obsolete

        return links
        
    def __rm_dupl(self, l):
        return list(dict.fromkeys(l))

def main():
    BOLD_WHITE = '\033[1m\033[37m'
    FAINT_WHITE = '\033[2m\033[37m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    GREY = '\033[37m'
    RESET = '\033[0m'

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', help='The base URL to start crawling from', required=True)
    parser.add_argument('-d', '--crawl-depth', help='The crawl depth to use, default is 10', type=int)
    parser.add_argument('-o', '--output-file', help='File to write the output into')
    parser.add_argument('-t', '--threads',
                        help='Maximum number of threads to run simultaneously (default is 100)',
                        type=int)
    parser.add_argument('--timeout',
                        help='Timeout for requests, default is 10s',
                        type=int)
    parser.add_argument('-a', '--all', help='Try to find all types of information',
                            action='store_true')
    parser.add_argument('-k', '--insecure', help='Allow insecure connections when using SSL',
                            action='store_true')
    parser.add_argument('-v', '--verbose', help='Verbose output',
                            action='store_true')
    parser.add_argument('--evidence', help='Print evidence',
                            action='store_true')
    parser.add_argument('--no-colours', help='No colours',
                            action='store_true')
    parser.add_argument('--exclude', help='Exclude URLs that include this string')
    
    args = parser.parse_args()

    fd = sys.stdout
    _print=False
    if args.output_file:
        args.no_colours = True
        fd = args.output_file
        _print=True

    if args.no_colours:
        BOLD_WHITE=''
        FAINT_WHITE=''
        RED=''
        GREEN=''
        GREY=''
        RESET=''
    
    if args.insecure:
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

    if args.crawl_depth:
        depth=args.crawl_depth
    else:
        depth=1

    if args.threads:
        if args.threads>100:
            print('[!] ERROR: Too many threads, please enter a number lower than',
                  100, file=sys.stderr)
            sys.exit(1)
        threads=args.threads
    else:
        threads=100

    if args.timeout:
        timeout=args.timeout
    else:
        timeout=2
        
    crawler = Crawler(baseurl=args.url, depth=depth, exclude=args.exclude)
    crawler.run(url=args.url, verify=not(args.insecure), nr_threads=threads, timeout=timeout)

    if _print:
        with open(fd, 'w') as f:
            print('# Crawl report', args.url, file=f)
            print('* (Internal Links)[#internal_links]', file=f)
            print('* (Possible Emails)[#possible_emails]', file=f)
            print('* (Subdomains)[#subdomains]', file=f)
            print('* (External Links)[#external_links]', file=f)
            print('* (IP Addresses and Version Numbers)[#ip_addresses_and_version_numbers]', file=f)
            
            print('\n## INTERNAL LINKS ##\n', file=f)
            print('* (Back to Top)[crawl_report]', file=f)
            urls = crawler.get_int_urls()
            for url,it in urls.items():
                if it['status'] == 200:
                    print(BOLD_WHITE+url+RESET, GREEN+'-->', '['+str(it['status'])+']'+RESET,
                          file=f)
                else:
                    print(FAINT_WHITE+url+RESET, GREY+'-->', '['+str(it['status'])+']'+RESET,
                          file=f)
                if args.verbose or args.evidence:
                    print('\t', GREY+'Evidence:', it['evidence']+RESET,
                          file=f)
                    print('\t', GREY+'Regex:', it['regex']+RESET,
                          file=f)
            
            print('\n## POSSIBLE EMAILS ##\n', file=f)
            print('* (Back to Top)[crawl_report]', file=f)
            if args.verbose or args.evidence:
                mails = crawler.get_emails()
                for baseurl, addrs in mails.items():
                    if addrs:
                        print('\n'.join([addr for addr in addrs]),
                              file=f)
            else:
                mails = crawler.get_emails(as_dict=False)
                print('\n'.join([m for m in mails]), file=f)

            print('\n## SUBDOMAINS ##\n', file=f)
            print('* (Back to Top)[crawl_report]', file=f)
            urls = crawler.get_subdomains()
            for url,it in urls.items():
                if it['status'] == 200:
                    print(BOLD_WHITE+url+RESET, GREEN+'-->', '['+str(it['status'])+']'+RESET,
                          file=f)
                else:
                    print(FAINT_WHITE+url+RESET, GREY+'-->', '['+str(it['status'])+']'+RESET,
                          file=f)
                if args.verbose or args.evidence:
                    print('\t', GREY+'Evidence:', it['evidence']+RESET,
                          file=f)
                    print('\t', GREY+'Regex:', it['regex']+RESET,
                          file=f)
            
            print('\n## EXTERNAL LINKS ##\n', file=f)
            print('* (Back to Top)[crawl_report]', file=f)
            urls = crawler.get_ext_urls()
            for url,it in urls.items():
                if it['status'] == 200:
                    print(BOLD_WHITE+url+RESET, GREEN+'-->', '['+str(it['status'])+']'+RESET,
                          file=f)
                else:
                    print(FAINT_WHITE+url+RESET, GREY+'-->', '['+str(it['status'])+']'+RESET,
                          file=f)
                if args.verbose or args.evidence:
                    print('\t', GREY+'Evidence:', it['evidence']+RESET,
                          file=f)
                    print('\t', GREY+'Regex:', it['regex']+RESET,
                          file=f)

            print('\n## IP ADDRESSES AND VERSION NUMBERS ##\n', file=f)
            print('* (Back to Top)[crawl_report]', file=f)
            if args.verbose or args.evidence:
                urls = crawler.get_ip_v()
                for baseurl, ip_v in urls.items():
                    if ip_v:
                        #print(baseurl)
                        print('\n'.join([item for item in ip_v['ip_v']]),
                              file=f)
                        print('\t', GREY+baseurl+RESET,
                              file=f)
                        print('\t', GREY+ip_v['evidence']+RESET,
                              file=f)
                        print('\t', GREY+ip_v['regex']+RESET,
                              file=f)
            else:
                ip_vs = crawler.get_ip_v(as_dict=False)
                print('\n'.join([i for i in ip_vs]), file=f)

    else:
        print('\nINTERNAL LINKS:\n=====================================')
        urls = crawler.get_int_urls()
        for url,it in urls.items():
            if it['status'] == 200:
                print(BOLD_WHITE+url+RESET, GREEN+'-->', '['+str(it['status'])+']'+RESET)
            else:
                print(FAINT_WHITE+url+RESET, GREY+'-->', '['+str(it['status'])+']'+RESET)
            if args.verbose or args.evidence:
                print('\t', GREY+'Evidence:', it['evidence']+RESET)
                print('\t', GREY+'Regex:', it['regex']+RESET)
            
        print('\nPOSSIBLE EMAILS:\n=====================================')
        if args.verbose or args.evidence:
            mails = crawler.get_emails()
            for baseurl, addrs in mails.items():
                if addrs:
                    print('\n'.join([addr for addr in addrs]))
        else:
            mails = crawler.get_emails(as_dict=False)
            print('\n'.join([m for m in mails]))
            
        print('\nSUBDOMAINS:\n=====================================')
        urls = crawler.get_subdomains()
        for url,it in urls.items():
            if it['status'] == 200:
                print(BOLD_WHITE+url+RESET, GREEN+'-->', '['+str(it['status'])+']'+RESET)
            else:
                print(FAINT_WHITE+url+RESET, GREY+'-->', '['+str(it['status'])+']'+RESET)
            if args.verbose or args.evidence:
                print('\t', GREY+'Evidence:', it['evidence']+RESET)
                print('\t', GREY+'Regex:', it['regex']+RESET)

        print('\nEXTERNAL LINKS:\n=====================================')
        urls = crawler.get_ext_urls()
        for url,it in urls.items():
            if it['status'] == 200:
                print(BOLD_WHITE+url+RESET, GREEN+'-->', '['+str(it['status'])+']'+RESET)
            else:
                print(FAINT_WHITE+url+RESET, GREY+'-->', '['+str(it['status'])+']'+RESET)
            if args.verbose or args.evidence:
                print('\t', GREY+'Evidence:', it['evidence']+RESET)
                print('\t', GREY+'Regex:', it['regex']+RESET)

        print('\nIP ADDRESSES AND VERSION NUMBERS:\n====================')
        if args.verbose or args.evidence:
            urls = crawler.get_ip_v()
            for baseurl, ip_v in urls.items():
                if ip_v:
                    #print(baseurl)
                    print('\n'.join([item for item in ip_v['ip_v']]))
                    print('\t', GREY+baseurl+RESET)
                    print('\t', GREY+ip_v['evidence']+RESET)
                    print('\t', GREY+ip_v['regex']+RESET)
        else:
            ip_vs = crawler.get_ip_v(as_dict=False)
            print('\n'.join([i for i in ip_vs]))


if __name__=='__main__':
    main()
