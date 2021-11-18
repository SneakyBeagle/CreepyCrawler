#!/usr/bin/env python3


## Custom module includes
from src.version import *
from src.db import DB
from src.colours import clr
from src.splash import splash
from src.crawler import Crawler

## Default lib imports
import sys
import os
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', help='The base URL to start crawling from', required=True)
    parser.add_argument('-d', '--crawl-depth', help='The crawl depth to use, default is 10', type=int)
    parser.add_argument('-o', '--output-file', help='File to write the output into')
    parser.add_argument('-db', '--database', help='Database to write the output into')
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
    return args

def main():
    """
    Main function
    """
    v='''
    SneakyBeagle
     v0.1 2021'''
    
    print(splash.splash+'\n'+TAG+'\n')

    args=get_args()

    fd = sys.stdout
    _print=False
    if args.output_file:
        args.no_colours = True
        fd = args.output_file
        _print=True

    if args.database:
        db=DB(db_name=args.database)

    if args.no_colours:
        clr.BOLD_WHITE=''
        clr.FAINT_WHITE=''
        clr.RED=''
        clr.GREEN=''
        clr.GREY=''
        clr.RESET=''
    
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
                    print(clr.BOLD_WHITE+url+clr.RESET, clr.GREEN+'-->', '['+str(it['status'])+']'+clr.RESET,
                          file=f)
                else:
                    print(clr.FAINT_WHITE+url+clr.RESET, clr.GREY+'-->', '['+str(it['status'])+']'+clr.RESET,
                          file=f)
                if args.verbose or args.evidence:
                    print('\t', clr.GREY+'Evidence:', it['evidence']+clr.RESET,
                          file=f)
                    print('\t', clr.GREY+'Regex:', it['regex']+clr.RESET,
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
                    print(clr.BOLD_WHITE+url+clr.RESET, clr.GREEN+'-->', '['+str(it['status'])+']'+clr.RESET,
                          file=f)
                else:
                    print(clr.FAINT_WHITE+url+clr.RESET, clr.GREY+'-->', '['+str(it['status'])+']'+clr.RESET,
                          file=f)
                if args.verbose or args.evidence:
                    print('\t', clr.GREY+'Evidence:', it['evidence']+clr.RESET,
                          file=f)
                    print('\t', clr.GREY+'Regex:', it['regex']+clr.RESET,
                          file=f)
            
            print('\n## EXTERNAL LINKS ##\n', file=f)
            print('* (Back to Top)[crawl_report]', file=f)
            urls = crawler.get_ext_urls()
            for url,it in urls.items():
                if it['status'] == 200:
                    print(clr.BOLD_WHITE+url+clr.RESET, clr.GREEN+'-->', '['+str(it['status'])+']'+clr.RESET,
                          file=f)
                else:
                    print(clr.FAINT_WHITE+url+clr.RESET, clr.GREY+'-->', '['+str(it['status'])+']'+clr.RESET,
                          file=f)
                if args.verbose or args.evidence:
                    print('\t', clr.GREY+'Evidence:', it['evidence']+clr.RESET,
                          file=f)
                    print('\t', clr.GREY+'Regex:', it['regex']+clr.RESET,
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
                        print('\t', clr.GREY+baseurl+clr.RESET,
                              file=f)
                        print('\t', clr.GREY+ip_v['evidence']+clr.RESET,
                              file=f)
                        print('\t', clr.GREY+ip_v['regex']+clr.RESET,
                              file=f)
            else:
                ip_vs = crawler.get_ip_v(as_dict=False)
                print('\n'.join([i for i in ip_vs]), file=f)

    else:
        print('\nINTERNAL LINKS:\n=====================================')
        urls = crawler.get_int_urls()
        for url,it in urls.items():
            if it['status'] == 200:
                print(clr.BOLD_WHITE+url+clr.RESET, clr.GREEN+'-->', '['+str(it['status'])+']'+clr.RESET)
            else:
                print(clr.FAINT_WHITE+url+clr.RESET, clr.GREY+'-->', '['+str(it['status'])+']'+clr.RESET)
            if args.verbose or args.evidence:
                print('\t', clr.GREY+'Evidence:', it['evidence']+clr.RESET)
                print('\t', clr.GREY+'Regex:', it['regex']+clr.RESET)
            
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
                print(clr.BOLD_WHITE+url+clr.RESET, clr.GREEN+'-->', '['+str(it['status'])+']'+clr.RESET)
            else:
                print(clr.FAINT_WHITE+url+clr.RESET, clr.GREY+'-->', '['+str(it['status'])+']'+clr.RESET)
            if args.verbose or args.evidence:
                print('\t', clr.GREY+'Evidence:', it['evidence']+clr.RESET)
                print('\t', clr.GREY+'Regex:', it['regex']+clr.RESET)

        print('\nEXTERNAL LINKS:\n=====================================')
        urls = crawler.get_ext_urls()
        for url,it in urls.items():
            if it['status'] == 200:
                print(clr.BOLD_WHITE+url+clr.RESET, clr.GREEN+'-->', '['+str(it['status'])+']'+clr.RESET)
            else:
                print(clr.FAINT_WHITE+url+clr.RESET, clr.GREY+'-->', '['+str(it['status'])+']'+clr.RESET)
            if args.verbose or args.evidence:
                print('\t', clr.GREY+'Evidence:', it['evidence']+clr.RESET)
                print('\t', clr.GREY+'Regex:', it['regex']+clr.RESET)

        print('\nIP ADDRESSES AND VERSION NUMBERS:\n====================')
        if args.verbose or args.evidence:
            urls = crawler.get_ip_v()
            for baseurl, ip_v in urls.items():
                if ip_v:
                    #print(baseurl)
                    print('\n'.join([item for item in ip_v['ip_v']]))
                    print('\t', clr.GREY+baseurl+clr.RESET)
                    print('\t', clr.GREY+ip_v['evidence']+clr.RESET)
                    print('\t', clr.GREY+ip_v['regex']+clr.RESET)
        else:
            ip_vs = crawler.get_ip_v(as_dict=False)
            print('\n'.join([i for i in ip_vs]))


if __name__=='__main__':
    main()
