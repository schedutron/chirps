"""Main bot script - bot.py
For the DigitalOcean Tutorial.
"""

# Parts of the standard library
import random
import time

# Installed library
from lxml.html import fromstring
import nltk  # Used here to split paragraphs into sentences during scraping.
nltk.download('punkt')
import requests  # Used to get the HTML source of a web page to be scraped.

from twitter import OAuth, Twitter

# Local credentials file defined above
import credentials

tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')  # This line will be explained soon

oauth = OAuth(
        credentials.ACCESS_TOKEN,
        credentials.ACCESS_SECRET,
        credentials.CONSUMER_KEY,
        credentials.CONSUMER_SECRET
    )
t = Twitter(auth=oauth)

HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)'
                      ' AppleWebKit/537.36 (KHTML, like Gecko) Cafari/537.36'
        }


def extract_paratext(paras):
    """Extracts text from <p> elements and returns a clean, tokenized random
    paragraph."""

    paras = [para.text_content() for para in paras if para.text_content()]
    para = random.choice(paras)
    return tokenizer.tokenize(para)


def extract_text(para):
    """Returns a sufficiently-large random text from a tokenized paragraph,
    if such text exists. Otherwise, returns None."""

    for _ in range(10):
        text = random.choice(para)
        if text and 60 < len(text) < 210:
            return text

    return None


def scrape_coursera():
    """Scrapes content from the Coursera blog."""
    url = 'https://blog.coursera.org'
    r = requests.get(url, headers=HEADERS)
    tree = fromstring(r.content)
    links = tree.xpath('//div[@class="recent"]//div[@class="title"]/a/@href')

    for link in links:
        r = requests.get(link, headers=HEADERS)
        blog_tree = fromstring(r.content)
        paras = blog_tree.xpath('//div[@class="entry-content"]/p')
        para = extract_paratext(paras)  # Gets a random paragraph.
        text = extract_text(para)  # Gets a good-enough random text quote.
        if not text:
            continue
        
        yield '"%s" %s' % (text, link)  # This will be passed on to the code that composes our tweet.


def scrape_thenewstack():
    """Scrapes news from thenewstack.io"""

    # For some, page may not be fetched without verify=False flag.
    r = requests.get('https://thenewstack.io', verify=False)

    tree = fromstring(r.content)
    links = tree.xpath('//div[@class="normalstory-box"]/header/h2/a/@href')

    for link in links:
        r = requests.get(link, verify=False)
        tree = fromstring(r.content)
        paras = tree.xpath('//div[@class="post-content"]/p')
        para = extract_paratext(paras)
        text = extract_text(para)  # Gets a good-enough random text quote.
        if not text:
            continue

        yield '"%s" %s' % (text, link)


def main():
    """Encompasses the main loop of the bot."""
    print('Bot started.')
    news_funcs = ['scrape_coursera', 'scrape_thenewstack']
    news_iterators = []  # A list for the scrapers we defined.
    for func in news_funcs:
        news_iterators.append(globals()[func]())
    while True:
        for i, iterator in enumerate(news_iterators):
            try:
                tweet = next(iterator)
                t.statuses.update(status=tweet)
                print(tweet, end='\n')
                time.sleep(600)  # Sleep for 10 minutes.
            except StopIteration:
                news_iterators[i] = globals()[newsfuncs[i]]()


if __name__ == "__main__":  # This checks if the script is called directly.
    main()
