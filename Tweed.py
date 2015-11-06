import rx, requests, re, time, sys
from lxml import html


user_regex = re.compile('http://[^\s\.]*\.tumblr\.com')
to_crawl = set(sys.argv[1:])
crawled = set()
api_suffix = "/api/read"
def scrape_users(html_text, comp_regex=user_regex):
    unwanted = set(['http://static.tumblr.com', 'http://assets.tumblr.com'])
    return set(comp_regex.findall(html_text)) - unwanted

def map_to_posts(html_tree):
    p_tree = html_tree.xpath("//post")
    def to_posts(post_tree):
        reblog_dict = post_tree.xpath(".//a[@class='meta-item reblog-link']")
        src_dict = post_tree.xpath(".//a[@class='meta-item source-link']")

        if not src_dict: src_dict = reblog_dict
        if not reblog_dict: reblog_dict = src_dict

        return {
                'date': post_tree.attrib['date'],
                'type': post_tree.attrib['type'],

                #'reblog-link': reblog_dict[0].attrib['href'], 
                #'source-link': src_dict[0].attrib['href'],
                #'other': [x.attrib['href'] for x in post_tree.xpath(".//*[@href]") if x.attrib['href'] not in reblog_dict[0].values() and x.attrib['href'] not in src_dict[0].values()]
                }

    return [to_posts(n) for n in p_tree]

#get blog archives
#

html_stream = rx.subjects.Subject()

post_stream = html_stream.map(html.fromstring).flat_map(map_to_posts)
s1 = post_stream.subscribe()

new_user_stream = html_stream.map(scrape_users).flat_map(lambda a: a.difference(crawled))
s2 = new_user_stream.subscribe(to_crawl.add)



while 1:

    blog_url = to_crawl.pop()
    print(blog_url)
    html_stream.on_next(requests.get(blog_url).text)
    crawled.add(blog_url)
    print('sleeping...', len(to_crawl))
    time.sleep(5)
