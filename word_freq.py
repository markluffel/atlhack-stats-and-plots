#!/usr/bin/env python

from xml.etree import ElementTree as etree
import os,sys,time,re

bitsRegex = re.compile('[01]+')
junkRegex = re.compile(r'(<.*?>)|:|,|\.|\(|\)|"|\?|!|\+|/|(&quot;)')
dashesRegex = re.compile('(\W-)|(-\W)')

class Post(object):
    def __init__(self, title='', content='', date=None):
        self.title = title
        try:
            self.hackfest = int(bitsRegex.search(title).group(0),2)
        except:
            self.hackfest = ''
        self.content = content
        self.date = date
        self.wordHistogram = histogram(wordBag(content))
        self.wordFrequencyList = frequencyList(self.wordHistogram)
    
    def __contains__(self, word):
        return word in self.wordHistogram



def parseTimeStamp(stamp):
    stamp = stamp[:-6] # trim off the timezone offset
    return time.strptime(stamp, "%a, %d %b %Y %H:%M:%S")

def atlhackBlog(filename):
    blog = etree.parse(filename)
    for post in blog.findall('channel/item'):
        yield Post(
            content= post.find('description').text,
            date= parseTimeStamp(post.find('pubDate').text),
            title= post.find('title').text
        )



def stripHtml(content):
    content = re.sub(junkRegex, ' ', content)
    content = re.sub(dashesRegex, ' ', content)
    return content

def histogram(items):
    result = {}
    for item in items:
        try:
            result[item] += 1
        except KeyError:
            result[item] = 1
    return result

def mergeHistograms(histos):
    result = {}
    for histo in histos:
        for item,count in histo.iteritems():
            try:
                result[item] += count
            except KeyError:
                result[item] = count
    return result

def frequencyList(items=None,histo=None):
    if histo is None:
        assert items is not None
        histo = histogram(items)
    else:
        assert items is None
    
    freq = [(count,item) for item,count in histo.iteritems()]
    freq.sort(reverse=True)
    return freq

def wordBag(text,removeStopwords=True):
    if not hasattr(wordBag,'stopWords'):
        wordBag.stopwords = set(open('stop_words.txt','r').read().split())
    
    text = stripHtml(text)
    text = text.lower()
    words = text.split()
    if DEBUG:
        print ' '.join(words)
    
    if removeStopwords:
        return [w for w in words if w not in wordBag.stopwords]
    else:
        return words

def wordFrequencyList(text):
    return frequencyList(items=wordBag(text))




def rpad(text,width):
    text = str(text)
    return text + (' '*(width-len(text)))

def lpad(text,width):
    text = str(text)
    return (' '*(width-len(text))) + text



def main(feedUrl,filename):
    if not os.path.exists(filename):
        os.system('curl '+feedUrl+' > '+filename)
    
    blog = list(atlhackBlog(filename))
    blogHisto = mergeHistograms(post.wordHistogram for post in blog)
    freq = frequencyList(histo=blogHisto)
    totalWords = sum(len(post.wordFrequencyList) for post in blog)
    
    for count,word in freq:
        if count < 3:
            break
        
        print rpad(word,20),rpad(count,5),
        for post in blog:
            if word in post:
                print lpad(post.hackfest,3),
            else:
                print '   ',
        print
    
    return (blog,freq)



DEBUG = '--debug' in sys.argv
if __name__ == '__main__':
    main(
        feedUrl='http://atlhack.org/node/feed',
        filename='atlhack.xml'
    )
