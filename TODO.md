# TO DO list for CreepyCrawler

## General
- [x] Currently only supports root directory as starting point of crawling. Would be nice if this can be started from anywhere within the webdirectories
- [] Add custom header support
- [] Add custom cookie support
- [x] Add timeout support
- [] Add support for SQLite database to store results

## Fixes
- [] Add evidence printing to emails and IPs
- [] Split IP and versions and add IPv6
- [] Fix the main() mess with the printing or writing to file. That can be done way nicer
- [] Reduce evidence output by using the "span" to only show a portion

## Features
- [] Support multiple baseurls, instead of just one
- [] Read targets from file
- [] Add support to add to existing file, without duplicates
- [] Add more OSINT options, such as duckduckgo apis, shodan, etc (dnsdumpster?)

## Info gathering
- [] Search for form actions (HTML tags)
- [] Search for phone numbers
- [] Search for names (Based on list of known names? Or regex?)

## Maybe?
- [] Read request from file
- [] Support other request methods, and recognise when needing these
- [] Add debug mode
- [] Add support for .xlsx files to store results
- [] Add support for .xml files to store results
- [] Add support for .html files to store results
