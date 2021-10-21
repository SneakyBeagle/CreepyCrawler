# CreepyCrawler
Website crawler/spider, using regular expressions instead of standard scraping techniques. Simply attempts to find all links embedded into a webpages source and attempts to access them. Depending on the crawl depth, this process can repeat a number of times. Also finds email addresses, subdomains, external links and some IPv4 addresses and version numbers (although that requires some more work).

## Why?
I did not like any of the available webspiders/crawlers, so I decided
it was time to start building my own. Next to that, I wanted to
implement some advantages over other similar tools,
[read here about them](#advantages).
I use/plan on using this tool when doing reconnaissance with pentests
and such.

## Advantages
* Similar parameter usage as cURL and Gobuster (or at least, that is the aim)
* Regex to find links embedded in page source, instead of ready made
  scraping frameworks. This has the advantage of being able to find
  links, even when not embedded in html tags.
* Output in Markdown
* Python
* Crossplatform
* Little dependencies
* Single file, for now at least

## Usage

For a detailed help message, use the following
```
./creepycrawler --help
```

Run CreepyCrawler, targeting https://example.com, using a maximum of 100 threads, a crawl depth of 3 (can take a long time if many links are found), outputting the results in example_cc.md
```
./creepycrawler -u https://example.com -t 100 -d 3 -o example_cc.md
```

Shortest run possible at the moment. Uses the default crawl depth of 1 and the maximum number of threads. Does not output the results into a markdown file, although that is generally the best way to go.
```
./creepycrawler -u https://example.com -t 100
```

It is also possible to run with all default settings. Only the URL is required
```
./creepycrawler -u https://example.com
```
