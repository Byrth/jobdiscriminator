import json
import os
import unirest
from time import sleep

def get_job(jobkey):
    return unirest.get('https://www.indeed.com/viewjob?jk='+jobkey)

for _,_,files in os.walk('Scraped/'):
    for filename in files:
        with open('Scraped/'+filename,'rb') as jsonfile:
            for entry in json.load(jsonfile):
                if 'url' in entry:
                    if not os.path.isfile('raw_pages/'+entry['jobkey']):
                        with open('raw_pages/'+entry['jobkey'],'w') as htmlfile:
                            htmlfile.write(get_job(entry['jobkey']).body)
                            sleep(1) # Avoid throttling their API