import json
import numpy
from collections import Counter

words_to_keep = 1000
num_clust = 7

import os
from optparse import OptionParser
parser = OptionParser()
parser.add_option('-s','--search',dest="searchterm",help="The job descriptions to download from indeed.com",metavar="SEARCH")

(options,args) = parser.parse_args()

if options.searchterm:
    print 'Clustering '+options.searchterm+' pages'
    inputfile = 'Words/'+options.searchterm+'.json'
    scrapedpath = 'Scraped/'+options.searchterm+'/'
else:
    print 'Clustering all!'
    scrapedpath = 'Scraped/'
    inputfile = 'Words/all.json'

all_parameters = {} # A dictionary of dictionaries
entries = []
for curpath,_,files in os.walk(scrapedpath):
    if 'all.json' in files:
        with open(curpath+'/all.json','rb') as jsonfile:
            what = json.load(jsonfile)
            print len(what),type(what)
            entries.extend(what)
    
with open(inputfile,'rb') as jsonfile:
    words = json.load(jsonfile)
    
for entry in entries:
    if 'latitude' in entry and 'longitude' in entry and (entry['jobkey'] in words) and words[entry['jobkey']] and (not entry['jobkey'] in all_parameters):
        all_parameters[entry['jobkey']] = {'latitude':entry['latitude'],'longitude':entry['longitude'],'words':words[entry['jobkey']]}

all_words = Counter()
for jk in all_parameters:
    for a,b in all_parameters[jk]['words'].iteritems():
        all_words.update({a:b})
top = {}
keys = {}
count = 0
for v,_ in all_words.most_common(words_to_keep):
    top[v] = count
    keys[count] = v
    count+=1

matrix = numpy.zeros((len(all_parameters),words_to_keep),dtype=numpy.float32)
entry_counter = 0
data_order = []
for jk in all_parameters:
    for a,b in all_parameters[jk]['words'].iteritems():
        if a in top:
            matrix[entry_counter][top[a]] = b
    data_order = data_order + [jk]
    entry_counter += 1
# Mean normalize for frequency in the corpus
words_per_entry = matrix.sum(axis=1)
matrix = matrix/words_per_entry[:,None]

word_frequency = matrix.sum(axis=0)
matrix = matrix/word_frequency

from sklearn.cluster import KMeans
#inertias = {}
#labels = {}
#centroids = {}
#for k in [3*x+1 for x in range(num_clust)]:
#    inertias[k] = 0
#    for n in range(1,10):
#        k_means = KMeans(n_clusters=k).fit(matrix)
#        if (k_means.inertia_ < inertias[k]) or (inertias[k] == 0):
#            inertias[k] = k_means.inertia_
#            labels[k] = k_means.labels_
#            centroids[k] = k_means.cluster_centers_

labels = []
centroids = []
for k in [num_clust]:
    inertia = 0
    for n in range(1,10):
        k_means = KMeans(n_clusters=k).fit(matrix)
        if (k_means.inertia_ < inertia) or (inertia == 0):
            inertia = k_means.inertia_
            labels = k_means.labels_
            centroids = k_means.cluster_centers_
#print inertia

from matplotlib import pyplot as mpl
#mpl.plot([x for x,inertia in inertias.iteritems()],[inertia for x,inertia in inertias.iteritems()],'.')
#mpl.show()

#print matrix.dtype
def doPCA(data):
    from sklearn.decomposition import PCA
    pca=PCA(n_components=2)
    return pca.fit(data)
pca = doPCA(matrix)
print pca.explained_variance_ratio_
new_data = pca.transform(matrix)
fig1 = mpl.Figure()
#mpl.plot(100*new_data[:,0],1000*new_data[:,1],'.',markersize=2)
cluster_centers = pca.transform(centroids)
colors = [[0.91,0.61,0.17],'c','m','r','k','y','b'] # Change yellow to mustard, color data points based on label
for i,v in enumerate(labels):
    mpl.plot(100*new_data[i,0],1000*new_data[i,1],'.',markeredgecolor=colors[v],markersize=2)
for n in range(num_clust):
    mpl.plot(100*cluster_centers[n,0],1000*cluster_centers[n,1],'o',markerfacecolor=colors[n],markersize=10,mec=[.5,.5,.5])

j = numpy.fabs(pca.components_)
top_five = []
for n in j:
    top_five.append(sorted(range(len(n)), key=lambda i: n[i])[-5:])
xlabel = 'Comp1: '
ylabel = 'Comp2: '
count = 0
for component in top_five:
    commacount = 0
    for word_ind in component:
        if count == 0:
            if commacount > 0:
                xlabel += ', '
            xlabel += keys[word_ind]
        elif count == 1:
            if commacount > 0:
                ylabel += ', '
            ylabel += keys[word_ind]
        commacount += 1
    count += 1

mpl.xlabel(xlabel)
mpl.ylabel(ylabel)
fig1.suptitle('Cluster centroids')
mpl.show()

from scipy.misc import imread
from random import random
import math

fig2 = mpl.Figure()
with open('clipped.png','rb') as map:
    img=imread(map)
    mpl.imshow(img[:,:,2],zorder=0,extent=[-125,-66,25,52],cmap='binary')
for i,v in enumerate(labels):
    dist = random()/16 # fuzz size
    angle = random()*6.28
    mpl.plot(all_parameters[data_order[i]]['longitude']+(dist*math.cos(angle)),all_parameters[data_order[i]]['latitude']+(dist*math.sin(angle)),'.',markeredgecolor=colors[v],markersize=1)
    
mpl.show()