link_patterns = [
    '^.*(?P<link>http[s]{0,1}\:\/\/[^\"^\,^\(^\)^\{^\}^\']+\.[^\"^\<^\>^\'^\,^\(^\)^\{^\}^\']+).*$', #general links
    
    '^(.*(href|link|action|value|src|srcset)\=\"(?P<link>[^\"^\<^\>^\,^\(^\)^\{^\}^\']+)\".*)+$', # links in tags
    
    '^(?P<link>\/.*\/)$', # links on robots.txt
    
    '.*(?P<link>g.co/[^\^\<^\>"]*)$' # google specific link often embedded in text, not in tags
]

mail_patterns = [
    '[A-z][0-9A-z\-\_\.]+\@[0-9A-z\-\_\.]+\.[a-z]+'
]

ip_patterns = [
    '[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}', # IPv4 adresses
    
    '([A-z]+[\s\-\_][A-z]*[\s\-\_]{0,1}[vV]{0,1}[\d]+\.[\d][\.\d]{0,2})', # Version in format like 'Bootstrap v3.3.7'

        '([vV]\s*[\d]+\.[\d][\.\d]{0,2})' # Version in format like 'v3.3.7'
]

version_patterns = [

]
