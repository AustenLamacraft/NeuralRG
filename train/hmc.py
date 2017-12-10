import os
import sys
sys.path.append(os.getcwd())

import numpy as np
import torch
torch.manual_seed(42)
from torch.autograd import Variable
from utils.autoCorrelation import autoCorrelationTimewithErr
from utils.acceptRate import acceptanceRate
from numpy.testing import assert_array_almost_equal,assert_array_equal

__all__ = ['HMCSampler']

def metropolis(e1,e2):
    diff = e1-e2
    return diff.data.exp()-diff.data.uniform_()>=0.0

class HMCSampler:
    def __init__(self,model,prior,collectdata,stepSize=0.1,interSteps=10,targetAcceptRate=0.65,stepSizeMin=0.001,stepSizeMax=1000,stepSizeChangeRatio=0.03,dynamicStepSize=False):
        pass
        self.model = model
        self.prior = prior
        self.stepSize = stepSize
        self.interSteps = interSteps
        self.collectdata = collectdata
        self.dynamicStepSize = dynamicStepSize
        if self.dynamicStepSize:
            self.targetAcceptRate = targetAcceptRate
            self.stepSizeMax = stepSizeMax
            self.stepSizeMin = stepSizeMin
            self.stepSizeInc = stepSizeChangeRatio+1
            self.stepSizeDec = 1-stepSizeChangeRatio

    def updateStepSize(self,accept,stepSize):
        ratio = torch.sum(accept)/accept.shape[0]*accept[1]
        if ratio > self.targetAcceptRate:
            newStepSize = stepSize*self.stepSizeInc
        else:
            newStepSize = stepSize*self.stepSizeDec
        newStepSize = max(min(self.stepSizeMax,newStepSize),self.stepSizeMin)
        return newStepSize

    @staticmethod
    def hmcUpdate(z,v,model,stepSize,interSteps):
        force = -model.backward(z)
        #print (type(force))
        vp = v - 0.5*stepSize*force
        zp  = z + stepSize*vp
        for i in range(interSteps):
            force = -model.backward(zp)
            vp -= stepSize*force
            zp += stepSize*vp
        force = -model.backward(zp)
        vp = vp - 0.5*stepSize*force
        return zp,vp

    @staticmethod
    def hamiltonian(energy,v):
        return -energy+0.5*torch.sum(v**2,1)

    def step(self,z):
        '''
        if isinstance(z,torch.DoubleTensor):
            v = torch.randn(z.size()).double()
        else:
            v = torch.randn(z.size())
        '''
        if isinstance(z.data,torch.DoubleTensor):
            v = Variable(torch.randn(z.size()).double(),requires_grad = True)
        else:
            v = Variable(torch.randn(z.size()),requires_grad = True)
        #x = z.clone()
        zp,vp = self.hmcUpdate(z,v,self.model,self.stepSize,self.interSteps)
        accept = metropolis(self.hamiltonian(self.model(z),v),self.hamiltonian(self.model(zp),vp))
        if self.dynamicStepSize:
            self.stepSize = self.updateStepSize(accept,self.stepSize)
        #print(type(accept.numpy()))
        accept = np.array([accept.numpy()]*self.model.nvars).transpose()
        mask = 1-accept
        x = Variable(torch.from_numpy(z.data.numpy()*mask +zp.data.numpy()*accept).double()) 
        #print (x)
        accratio = accept.mean()
        #accept = accept.view(-1,1)
        #x.masked_scatter_(accept, torch.masked_select(z, accept))
        #assert_array_almost_equal(x.cpu().numpy(),z.cpu().numpy())
        return accratio,x

    def run(self,batchSize,ntherm,nmeasure,nskip):
        z = self.prior(batchSize)

        for _ in range(ntherm):
            _,z = self.step(z)

        zpack = []
        measurePack = []
        accratio = 0.0
        for _ in range(nmeasure):
            for _ in range(nskip):
                a,z = self.step(z)
                accratio += a
            if self.collectdata:
                z_ = z.data.cpu().numpy()
                logp = self.model(z).data.cpu().numpy()
                logp.shape = (-1, 1)
                zpack.append(np.concatenate((z_, logp), axis=1))
                #zpack.append(z_)
            measure = self.measure(z)
            measurePack.append(measure)
        accratio /= float(nmeasure * nskip)
        print ('#accratio:', accratio)
        return zpack,None,measurePack,accratio, None, None

    def measure(self, x,measureFn=None):
        """
        This method measures some varibales.
        Args:
            measureFn (function): function to measure variables. If None, will run measure at target class.
        """
        if measureFn is None:
            measurements = self.model.measure(x)
        else:
            measurements = measureFn(x)
        return measurements
