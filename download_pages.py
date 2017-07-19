import json
import os
import unirest
from time import sleep
import os
from optparse import OptionParser
parser = OptionParser()
parser.add_option('-s','--search',dest="searchterm",help="The job descriptions to download from indeed.com",metavar="SEARCH")

(options,args) = parser.parse_args()


print 'Downloading '+options.searchterm+' pages'

inputdir = 'Scraped/'+options.searchterm+'/'
outputdir = 'raw_pages/'+options.searchterm+'/'
if not os.path.exists(inputdir):
    raise ValueError()
if not os.path.exists(outputdir):
    os.mkdir(outputdir)

def get_job(jobkey):
    return unirest.get('https://www.indeed.com/viewjob?jk='+jobkey)

count = 0
for _,_,files in os.walk(inputdir):
    for filename in files:
        with open(inputdir+filename,'rb') as jsonfile:
            for entry in json.load(jsonfile):
                if 'url' in entry:
                    if not os.path.isfile(outputdir+entry['jobkey']):
                        with open(outputdir+entry['jobkey'],'w') as htmlfile:
                            htmlfile.write(get_job(entry['jobkey']).body)
                        count = count + 1
                        if count%50 == 0:
                            print count+' new '+options.searchterm+' files downloaded'
                        sleep(1) # Avoid throttling their API
print 'Total: '+str(count)+' new '+options.searchterm+' files downloaded!'