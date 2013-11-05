'''
@created: Nov 4, 2013
@author: homoflashmanicus
@description: Manage arxiv citation network as sparse matrix
'''

import scipy.sparse as sps
from itertools import izip
import  utils

class Network:
    ''' Build and manage network.'''
    def __init__(self,directed=True):
        self.source = list()
        self.target = list()
        self.weight = list()
        self.directed=directed
        self.M = None

    def addLink(self,s,t,w):
        self.source.append(s)
        self.target.append(t)
        self.weight.append(w)

    def buildMatrix(self):
        self.M = sps.csr_matrix((self.weight, (self.source,self.target)))
        self.M._shape = (self.nNodes,self.nNodes)
        self.nLinks = self.M.sum()

    def outLinks(self, M=None, start=None, end=None):
        if M==None:
            return self.M[:,start:end].sum(1).A1
        else:
            return M[:,start:end].sum(1).A1

    def inLinks(self,M=None,start=None,end=None):
        if M==None:
            return self.M[start:end,:].sum(0).A1
        else:
            return M[start:end,:].sum(0).A1

class CitationNetwork(Network):
    def __init__(self):
        Network.__init__(self)
        self.dataFile = '' 
        self.papers = list()   
        self.paperIndex = dict()
        self.links = list()
        self.start = '9301'
        self.end = '0401'

    def load(self,dataFile):

        #read in citation network data
        self.dataFile = dataFile
        f=open(self.dataFile)
        raw = f.read()
        f.close()

        self.nNodes=0
        #loop through data to build sorted list of arxiv ids
        for line in raw.splitlines():
            if line[0] == '#': continue
            link = [ utils.fixid(p) for p in line.split()]
            self.links.append(link)
            for p in link:
                if p not in self.paperIndex:
                    self.papers.append(p)
                    self.paperIndex[p] = self.nNodes
                    self.nNodes +=1
        
        #sort papers by id and remap papersIndex
        self.papers = sorted(self.papers, key=lambda(p): utils.datehelper(p))
        self.paperIndex = dict( (p,i) for p,i in izip( self.papers, range(self.nNodes) ) )
        
        #build adjacency matrix
        for l in self.links:
            self.addLink(self.paperIndex[l[0]], self.paperIndex[l[1]], 1.0)
        self.buildMatrix()

    def inDegree(self, start=None, end=None):
        '''Get in degree of each paper, subject to the constraint that source node lies within the range start:end''' 
        if type(start)==str:
            try:
                startIndex = self.paperIndex[start+'001']
            except:
                startIndex = 0
            try:
                endIndex = self.paperIndex[end+'001']  
            except:
                endIndex =self.nNodes
        elif type(start)==int:
            startIndex=start
            endIndex=end
        else:
            startIndex = 0
            endIndex=self.nNodes
        return self.inLinks(start=startIndex,end=endIndex)
        
    def outDegree(self,start=None,end=None):
        '''Get out degree of each paper, subject to the constraint that target node lies within the range start:end''' 
        if type(start)==str:
            try:
                startIndex = self.paperIndex[start+'001']
            except:
                startIndex = 0
            try:
                endIndex = self.paperIndex[end+'001']  
            except:
                endIndex =self.nNodes
        elif type(start)==int:
            startIndex=start
            endIndex=end
        else:
            startIndex = 0
            endIndex=self.nNodes
        return self.outLinks(start=startIndex,end=endIndex)

    def dataToDict(self,data):
        '''Build dictionary of arxivid, data pairs'''
        return dict((aid, d) for aid,d in izip(self.papers,data))

    def filterByDate(self,data,start,end):
        if type(data)==dict:
            return  dict( (k,v) for k,v in data.iteritems() if utils.datecomp(start,k) and utils.datecomp(k,end) )
        elif type(data)==list:
            return  [v for k,v in izip(self.papers, data) if utils.datecomp(start,k)  and utils.datecomp(k,end) ]