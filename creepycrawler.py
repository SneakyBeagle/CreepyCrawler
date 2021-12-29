#!/usr/bin/env python3


## Custom module includes
from src.version import *
from src.cc_db import db
from src.colours import clr
from src.splash import splash
from src.crawler import Crawler
from src.buster import Buster

## Default lib imports
import sys
import os
import argparse

def crawl(args):
    """
    Crawl function
    """    
    if args.output_file:
        #args.no_colours = True
        # Write to csv file
        pass

    if args.database:
        db.db_init(db_name=args.database)
        db.set_target(domain=get_domain(url=args.url),
                         protocol=get_protocol(url=args.url))
        
    if args.no_colours:
        clr.no_colours()

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
    if args.user_agent:
        crawler.run(url=args.url, verify=not(args.insecure), nr_threads=threads,
                    timeout=timeout, user_agent=args.user_agent)
    else:
        crawler.run(url=args.url, verify=not(args.insecure), nr_threads=threads,
                    timeout=timeout)

    if args.database:
        insert_links_into_db(target=get_domain(url=args.url),
                             protocol=get_protocol(url=args.url),
                             urls_dict=crawler.get_int_urls())
        insert_links_into_db(target=get_domain(url=args.url),
                             protocol=get_protocol(url=args.url),
                             urls_dict=crawler.get_ext_urls(), internal=False)

    print_results(crawler=crawler, args=args)
        
def dir_bust(args):
    if args.output_file:
        #args.no_colours = True
        # Write to csv file
        pass

    if args.database:
        db.db_init(db_name=args.database)
        db.set_target(domain=get_domain(url=args.url),
                         protocol=get_protocol(url=args.url))
        
    if args.no_colours:
        clr.no_colours()

    if args.insecure:
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

    if args.dir_depth:
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
        threads=10

    if args.timeout:
        timeout=args.timeout
    else:
        timeout=2

    if args.wordlist:
        buster = Buster(baseurl=args.url, depth=depth, exclude=args.exclude,
                        timeout=2, wordlist=args.wordlist)
    else:
        buster = Buster(baseurl=args.url, depth=depth, exclude=args.exclude,
                        timeout=2)

    if args.user_agent:
        buster.run(url=args.url, verify=not(args.insecure), nr_threads=threads,
                   timeout=timeout, user_agent=args.user_agent)
    else:
        buster.run(url=args.url, verify=not(args.insecure), nr_threads=threads,
                   timeout=timeout)

def single(args):
    """
    """
    if args.no_colours:
        clr.no_colours()

    if args.insecure:
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

    if args.timeout:
        timeout=args.timeout
    else:
        timeout=10

    crawler = Crawler(baseurl=args.url, exclude=args.exclude)
    if args.user_agent:
        crawler.run_single(url=args.url, verify=not(args.insecure),
                    timeout=timeout, user_agent=args.user_agent)
    else:
        crawler.run_single(url=args.url, verify=not(args.insecure),
                    timeout=timeout)

    if args.database:
        insert_links_into_db(target=get_domain(url=args.url),
                             protocol=get_protocol(url=args.url),
                             urls_dict=crawler.get_int_urls())
        insert_links_into_db(target=get_domain(url=args.url),
                             protocol=get_protocol(url=args.url),
                             urls_dict=crawler.get_ext_urls(), internal=False)

    print_results(crawler=crawler, args=args)


def auto(args):
    print("NOT IMPLEMENTED YET")

def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="The mode to run in")

    # CRAWL PARSER #
    crawl_parser = subparsers.add_parser('crawl', help='Crawl mode.')
    crawl_parser.add_argument('-u', '--url',
                              help='The base URL to start crawling from',
                              required=True)
    crawl_parser.add_argument('-d', '--crawl-depth',
                              help='The crawl depth to use, default is 1',
                              type=int)
    crawl_parser.add_argument('-t', '--threads',
                              help='Maximum number of threads to run simultaneously (default is 100)',
                              type=int)
    crawl_parser.add_argument('--timeout',
                              help='Timeout for requests, default is 2s',
                              type=int)
    crawl_parser.add_argument('-k', '--insecure', help='Allow insecure connections when using SSL',
                              action='store_true')
    crawl_parser.add_argument('--evidence', help='Print evidence',
                              action='store_true')
    crawl_parser.add_argument('-o', '--output-file', help='File to write the output into')
    crawl_parser.add_argument('-db', '--database', help='Database to write the output into')
    crawl_parser.add_argument('--no-colours', help='No colours',
                              action='store_true')
    crawl_parser.add_argument('--exclude', help='Exclude URLs that include this string')
    crawl_parser.add_argument('--user-agent', help='Specify user agent')
    crawl_parser.set_defaults(func=crawl)

    # DIRECTORY BUSTER PARSER #
    dir_parser = subparsers.add_parser('dir', help='Multi-threaded directory bust mode.')
    dir_parser.add_argument('-u', '--url',
                            help='The base URL to start crawling from',
                            required=True)
    dir_parser.add_argument('-d', '--dir-depth',
                              help='The dir depth to use, default is 1',
                              type=int)
    dir_parser.add_argument('-t', '--threads',
                            help='Maximum number of threads to run simultaneously (default is 100)',
                            type=int)
    dir_parser.add_argument('--timeout',
                            help='Timeout for requests, default is 2s',
                            type=int)
    dir_parser.add_argument('-k', '--insecure', help='Allow insecure connections when using SSL',
                            action='store_true')
    dir_parser.add_argument('--evidence', help='Print evidence',
                            action='store_true')
    dir_parser.add_argument('-o', '--output-file', help='File to write the output into')
    dir_parser.add_argument('-db', '--database', help='Database to write the output into')
    dir_parser.add_argument('--no-colours', help='No colours',
                            action='store_true')
    dir_parser.add_argument('--exclude', help='Exclude URLs that include this string')
    dir_parser.add_argument('-w', '--wordlist', help='Wordlist to use for dirbusting')
    dir_parser.add_argument('--user-agent', help='Specify user agent')
    dir_parser.set_defaults(func=dir_bust)

    # SINGLE PAGE PARSER #
    single_parser = subparsers.add_parser('single', help='Scan single page for interesting info. (Not implemented)')
    single_parser.add_argument('-u', '--url',
                             help='The base URL to start crawling from',
                             required=True)
    single_parser.add_argument('--timeout',
                              help='Timeout for requests, default is 10s',
                              type=int)
    single_parser.add_argument('-k', '--insecure', help='Allow insecure connections when using SSL',
                              action='store_true')
    single_parser.add_argument('--evidence', help='Print evidence',
                              action='store_true')
    single_parser.add_argument('-o', '--output-file', help='File to write the output into')
    single_parser.add_argument('-db', '--database', help='Database to write the output into')
    single_parser.add_argument('--no-colours', help='No colours',
                              action='store_true')
    single_parser.add_argument('--exclude', help='Exclude URLs that include this string')
    single_parser.add_argument('--user-agent', help='Specify user agent')
    single_parser.set_defaults(func=single)

    # AUTOMATED PARSER #
    auto_parser = subparsers.add_parser('auto', help='Automated mode. (Not implemented)')
    auto_parser.add_argument('-u', '--url',
                             help='The base URL to start crawling from',
                             required=True)
    auto_parser.set_defaults(func=auto)
    
    args = parser.parse_args()
    return args

def get_domain(url):
    if url.startswith('http://'):
        domain = (url.split('http://')[1]).split('/')[0]
    elif url.startswith('https://'):
        domain = (url.split('https://')[1]).split('/')[0]
    else:
        domain = url.split('/')[0]
    return domain

def get_protocol(url):
    if url.startswith('http://'):
        protocol = 'http://'
    elif url.startswith('https://'):
        protocol = 'https://'
    else:
        protocol = 'https://'
    return protocol

def insert_links_into_db(target, protocol, urls_dict, internal=True):
    for url,it in urls_dict.items():
        evidence=it['evidence']
        regex=' '#it['regex']
        status=it['status']
        if not(type(status)==int):
            status=0
        span=it['span']
        origin=' '#it['baseurl']
        length=it['length']
        if internal:
            db.insert_internal_link(target=target, protocol=protocol,
                                    url=url, evidence=evidence, status=status,
                                    regex=regex, origin=origin)
        else:
            db.insert_external_link(target=target, protocol=protocol,
                                    url=url, evidence=evidence, status=status,
                                    regex=regex, origin=origin)            

def print_results(crawler, args):
    print('\nINTERNAL LINKS:\n=====================================')
    urls = crawler.get_int_urls()
    for url,it in urls.items():
        if it['status'] == 200:
            print(clr.BOLD_WHITE+url+clr.RESET, clr.GREEN+'-->',
                  '['+str(it['status'])+']'+clr.RESET)
        elif not(it['status']=='Not visited'):
            print(clr.FAINT_WHITE+url+clr.RESET, clr.RED+'-->',
                  '['+str(it['status'])+']'+clr.RESET)
        else:
            print(clr.FAINT_WHITE+url+clr.RESET, clr.GREY+'-->', '['+str(it['status'])+']'+clr.RESET)
        if args.evidence:
            print('\t', clr.GREY+'Evidence:', it['evidence']+clr.RESET)
            print('\t', clr.GREY+'Regex:', it['regex']+clr.RESET)
            
    print('\nPOSSIBLE EMAILS:\n=====================================')
    if args.evidence:
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
            print(clr.BOLD_WHITE+url+clr.RESET, clr.GREEN+'-->', '['+str(it['status'])+']'+clr.RESET)
        else:
            print(clr.FAINT_WHITE+url+clr.RESET, clr.GREY+'-->', '['+str(it['status'])+']'+clr.RESET)
        if args.evidence:
            print('\t', clr.GREY+'Evidence:', it['evidence']+clr.RESET)
            print('\t', clr.GREY+'Regex:', it['regex']+clr.RESET)

    print('\nEXTERNAL LINKS:\n=====================================')
    urls = crawler.get_ext_urls()
    for url,it in urls.items():
        if it['status'] == 200:
            print(clr.BOLD_WHITE+url+clr.RESET, clr.GREEN+'-->', '['+str(it['status'])+']'+clr.RESET)
        else:
            print(clr.FAINT_WHITE+url+clr.RESET, clr.GREY+'-->', '['+str(it['status'])+']'+clr.RESET)
        if args.evidence:
            print('\t', clr.GREY+'Evidence:', it['evidence']+clr.RESET)
            print('\t', clr.GREY+'Regex:', it['regex']+clr.RESET)

    print('\nIP ADDRESSES AND VERSION NUMBERS:\n====================')
    if args.evidence:
        urls = crawler.get_ip_v()
        for baseurl, ip_v in urls.items():
            if ip_v:
                #print(baseurl)
                print('\n'.join([item for item in ip_v['ip_v']]))
                print('\t', clr.GREY+baseurl+clr.RESET)
                print('\t', clr.GREY+ip_v['evidence']+clr.RESET)
                print('\t', clr.GREY+ip_v['regex']+clr.RESET)
    else:
        ips = crawler.get_ips(as_dict=False)
        print('\n'.join([i for i in ips]))    

    print('\nVERSION NUMBERS:\n====================')
    if args.evidence:
        urls = crawler.get_versions()
        for baseurl, version in urls.items():
            if version:
                #print(baseurl)
                print('\n'.join([item for item in version['versions']]))
                print('\t', clr.GREY+baseurl+clr.RESET)
                print('\t', clr.GREY+version_v['evidence']+clr.RESET)
                print('\t', clr.GREY+version_v['regex']+clr.RESET)
    else:
        versions = crawler.get_versions(as_dict=False)
        print('\n'.join([i for i in versions]))
            
def main():
    """
    Main function
    """
    print(splash.splash+'\n'+TAG+'\n') # Print a random splash on startup

    args=parse_args()
    args.func(args)

if __name__=='__main__':
    main()
