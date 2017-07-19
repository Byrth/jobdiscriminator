import os

searchterm = ''
for dir,_,files in os.walk('Scraped/'+searchterm):
    
    print dir,_,files