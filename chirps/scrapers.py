import random
import re
from datetime import datetime
import unicodedata
from urllib.parse import urljoin

import nltk  # Used here to split paragraphs into sentences.
from lxml.html import fromstring
import requests


# tokenizer is used in scraping.
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
# headers are also used in scraping.
HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
                      ' AppleWebKit/537.36 (KHTML, like Gecko) Cafari/537.36'
        }

def extract_paratext(paras):
    """Extracts text from <p> elements and returns a clean, tokenized random
    paragraph."""

    paras = [para.text_content() for para in paras if para.text_content()]
    para = random.choice(paras)
    para = tokenizer.tokenize(para)
    # To fix unicode issues:
    return [unicodedata.normalize('NFKD', text) for text in para]


def extract_text(para):
    """Returns a sufficiently-large random text from a tokenized paragraph,
    if such text exists. Otherwise, returns None."""

    for _ in range(10):
        text = random.choice(para)
        if text and 60 < len(text) < 210:
            return text

    return None


def get_tech_news():  # I'm adventuring with regular expressions for parsing!
    """Finds news for tweeting, along with their links."""
    news_block_expr = re.compile(
        r'(?s)<li.*?a href="(.*?)".*?>.*?<img.*?src="(.*?)".*?>'
        r'<h2.*?>(.*?)</h2>.*?</a>'
    )
    latest_expr = re.compile(
        r'(?s)<section id="stream-panel".*ol>(.*)</ol>'
    )
    nyTech = requests.get(
        'https://nytimes.com/section/technology', headers=HEADERS)
    latest = latest_expr.search(nyTech.text)
    news_blocks = news_block_expr.findall(latest.group(1))

    for i in range(len(news_blocks)):
        item = (
            news_blocks[i][2].strip()
            + ' '
            + 'https://nytimes.com'
            + news_blocks[i][0],
            news_blocks[i][1].strip())  # This is img src.
        if item[1].startswith('Daily Report: '):
            item = item[14:]
        yield item


def scrape_themerkle(num_pages=17):
    """Scrapes news links from themerkle.com"""
    links = []
    for i in range(num_pages):
        r = requests.get("https://themerkle.com/page/%i" % (i+1))
        tree = fromstring(r.content)
        collection = tree.xpath("//h2[@class='title front-view-title']/a/@href")
        links.extend(collection)
    del tree

    for link in links:
        r = requests.get(link)
        tree = fromstring(r.content)
        paras = tree.xpath('//div[@class="thecontent"]/p')
        para = extract_paratext(paras)
        text = extract_text(para)
        if text is not None:
            yield '"%s" %s' % (text, link)


def scrape_udacity():
    """Scrapes content from the Udacity blog."""
    now = datetime.now()
    url = 'https://blog.udacity.com/%s/%s' % (now.year, now.month)
    r = requests.get(url, headers=HEADERS)
    tree = fromstring(r.content)
    links = tree.xpath('//div[@class="entry-content"]/p[last()]/a/@href')
    del tree

    for link in links:
        r = requests.get(link, headers=HEADERS)
        blog_tree = fromstring(r.content)
        paras = blog_tree.xpath('//div[@id="quotablecontent"]/p')
        para = extract_paratext(paras)  # Gets a random paragraph.
        text = extract_text(para)  # Gets a good-enough random text quote.
        if text is not None:
            yield '"%s" %s' % (text, link)


def scrape_coursera():
    """Scrapes content from the Coursera blog."""
    url = 'https://blog.coursera.org'
    r = requests.get(url, headers=HEADERS)
    tree = fromstring(r.content)
    links = tree.xpath('//div[@class="recent"]//div[@class="title"]/a/@href')
    del tree

    for link in links:
        r = requests.get(link, headers=HEADERS)
        blog_tree = fromstring(r.content)
        paras = blog_tree.xpath('//div[@class="entry-content"]/p')
        para = extract_paratext(paras)  # Gets a random paragraph.
        text = extract_text(para)  # Gets a good-enough random text quote.
        if text is not None:
            yield '"%s" %s' % (text, link)


def scrape_classcentral():
    """Scrapes content from Class Central Reports."""
    url = 'http://class-central.com/report'
    r = requests.get(url, headers=HEADERS)
    tree = fromstring(r.content)
    links = [urljoin(url, link) for link in tree.xpath('//article/a/@href')]
    del tree  # tree no longer needed in memory

    for link in links:
        r = requests.get(link)
        blog_tree = fromstring(r.content)
        paras = blog_tree.xpath('//div[@class="entry-content"]/p')
        para = extract_paratext(paras)  # Gets a random paragraph.
        text = extract_text(para)  # Gets a good-enough random text quote.
        if text is not None:
            yield '"%s" %s' % (text, link)


def scrape_thenewstack():
    """Scrapes news from thenewstack.io"""
    # verify=False is unsecure. But for our purposes, is it?
    r = requests.get('https://thenewstack.io')

    tree = fromstring(r.content)
    links = tree.xpath('//div[@class="normalstory-box"]/header/h2/a/@href')
    del tree

    for link in links:
        r = requests.get(link)
        tree = fromstring(r.content)
        paras = tree.xpath('//div[@class="post-content"]/p')
        para = extract_paratext(paras)
        text = extract_text(para)
        if text is not None:
            yield '"%s" %s' % (text, link)
