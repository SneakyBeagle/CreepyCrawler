#!/usr/bin/env python3

import sys
import argparse
import requests
import re
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning

class Crawler():
    external_urls: list
    visited_urls: dict
    crawling_urls: list
    next_urls: list
    mail_patt = '[A-z][0-9A-z\-\_\.]+\@[0-9A-z\-\_\.]+[a-z]'
    emails: list

    # Links that often do not end up inside html tags, but can still be interesting
    links_patt = [
        '^(.*(href|link|action|value|src|srcset)\=\"(?P<link>[^\"]+)\".*)+$', # links in tags
        '.*(?P<link>g.co/[^\"]*$' # google specific link often embedded in text, not in tags
    ]

    def __init__(self, baseurl, depth=10):
        self.external_urls = {}
        self.visited_urls = {}
        self.visited_status = []
        self.crawling_urls = []
        self.next_urls = []
        self.emails = {}
        self.depth=depth

    def run(self, url, verify=True):
        # Initial request
        print('Getting baseurl', url)
        resp = self.get(url=url, verify=verify)
        if not(resp):
            print('[ERROR], cannot GET baseurl', url, '...')
            print('Exiting')
            sys.exit(1)
        print('Retrieving links')
        self.__retrieve_links_re(html=resp, baseurl=url)
        self.__retrieve_links(html=resp, baseurl=url)
        print('Retrieving emails')
        self.__retrieve_emailaddr(html=resp, baseurl=url)

        try:
            print('Start of crawling')
            # Crawling
            i=0
            while (i<=self.depth):
                i+=1
                print('Crawling depth:', i)
                self.crawling_urls = self.next_urls[:]
                self.next_urls=[]
                for link in self.crawling_urls:
                    resp = self.get(url=link, verify=verify)
                    if resp:
                        print('Visited', len(self.visited_urls), 'links', end='\r')
                        self.__retrieve_links(html=resp, baseurl=link)
                        self.__retrieve_emailaddr(html=resp, baseurl=link)
        except KeyboardInterrupt:
            print('\nStopping')
        except Exception as e:
            print('Error:', e, file=sys.stderr)
                
        print('Visited', len(self.visited_urls))
            

    def get(self, url, verify=True):
        '''
        Try GET request to URL and save the response in visited_urls.
        '''
        try:
            if not(url in self.visited_urls):
                res = requests.get(url, verify=verify)
                self.visited_urls[url] = {'html': res.text,
                                          'headers': res.headers,
                                          'status': res.status_code,
                                          'length': len(res.text)}
                self.visited_status.append(res.status_code)

                return res.text
        except Exception as e:
            print('[ERROR], could not do GET request to', url, '->', e)
            return None
    

    def get_links(self):
        return self.next_urls
    
    def get_urls(self):
        return self.visited_urls

    def get_ext_urls(self):
        return self.external_urls

    def get_emails(self):
        return self.emails

    def __retrieve_emailaddr(self, html, baseurl):
        self.emails[baseurl] = re.findall(self.mail_patt, html)

        self.emails[baseurl] = self.__rm_dupl(self.emails[baseurl])

    def __retrieve_links_re(self, html, baseurl):
        search_patt='^(.*(href|link|action|value|src|srcset)\=\"(?P<link>[^\"]+)\".*)+$'
        html = html.split(' ')

        links=[]
        for line in html:
            if '/' in line or '.' in line:
                match = re.search(search_patt, line)
                if match:
                    if match['link'].startswith('http://') or match['link'].startswith('https://'):
                        links.append(match['link'])
                    else:
                        if match['link'].startswith('//'):
                            links.append(baseurl.split('//')[0]+match['link'])
                        elif match['link'].startswith('/'):# or match['link'].startswith('#'):
                            links.append(baseurl+match['link'])
                        else:
                            links.append(baseurl+'/'+match['link'])
                    

        self.external_urls[baseurl] = []
        links = self.__rm_dupl(links)
        if link.startswith(baseurl) and not(link in self.visited_urls or link in self.crawling_urls):
            self.next_urls.append(link)
        else:
            self.external_urls[baseurl].append(link)
            
        sys.exit(0)
        return links
        
    def __retrieve_links(self, html, baseurl):
        soup = BeautifulSoup(html, 'html.parser')

        re_res=re.findall('https\:\/\/[A-z0-9\.\:\-\_\=\+\?\~\/\&\;]+', html)
        links = []
        soup_res = soup.find_all('a')+soup.find_all('link')
        print('\n', '\n'.join(re_res), '\n')
        for link in soup_res:
            path = link.get('href')
            print(path)
            if path:
                if path.startswith('/'):
                    path = baseurl.split(':')[0]+path
                elif path.startswith('#'):
                    path = baseurl+'/'+path
                elif path.startswith('/'):
                    path = baseurl+path

                links.append(path)


        self.external_urls[baseurl] = []
        for link in links:
            if link.startswith(baseurl) and not(link in self.visited_urls or link in self.crawling_urls):
                self.next_urls.append(link)
            else:
                self.external_urls[baseurl].append(link)

        self.next_urls = self.__rm_dupl(self.next_urls)
        self.external_urls[baseurl] = self.__rm_dupl(self.external_urls[baseurl])

    def __rm_dupl(self, l):
        return list(dict.fromkeys(l))

# TODO support for custom headers, cookies, read request from file, other request methods
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', help='The base URL to start crawling from', required=True)
    parser.add_argument('-d', '--crawl-depth', help='The crawl depth to use, default is 10')
    parser.add_argument('-a', '--all', help='Try to find all types of information',
                            action='store_true')
    parser.add_argument('-k', '--insecure', help='Allow insecure connections when using SSL',
                            action='store_true')
    parser.add_argument('-v', '--verbose', help='Verbose output',
                            action='store_true')
    args = parser.parse_args()

    if args.insecure:
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    
    crawler = Crawler(baseurl=args.url)
    crawler.run(url=args.url, verify=not(args.insecure))
    
    print('\nINTERNAL LINKS:\n=====================================')
    urls = crawler.get_urls()
    print('\n'.join([url for url in urls]))
            
    print('\nPOSSIBLE EMAILS:\n=====================================')
    mails = crawler.get_emails()
    for baseurl, addrs in mails.items():
        if addrs:
            #print(baseurl, ':')
            print('\n'.join([addr for addr in addrs]))
            
    print('\nEXTERNAL LINKS:\n=====================================')
    urls = crawler.get_ext_urls()
    for baseurl, links in urls.items():
        if links:
            #print(baseurl, ':')
            print('\n'.join([link for link in links]))


if __name__=='__main__':
    main()
