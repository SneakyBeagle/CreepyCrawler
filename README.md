# CreepyCrawler
Website crawler/spider, buster and OSINT tool, using regular expressions instead of standard scraping techniques.


## Advantages
* Easy to use
* Regexes to find links embedded in page source, instead of ready made
  scraping frameworks. This has the advantage of being able to find
  links, even when not in logical locations embedded in html tags.
* Python
* Multi-threaded
* Crossplatform
* Little dependencies
* Single file executable

## Content
- [Usage](#usage)
- [Install](#install)

## Usage
CreepyCrawler has a number of modes available, with more coming. At the moment these modes include:
- [crawl](#crawl), crawling the webserver for available information
- [dir](#dir), traditional directory busting, non-recursive and multithreaded
- [single](#single), analyse a single URL. Same as [crawl](#crawl), but for a single page.
- [auto](#auto), automated mode. Not implemented yet, but is meant to combine crawl and dir recursively.

For a detailed help message, use the following
```
./creepycrawler.py --help
```

### Crawl
Simply attempts to find all links embedded into a webpages source and attempts to access them. Depending on the crawl depth, this process can repeat a number of times. Also finds email addresses, subdomains, external links, IPv4 addresses, IPv6 addresses and version numbers.

Simple run on https://example.com
```
./creepycrawler crawl -u https://example.com
```
For a detailed help message, use the following
```
./creepycrawler.py crawl --help
```

### Dir
Traditional directory buster. Takes a wordlist and tries them all. Does not run recursively and uses multi-threading to speed things up.

## Install
Currently, the install and build scripts can be used on Linux and MacOS systems to install (or only build) the tool. This builds a (single file) executable using pyinstaller and places it in /usr/bin/. If you don't want it there, it is also possible to only build the executable, which will then be located under ./dist/

### Linux
Build and install the executable to /usr/bin/
```
./install.sh
```
Only build the executable.
```
./build.sh
```

### MacOS
Build and install the executable to /usr/bin/
```
./install.sh
```
Only build the executable.
```
./build.sh
```

### Windows
```
# Not tested yet
```

