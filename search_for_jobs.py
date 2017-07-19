import unirest
import json
from time import sleep
import os
from optparse import OptionParser

parser = OptionParser()
parser.add_option('-s','--search',dest="searchterm",help="The term to search indeed.com for",metavar="SEARCH")

(options,args) = parser.parse_args()


print 'Searching for '+options.searchterm

outputdir = 'Scraped/'+options.searchterm
if not os.path.exists(outputdir):
    os.mkdir(outputdir)

with open('userkey.txt','rb') as keyfile:
    userkey = keyfile.read(15) # 15 byte key assigned when you join the indeed ad API

def make_query_string(city,start=1):
    # 25 is the max limit they allow
    return 'http://api.indeed.com/ads/apisearch?publisher='+userkey+'&q="'+options.searchterm+'"&l='+city+'&sort=&radius=100&st=&jt=&start='+str(start)+'&limit=25&fromage=&filter=&latlong=1&co=us&chnl=&userip=1.2.3.4&useragent=Mozilla/%2F4.0%28Firefox%29&v=2&format=json'
all = []
city_list = [   'washington%2C dc',
                'seattle%2C wa',
                'san fransisco%2C ca',
                'cambridge%2C ma',
                'boston%2C ma',
                'chicago%2C il',
                'san diego%2C ca',
                'los angeles%2C ca',
                'new york%2C ny',
                'boulder%2C co',
                'denver%2C co',
                'salt lake city%2C, ut',
                'phoenix%2C az',
                'provo%2C, ut',
                'atlanta%2C ga',
                'pittsburgh%2C pa',
                'dallas%2C tx',
                'austin%2C tx',
                'houston%2C tx',
                'sacramento%2C ca',
                'minneapolis%2C mn',
                'philadelphia%2C pa',
                'detroit%2C mi',
                'madison%2C wi',
                'baltimore%2C md',
                'new orleans%2C la',
                'richmond%2C va',
                'portland%2C or',
                'hartford%2C ct',
                '', #National
                ]
for city in city_list:
    results = []
    response = unirest.get(make_query_string(city))
    results = results + response.body['results']
    last_end = response.body['end']
    while response.body['end'] < min(1000,response.body['totalResults']): # It turns out that Indeed's API caps you off at 1000 results returned.
        sleep(1) # Avoid throttling their API
        response = unirest.get(make_query_string(city,response.body['end']))
        if last_end != response.body['end']:
            results = results + response.body['results']
            last_end = response.body['end']
        else:
            break
    if city != '':
        with open(outputdir+'/'+city+'.json','w') as output:
            json.dump(results,output)
        print city+' done!'
    else:
        with open(outputdir+'/National.json','w') as output:
            json.dump(results,output)
        print 'National done!'
    all = all + results
with open(outputdir+'/all.json','w') as output:
    json.dump(all,output)
print 'All done!'