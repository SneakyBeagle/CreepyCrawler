#!/usr/bin/env python3

import sys
import argparse
import requests
import re
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
import scrapy

class Crawler(scrapy.Spider):

    def __init__(self, name, allowed_domains, start_urls):
        self.name=name
        self.allowed_domains=allowed_domains
        self.start_urls=start_urls

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        print(1)
        for href in response.xpath('//href').getall():
            print(href)
        #print(response)


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
    

    crawler=Crawler(name=args.url, allowed_domains=[args.url], start_urls=[args.url])
    crawler.start_requests()

if __name__=='__main__':
    main()
