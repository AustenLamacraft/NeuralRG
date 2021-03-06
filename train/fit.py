import os
import sys
sys.path.append(os.getcwd())
import torch
torch.manual_seed(42)
from torch.autograd import Variable
import numpy as np

from model import Gaussian,MLP,RealNVP
from train import Ring2D, Ring5, Wave, Phi4, MCMC

class Buffer(object):
    def __init__(self,maximum,data=None,testRatio=0.0,cuda = None):
        testSize = int(testRatio*maximum)
        self.testRatio = testRatio
        self.capacity = int(maximum*(1+self.testRatio))
        self.data = data
        self.cuda = cuda
        if data is None:
            self.maximum = 0
        else:
            self.maximum = len(data)
    def draw(self,batchSize,testBatchSize=None):
        maximum = int(self.maximum*(1.0-self.testRatio))
        if batchSize > maximum:
            batchSize = maximum
        if self.cuda is None:
            perm = torch.randperm(maximum)
        else:
            perm = torch.randperm(maximum).cuda(self.cuda)
        if testBatchSize is None:
            return self.data[perm[:batchSize]]
        else:
            if testBatchSize > self.maximum-maximum:
                testBatchSize = self.maximum-maximum
            train =self.data[perm[:batchSize]]
            test = self.data[-testBatchSize-1:-1]
            return train,test
    def drawtest(self,testBatchSize):
        if testBatchSize>int(self.maximum*(self.testRatio)):
            testBatchSize = int(self.maximum*(self.testRatio))
        test = self.data[-testBatchSize-1:-1]
        return test
    def push(self,data):
        if self.data is None:
            self.data = data
            try:
                cuda = self.data.get_device()
            except AttributeError:
                cuda = None
            self.cuda = cuda
        else:
            self.data = torch.cat([self.data,data],0)
        if self.data.shape[0] > self.capacity:
            self._maintain()
        self.maximum = len(self.data)
    def _maintain(self):
        if self.cuda is None:
            perm = torch.randperm(self.data.shape[0])
        else:
            perm = torch.randperm(self.data.shape[0]).cuda(self.cuda)
        self.data = self.data[perm[:self.capacity]]
