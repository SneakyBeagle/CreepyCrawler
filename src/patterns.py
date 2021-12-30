## IPv4 and IPv6 addresses #######################################
IPV4='[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}'
IPV6SEG='(?:(?:[0-9a-fA-F]){1,4})'
IPV6=[
    '(?:' + IPV6SEG + ':){7,7}' + IPV6SEG,                  # 1:2:3:4:5:6:7:8
    '(?:' + IPV6SEG + ':){1,7}:',                           # 1::                                 1:2:3:4:5:6:7::
    '(?:' + IPV6SEG + ':){1,6}:' + IPV6SEG,                 # 1::8               1:2:3:4:5:6::8   1:2:3:4:5:6::8
    '(?:' + IPV6SEG + ':){1,5}(?::' + IPV6SEG + '){1,2}',  # 1::7:8             1:2:3:4:5::7:8   1:2:3:4:5::8
    '(?:' + IPV6SEG + ':){1,4}(?::' + IPV6SEG + '){1,3}',  # 1::6:7:8           1:2:3:4::6:7:8   1:2:3:4::8
    '(?:' + IPV6SEG + ':){1,3}(?::' + IPV6SEG + '){1,4}',  # 1::5:6:7:8         1:2:3::5:6:7:8   1:2:3::8
    '(?:' + IPV6SEG + ':){1,2}(?::' + IPV6SEG + '){1,5}',  # 1::4:5:6:7:8       1:2::4:5:6:7:8   1:2::8
    IPV6SEG + ':(?:(?::' + IPV6SEG + '){1,6})',             # 1::3:4:5:6:7:8     1::3:4:5:6:7:8   1::8
    ':(?:(?::' + IPV6SEG + '){1,7}|:)',                     # ::2:3:4:5:6:7:8    ::2:3:4:5:6:7:8  ::8       ::
    'fe80:(?::' + IPV6SEG + '){0,4}%[0-9a-zA-Z]{1,}',       # fe80::7:8%eth0     fe80::7:8%1  (link-local IPv6 addresses with zone index)
    '::(?:ffff(?::0{1,4}){0,1}:){0,1}[^\s:]' + IPV4,     # ::255.255.255.255  ::ffff:255.255.255.255  ::ffff:0:255.255.255.255 (IPv4-mapped IPv6 addresses and IPv4-translated addresses)
    '(?:' + IPV6SEG + ':){1,4}:[^\s:]' + IPV4
]
IPV6='|'.join(['(?:{})'.format(line) for line in IPV6[::-1]])

ip_patterns = [
    IPV4, # IPv4 adresses
    IPV6
]
#####################################################################

link_patterns = [
    '^.*(?P<link>http[s]{0,1}\:\/\/[^\"^\,^\(^\)^\{^\}^\']+\.[^\"^\<^\>^\'^\,^\(^\)^\{^\}^\']+).*$', #general links
    
    '^(.*(href|link|action|value|src|srcset)\=\"(?P<link>[^\"^\<^\>^\,^\(^\)^\{^\}^\']+)\".*)+$', # links in tags
    
    '^(?P<link>\/.*\/)$', # links on robots.txt
    
    '.*(?P<link>g.co/[^\^\<^\>"]*)$' # google specific link often embedded in text, not in tags
]

mail_patterns = [
    '[A-z][0-9A-z\-\_\.]+\@[0-9A-z\-\_\.]+\.[a-z]+', # Normal email
    '[A-z][0-9A-z\-\_\.]+\%40[0-9A-z\-\_\.]+\.[a-z]+' # URL encoded
]

version_patterns = [
    '([A-z]+[\s\-\_][A-z]*[\s\-\_]{0,1}[vV]{0,1}[\d]+\.[\d][\.\d]{0,2})', # Version in format like 'Bootstrap v3.3.7'

    '([vV]\s*[\d]+\.[\d][\.\d]{0,2})' # Version in format like 'v3.3.7'
]

string_patterns = [
    '[a-zA-ZàáâäãåąčćęèéêëėįìíîïłńòóôöõøùúûüųūÿýżźñçčšžÀÁÂÄÃÅĄĆČĖĘÈÉÊËÌÍÎÏĮŁŃÒÓÔÖÕØÙÚÛÜŲŪŸÝŻŹÑßÇŒÆČŠŽ∂ð\ \,\.\'\-]+'
]

cred_patterns = [
    'AKIA[A-Z0-9]{20}' # AWS access key id
]

if __name__=='__main__':
    # Thanks to https://gist.github.com/dfee/6ed3a4b05cfe7a6faf40a2102408d5d8
    import re
    test = [
        '1::',
        '1:: and some more text',
        '1:2:3:4:5:6:7::',
        '1::8',
        '1:2:3:4:5:6::8',
        '1:2:3:4:5:6::8',
        '1::7:8',
        '1:2:3:4:5::7:8',
        '1:2:3:4:5::8',
        '1::6:7:8',
        '1:2:3:4::6:7:8',
        '1:2:3:4::8',
        '1::5:6:7:8',
        '1:2:3::5:6:7:8',
        '1:2:3::8',
        '1::4:5:6:7:8',
        '1:2::4:5:6:7:8',
        '1:2::8',
        '1::3:4:5:6:7:8',
        '1::3:4:5:6:7:8',
        '1::8',
        '::2:3:4:5:6:7:8',
        '::2:3:4:5:6:7:8',
        '::8',
        '::',
        'fe80::7:8%eth0',
        'fe80::7:8%1',
        '::255.255.255.255',
        '::ffff:255.255.255.255',
        '::ffff:0:255.255.255.255',
        '2001:db8:3:4::192.0.2.33',
        '64:ff9b::192.0.2.33',
        'test',
        '192.168.1.1',
        'a name is',
        'harry potter'
    ]

    def test_individual(tests):
        for t in tests:
            try:
                print(t, '->', re.search(IPV6, t).group())
                #assert re.search(IPV6, t).group() == t
            except AttributeError:
                print(t, 'is not a IPv6 address')
            
    def test_multiline(tests):
        _tests = tests[:]
        for t in re.findall(IPV6, ' '.join(tests)):
            print(t)
            try:
                _tests.remove(t)
            except ValueError:
                print('')
        for t in _tests:
            print(t, 'is not a IPv6 address')
        #assert not _tests

    def test_strings(tests):
        for t in tests:
            try:
                print(t, '->', re.search(string_patterns[0], t).group())
            except AttributeError:
                print(t, 'is not a string')

    test_individual(test)
    test_multiline(test)
    test_strings(test)
