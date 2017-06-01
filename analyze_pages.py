import json
import os
import re
from stemming.porter2 import stem
from bs4 import BeautifulSoup as bs
from time import sleep
from nltk.corpus import stopwords

def chunk_space(chunk):
    chunk_out = chunk + ' ' # Need to fix spacing issue
    return chunk_out

only_letters = re.compile("[^a-zA-Z0-9]+")
dataset = {}

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
for _,_,files in os.walk('raw_pages/'):
    for filename in files:
        with open('raw_pages/'+filename,'rb') as bod:
            soup = bs(bod,'lxml')
            dataset[filename] = []
            for rem in soup(["script","style"]):
                rem.extract()
            lines = (line.strip() for line in soup.get_text().splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  ")) # break
            text = ''.join(chunk_space(chunk) for chunk in chunks if chunk).encode('utf-8') # Get rid of all blank lines and ends of line
            
            try:
                text = text.decode('unicode_escape').encode('ascii', 'ignore')
            except:
                pass
            
            text = only_letters.sub(" ", text) # Remove non-letter/numbers
            text = text.lower().split()
            text = [stem(w) for w in text if not w in stop_words] # Remove articles, conjunctions, etc. and stems the output

            tempdict = {}
            def add_to_dict(word):
                if word in tempdict:
                    tempdict[word] += 1
                else:
                    tempdict[word] = 1
            previous = ''
            twoback = ''
            for t in text:
                add_to_dict(t)
                if not previous == '':
                    add_to_dict(previous+' '+t)
                if not twoback == '':
                    add_to_dict(twoback+' '+previous+' '+t)
                    
                twoback = previous
                previous = t
            dataset[filename].append(tempdict)
with open('Words/alltest.json','w') as output:
    # Dump it out so I don't have to request these files multiple times while debugging
    json.dump(dataset,output)