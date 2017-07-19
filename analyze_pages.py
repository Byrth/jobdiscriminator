import json
import os
import re
from stemming.porter2 import stem
from bs4 import BeautifulSoup as bs
from time import sleep
from nltk.corpus import stopwords
from collections import defaultdict

import os
from optparse import OptionParser
parser = OptionParser()
parser.add_option('-s','--search',dest="searchterm",help="The job descriptions to download from indeed.com",metavar="SEARCH")

(options,args) = parser.parse_args()

def chunk_space(chunk):
    chunk_out = chunk + ' ' # Need to fix spacing issue
    return chunk_out

letters = re.compile("[^a-z ]+")
delimiters = re.compile("[\r\n\\\\]+")

stop_words = set(stopwords.words("english"))
stop_words.add('ca')
stop_words.add('york')
stop_words.add('new')
stop_words.add('ny')
stop_words.add('pa')
stop_words.add('san')
stop_words.add('francisco')
stop_words.add('dc')
stop_words.add('washington')
stop_words.add('seattle')
stop_words.add('ago')
stop_words.add('day')
stop_words.add('job')
stop_words.add('data')
stop_words.add('scientist')
stop_words.add('science')
stop_words.add('machine')
stop_words.add('learning')
stop_words.add('va')
stop_words.add('chicago')
stop_words.add('il')
stop_words.add('arlington')
stop_words.add('los')
stop_words.add('angeles')
stop_words.add('wa')
stop_words.add('hamilton')
stop_words.add('booz')
stop_words.add('allen')
stop_words.add('uber')
stop_words.add('religion')
stop_words.add('sex')
stop_words.add('name')
stop_words.add('sexual')
stop_words.add('orientation')
stop_words.add('gender')
stop_words.add('austin')
stop_words.add('houston')
stop_words.add('tx')
stop_words.add('md')
stop_words.add('baltimore')
stop_words.add('ut')
stop_words.add('ga')
stop_words.add('atlanta')
stop_words.add('palo')
stop_words.add('alto')
stop_words.add('hartford')
stop_words.add('ct')
stop_words.add('co')
stop_words.add('denver')

import time                                                

def timeme(method):
    def wrapper(*args, **kw):
        startTime = int(round(time.time() * 1000))
        result = method(*args, **kw)
        endTime = int(round(time.time() * 1000))

        print(endTime - startTime,'ms')
        return result

    return wrapper

def process_file(dir,filename):
    with open(dir+'/'+filename,'rb') as bod:
        soup = bs(bod,'lxml')
        for rem in soup(["script","style"]):
            rem.extract()
        text = letters.sub("",delimiters.sub(" ",soup.get_text(" ").lower()))
        
        words = (stem(word) for line in text.splitlines() for word in line.split(" ") if (word and not word in stop_words))

        tempdict = defaultdict(int)
        previous = None
        twoback = None
        for word in words:
            tempdict[word] += 1
            try:
                tempdict[previous+' '+word]+=1
                try:
                    tempdict[twoback+' '+previous+' '+word]+=1
                except:
                    pass
            except:
                pass
            twoback = previous
            previous = word
    if len(tempdict) > 150: # need at least 50 words to be considered a job description
        return tempdict


def it_over(inputdir,outputdir):
    count = 0
    basedir = ''
    for dir,_,files in os.walk(inputdir):
        dataset = {}
        if not basedir:
            basedir = dir # only a folder depth of 1
        for filename in files:
            dataset[filename] = process_file(dir,filename)
            count = count + 1
            if count%100 == 0:
                print str(count)+' files processed so far'
        if len(dataset) > 0:
            fname = re.sub(dir,'',basedir)+'.json'
            with open('Words/'+fname,'w') as output:
                # Dump it out so I don't have to reprocess these files multiple times while debugging
                print 'Dumping '+str(count)+' files to '+filename
                json.dump(dataset,output)
    print str(count)+' files processed total!'


if not options.searchterm:
    # Iterate over all downloaded jobs
    outputdir = 'Words/all.json'
    inputdir = 'raw_pages/'
    print 'Analyzing all downloaded pages!'
    it_over(inputdir,outputdir)
else:
    print 'Analyzing '+options.searchterm+' pages'

    outputdir = 'Words/'+options.searchterm+'.json'
    inputdir = 'raw_pages/'+options.searchterm+'/'
    if not os.path.exists(inputdir):
        raise ValueError()
    it_over(inputdir,outputdir)