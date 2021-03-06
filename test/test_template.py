import os
import sys
sys.path.append(os.getcwd())

import torch
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
torch.manual_seed(42)

import numpy as np
from numpy.testing import assert_array_almost_equal,assert_array_equal
from model import RealNVPtemplate,MLP,CNN,RealNVP,Gaussian

from subprocess import Popen, PIPE
import pytest

noCuda = 0
try:
    p  = Popen(["nvidia-smi","--query-gpu=index,utilization.gpu,memory.total,memory.used,memory.free,driver_version,name,gpu_serial,display_active,display_mode", "--format=csv,noheader,nounits"], stdout=PIPE)
except OSError:
    noCuda = 1

maxGPU = 0
if noCuda == 0:
    try:
        p = os.popen('nvidia-smi --query-gpu=index --format=csv,noheader,nounits')
        i = p.read().split('\n')
        maxGPU = int(i[-2])+1
    except OSError:
        noCuda = 1

skipIfNoCuda = pytest.mark.skipif(noCuda == 1,reason = "NO cuda insatllation, found through nvidia-smi")
skipIfOnlyOneGPU = pytest.mark.skipif(maxGPU < 2,reason = "Only one gpu")

def test_tempalte_invertibleMLP():

    print("test mlp")

    gaussian = Gaussian([2])

    sList = [MLP(2, 10), MLP(2, 10), MLP(2, 10), MLP(2, 10)]
    tList = [MLP(2, 10), MLP(2, 10), MLP(2, 10), MLP(2, 10)]

    realNVP = RealNVP([2], sList, tList, gaussian)
    x = realNVP.prior(10)
    mask = realNVP.createMask(["channel"]*4,ifByte=0)
    print("original")
    #print(x)

    z = realNVP._generate(x,realNVP.mask,realNVP.mask_,True)

    print("Forward")
    #print(z)

    zp = realNVP._inference(z,realNVP.mask,realNVP.mask_,True)

    print("Backward")
    #print(zp)

    assert_array_almost_equal(realNVP._generateLogjac.data.numpy(),-realNVP._inferenceLogjac.data.numpy())

    print("logProbability")
    print(realNVP._logProbability(z,realNVP.mask,realNVP.mask_))

    assert_array_almost_equal(x.data.numpy(),zp.data.numpy())


def test_tempalte_invertibleCNN():

    gaussian3d = Gaussian([2,4,4])
    x3d = gaussian3d(3)
    #z3dp = z3d[:,0,:,:].view(10,-1,4,4)
    #print(z3dp)

    netStructure = [[3,2,1,1],[4,2,1,1],[3,2,1,0],[2,2,1,0]] # [channel, filter_size, stride, padding]

    sList3d = [CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2)]
    tList3d = [CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2)]

    realNVP3d = RealNVP([2,4,4], sList3d, tList3d, gaussian3d)
    mask3d = realNVP3d.createMask(["channel"]*4,ifByte=0)

    print("Testing 3d")
    print("3d original:")
    #print(x3d)

    z3d = realNVP3d._generate(x3d,realNVP3d.mask,realNVP3d.mask_,True)
    print("3d forward:")
    #print(z3d)

    zp3d = realNVP3d._inference(z3d,realNVP3d.mask,realNVP3d.mask_,True)
    print("Backward")
    #print(zp3d)

    assert_array_almost_equal(realNVP3d._generateLogjac.data.numpy(),-realNVP3d._inferenceLogjac.data.numpy())

    print("3d logProbability")
    print(realNVP3d._logProbability(z3d,realNVP3d.mask,realNVP3d.mask_))

    saveDict3d = realNVP3d.saveModel({})
    torch.save(saveDict3d, './saveNet3d.testSave')
    # realNVP.loadModel({})
    sListp3d = [CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2)]
    tListp3d = [CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2)]

    realNVPp3d = RealNVP([2,4,4], sListp3d, tListp3d, gaussian3d)
    saveDictp3d = torch.load('./saveNet3d.testSave')
    realNVPp3d.loadModel(saveDictp3d)

    zz3d = realNVPp3d._generate(x3d,realNVPp3d.mask,realNVPp3d.mask_)
    print("3d Forward after restore")
    #print(zz3d)

    assert_array_almost_equal(x3d.data.numpy(),zp3d.data.numpy())
    assert_array_almost_equal(zz3d.data.numpy(),z3d.data.numpy())

def test_template_slice_function():
    gaussian3d = Gaussian([2,4,4])
    x = gaussian3d(3)
    #z3dp = z3d[:,0,:,:].view(10,-1,4,4)
    #print(z3dp)

    #print(x)
    netStructure = [[3,2,1,1],[4,2,1,1],[3,2,1,0],[1,2,1,0]] # [channel, filter_size, stride, padding]

    sList3d = [CNN(netStructure),CNN(netStructure),CNN(netStructure),CNN(netStructure)]
    tList3d = [CNN(netStructure),CNN(netStructure),CNN(netStructure),CNN(netStructure)]

    realNVP = RealNVP([2,4,4], sList3d, tList3d, gaussian3d)

    z = realNVP._generateWithSlice(x,0,True)
    #print(z)
    zz = realNVP._inferenceWithSlice(z,0,True)

    #print(zz)

    assert_array_almost_equal(x.data.numpy(),zz.data.numpy())
    #print(realNVP._generateLogjac.data.numpy())
    #print(realNVP._inferenceLogjac.data.numpy())
    assert_array_almost_equal(realNVP._generateLogjac.data.numpy(),-realNVP._inferenceLogjac.data.numpy())

def test_tempalte_contraction_mlp():
    gaussian = Gaussian([2])

    sList = [MLP(1, 10), MLP(1, 10), MLP(1, 10), MLP(1, 10)]
    tList = [MLP(1, 10), MLP(1, 10), MLP(1, 10), MLP(1, 10)]

    realNVP = RealNVP([2], sList, tList, gaussian)

    x = realNVP.prior(10)
    mask = realNVP.createMask(["channel"]*4,ifByte=1)
    print("original")
    #print(x)

    z = realNVP._generateWithContraction(x,realNVP.mask,realNVP.mask_,0,True)

    print("Forward")
    #print(z)

    zp = realNVP._inferenceWithContraction(z,realNVP.mask,realNVP.mask_,0,True)

    print("Backward")
    #print(zp)
    assert_array_almost_equal(realNVP._generateLogjac.data.numpy(),-realNVP._inferenceLogjac.data.numpy())

    x_data = realNVP.prior(10)
    y_data = realNVP.prior.logProbability(x_data)
    print("logProbability")
    '''
    for i in range(10):
        logp = realNVP._logProbabilityWithContraction(x_data,realNVP.mask,realNVP.mask_,0)

        criterion = torch.nn.MSELoss(size_average=True)
        loss = criterion(logp, y_data)
        print(loss)
    '''

def test_template_contraction_function_with_checkerboard():
    gaussian3d = Gaussian([2,4,4])
    x = gaussian3d(3)
    #z3dp = z3d[:,0,:,:].view(10,-1,4,4)
    #print(z3dp)

    #print(x)
    netStructure = [[3,2,1,1],[4,2,1,1],[3,2,1,0],[1,2,1,0]] # [channel, filter_size, stride, padding]

    sList3d = [CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2)]
    tList3d = [CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2)]

    realNVP = RealNVP([2,4,4], sList3d, tList3d, gaussian3d)
    mask = realNVP.createMask(["checkerboard"]*4,1)

    z = realNVP._generateWithContraction(x,realNVP.mask,realNVP.mask_,2,True)
    #print(z)

    zz = realNVP._inferenceWithContraction(z,realNVP.mask,realNVP.mask_,2,True)
    #print(zz)

    assert_array_almost_equal(x.data.numpy(),zz.data.numpy())
    assert_array_almost_equal(realNVP._generateLogjac.data.numpy(),-realNVP._inferenceLogjac.data.numpy())

def test_template_contraction_function_with_channel():
    gaussian3d = Gaussian([2,4,4])
    x = gaussian3d(3)
    #z3dp = z3d[:,0,:,:].view(10,-1,4,4)
    #print(z3dp)

    #print(x)
    netStructure = [[3,2,1,1],[4,2,1,1],[3,2,1,0],[1,2,1,0]] # [channel, filter_size, stride, padding]

    sList3d = [CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2)]
    tList3d = [CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2)]

    realNVP = RealNVP([2,4,4], sList3d, tList3d, gaussian3d)
    mask = realNVP.createMask(["channel"]*4,1)

    z = realNVP._generateWithContraction(x,realNVP.mask,realNVP.mask_,2,True)
    #print(z)

    zz = realNVP._inferenceWithContraction(z,realNVP.mask,realNVP.mask_,2,True)
    #print(zz)

    assert_array_almost_equal(x.data.numpy(),zz.data.numpy())
    assert_array_almost_equal(realNVP._generateLogjac.data.numpy(),-realNVP._inferenceLogjac.data.numpy())

@skipIfNoCuda
def test_contraction_cuda():
    gaussian3d = Gaussian([2,4,4])
    x = gaussian3d(3).cuda()
    #z3dp = z3d[:,0,:,:].view(10,-1,4,4)
    #print(z3dp)

    #print(x)
    netStructure = [[3,2,1,1],[4,2,1,1],[3,2,1,0],[1,2,1,0]] # [channel, filter_size, stride, padding]

    sList3d = [CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2)]
    tList3d = [CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2)]

    realNVP = RealNVP([2,4,4], sList3d, tList3d, gaussian3d)
    realNVP = realNVP.cuda()
    mask = realNVP.createMask(["checkerboard"]*4,1,cuda = 0)

    z = realNVP._generateWithContraction(x,realNVP.mask,realNVP.mask_,2,True)
    print(realNVP._logProbabilityWithContraction(z,realNVP.mask,realNVP.mask_,2))
    zz = realNVP._inferenceWithContraction(z,realNVP.mask,realNVP.mask_,2,True)

    assert_array_almost_equal(x.cpu().data.numpy(),zz.cpu().data.numpy())
    assert_array_almost_equal(realNVP._generateLogjac.data.cpu().numpy(),-realNVP._inferenceLogjac.data.cpu().numpy())

@skipIfNoCuda
def test_slice_cuda():
    gaussian3d = Gaussian([2,4,4])
    x = gaussian3d(3).cuda()
    netStructure = [[3,2,1,1],[4,2,1,1],[3,2,1,0],[1,2,1,0]]
    sList3d = [CNN(netStructure),CNN(netStructure),CNN(netStructure),CNN(netStructure)]
    tList3d = [CNN(netStructure),CNN(netStructure),CNN(netStructure),CNN(netStructure)]

    realNVP = RealNVP([2,4,4], sList3d, tList3d, gaussian3d)
    realNVP = realNVP.cuda()
    z = realNVP._generateWithSlice(x,0,True)
    print(realNVP._logProbabilityWithSlice(z,0))
    zz = realNVP._inferenceWithSlice(z,0,True)
    assert_array_almost_equal(x.cpu().data.numpy(),zz.cpu().data.numpy())
    assert_array_almost_equal(realNVP._generateLogjac.data.cpu().numpy(),-realNVP._inferenceLogjac.data.cpu().numpy())

@skipIfNoCuda
def test_tempalte_contractionCNN_cuda():
    gaussian3d = Gaussian([2,4,4])
    x3d = gaussian3d(3).cuda()
    netStructure = [[3,2,1,1],[4,2,1,1],[3,2,1,0],[2,2,1,0]]
    sList3d = [CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2)]
    tList3d = [CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2)]

    realNVP3d = RealNVP([2,4,4], sList3d, tList3d, gaussian3d)
    realNVP3d = realNVP3d.cuda()
    mask3d = realNVP3d.createMask(["channel"]*4,ifByte=0, cuda = 0)
    z3d = realNVP3d._generate(x3d,realNVP3d.mask,realNVP3d.mask_,True)
    zp3d = realNVP3d._inference(z3d,realNVP3d.mask,realNVP3d.mask_,True)
    print(realNVP3d._logProbability(z3d,realNVP3d.mask,realNVP3d.mask_))
    assert_array_almost_equal(x3d.cpu().data.numpy(),zp3d.cpu().data.numpy())
    assert_array_almost_equal(realNVP3d._generateLogjac.data.cpu().numpy(),-realNVP3d._inferenceLogjac.data.cpu().numpy())

@skipIfNoCuda
def test_tempalte_contractionCNN_checkerboard_cuda():
    gaussian3d = Gaussian([2,4,4])
    x3d = gaussian3d(3).cuda()
    netStructure = [[3,2,1,1],[4,2,1,1],[3,2,1,0],[2,2,1,0]]
    sList3d = [CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2)]
    tList3d = [CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2)]

    realNVP3d = RealNVP([2,4,4], sList3d, tList3d, gaussian3d)
    realNVP3d = realNVP3d.cuda()
    mask3d = realNVP3d.createMask(["checkerboard"]*4,ifByte=0,cuda = 0)
    z3d = realNVP3d._generate(x3d,realNVP3d.mask,realNVP3d.mask_,True)
    zp3d = realNVP3d._inference(z3d,realNVP3d.mask,realNVP3d.mask_,True)
    print(realNVP3d._logProbability(z3d,realNVP3d.mask,realNVP3d.mask_))
    assert_array_almost_equal(x3d.cpu().data.numpy(),zp3d.cpu().data.numpy())
    assert_array_almost_equal(realNVP3d._generateLogjac.data.cpu().numpy(),-realNVP3d._inferenceLogjac.data.cpu().numpy())

@skipIfOnlyOneGPU
def test_slice_cudaNo0():
    gaussian3d = Gaussian([2,4,4])
    x = gaussian3d(3).cuda(2)
    netStructure = [[3,2,1,1],[4,2,1,1],[3,2,1,0],[1,2,1,0]]
    sList3d = [CNN(netStructure),CNN(netStructure),CNN(netStructure),CNN(netStructure)]
    tList3d = [CNN(netStructure),CNN(netStructure),CNN(netStructure),CNN(netStructure)]

    realNVP = RealNVP([2,4,4], sList3d, tList3d, gaussian3d)
    realNVP = realNVP.cuda(2)
    z = realNVP._generateWithSlice(x,0,True)
    print(realNVP._logProbabilityWithSlice(z,0))
    zz = realNVP._inferenceWithSlice(z,0,True)
    assert_array_almost_equal(x.cpu().data.numpy(),zz.cpu().data.numpy())
    assert_array_almost_equal(realNVP._generateLogjac.data.cpu().numpy(),-realNVP._inferenceLogjac.data.cpu().numpy())

def test_forward():
    gaussian3d = Gaussian([2,4,4])
    x = gaussian3d(3)
    netStructure = [[3,2,1,1],[4,2,1,1],[3,2,1,0],[1,2,1,0]]
    sList3d = [CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2)]
    tList3d = [CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2)]

    realNVP = RealNVP([2,4,4], sList3d, tList3d, gaussian3d)
    z = realNVP(x)
    assert(list(z.data.shape) == [3])
    #assert(z.shape ==)
    realNVP.pointer = "generate"
    z = realNVP(x)
    assert(list(z.data.shape) == [3,2,4,4])

@skipIfOnlyOneGPU
def test_parallel():
    gaussian3d = Gaussian([2,4,4])
    x = gaussian3d(3)
    netStructure = [[3,2,1,1],[4,2,1,1],[3,2,1,0],[1,2,1,0]]
    sList3d = [CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2)]
    tList3d = [CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2)]

    realNVP = RealNVP([2,4,4], sList3d, tList3d, gaussian3d)
    z = realNVP(x)
    print(z)
    net = torch.nn.DataParallel(realNVP.cuda(0),device_ids=[0,1])
    output = net(x.cuda())
    print(output)

    assert_array_almost_equal(z.data.numpy(),output.cpu().data.numpy(),decimal=5)

def test_multiplyMask_generate_CNN():
    gaussian3d = Gaussian([2,4,4])
    x3d = gaussian3d(3)
    #z3dp = z3d[:,0,:,:].view(10,-1,4,4)
    #print(z3dp)

    netStructure = [[3,2,1,1],[4,2,1,1],[3,2,1,0],[2,2,1,0]] # [channel, filter_size, stride, padding]

    sList3d = [CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2)]
    tList3d = [CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2)]

    realNVP3d = RealNVP([2,4,4], sList3d, tList3d, gaussian3d)
    mask3d = realNVP3d.createMask(["channel","checkerboard","channel","checkerboard"],ifByte=0)

    print("Testing 3d")
    print("3d original:")
    #print(x3d)

    z3d = realNVP3d._generate(x3d,realNVP3d.mask,realNVP3d.mask_,True)
    print("3d forward:")
    #print(z3d)

    zp3d = realNVP3d._inference(z3d,realNVP3d.mask,realNVP3d.mask_,True)
    print("Backward")
    #print(zp3d)

    assert_array_almost_equal(realNVP3d._generateLogjac.data.numpy(),-realNVP3d._inferenceLogjac.data.numpy())

    print("3d logProbability")
    print(realNVP3d._logProbability(z3d,realNVP3d.mask,realNVP3d.mask_))

    saveDict3d = realNVP3d.saveModel({})
    torch.save(saveDict3d, './saveNet3d.testSave')
    # realNVP.loadModel({})
    sListp3d = [CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2)]
    tListp3d = [CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2)]

    realNVPp3d = RealNVP([2,4,4], sListp3d, tListp3d, gaussian3d)
    saveDictp3d = torch.load('./saveNet3d.testSave')
    realNVPp3d.loadModel(saveDictp3d)

    zz3d = realNVPp3d._generate(x3d,realNVPp3d.mask,realNVPp3d.mask_)
    print("3d Forward after restore")
    #print(zz3d)

    assert_array_almost_equal(x3d.data.numpy(),zp3d.data.numpy())
    assert_array_almost_equal(zz3d.data.numpy(),z3d.data.numpy())

def test_multiplyMask_generateWithContraction_CNN():
    gaussian3d = Gaussian([2,4,4])
    x = gaussian3d(3)
    #z3dp = z3d[:,0,:,:].view(10,-1,4,4)
    #print(z3dp)

    #print(x)
    netStructure = [[3,2,1,1],[4,2,1,1],[3,2,1,0],[1,2,1,0]] # [channel, filter_size, stride, padding]

    sList3d = [CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2)]
    tList3d = [CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2)]

    realNVP = RealNVP([2,4,4], sList3d, tList3d, gaussian3d)
    mask = realNVP.createMask(["channel","checkerboard","channel","checkerboard"],ifByte = 1)

    z = realNVP._generateWithContraction(x,realNVP.mask,realNVP.mask_,2,True)
    #print(z)

    zz = realNVP._inferenceWithContraction(z,realNVP.mask,realNVP.mask_,2,True)
    #print(zz)

    assert_array_almost_equal(x.data.numpy(),zz.data.numpy())
    assert_array_almost_equal(realNVP._generateLogjac.data.numpy(),-realNVP._inferenceLogjac.data.numpy())

def test_multiplyMask_generateWithSlice_CNN():
    gaussian3d = Gaussian([2,4,4])
    x = gaussian3d(3)
    #z3dp = z3d[:,0,:,:].view(10,-1,4,4)
    #print(z3dp)

    #print(x)
    netStructure = [[3,2,1,1],[4,2,1,1],[3,2,1,0],[1,2,1,0]] # [channel, filter_size, stride, padding]

    sList3d = [CNN(netStructure),CNN(netStructure),CNN(netStructure),CNN(netStructure)]
    tList3d = [CNN(netStructure),CNN(netStructure),CNN(netStructure),CNN(netStructure)]

    realNVP = RealNVP([2,4,4], sList3d, tList3d, gaussian3d)
    mask = realNVP.createMask(["channel","checkerboard","channel","checkerboard"],ifByte = 1)

    z = realNVP._generateWithSlice(x,0,True)
    #print(z)
    zz = realNVP._inferenceWithSlice(z,0,True)

    #print(zz)

    assert_array_almost_equal(x.data.numpy(),zz.data.numpy())
    #print(realNVP._generateLogjac.data.numpy())
    #print(realNVP._inferenceLogjac.data.numpy())
    assert_array_almost_equal(realNVP._generateLogjac.data.numpy(),-realNVP._inferenceLogjac.data.numpy())

@skipIfNoCuda
def test_contraction_cuda_withDifferentMasks ():
    gaussian3d = Gaussian([2,4,4])
    x = gaussian3d(3).cuda()
    #z3dp = z3d[:,0,:,:].view(10,-1,4,4)
    #print(z3dp)

    #print(x)
    netStructure = [[3,2,1,1],[4,2,1,1],[3,2,1,0],[1,2,1,0]] # [channel, filter_size, stride, padding]

    sList3d = [CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2)]
    tList3d = [CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2),CNN(netStructure,inchannel = 2)]

    realNVP = RealNVP([2,4,4], sList3d, tList3d, gaussian3d)
    realNVP = realNVP.cuda()
    mask = realNVP.createMask(["channel","checkerboard","channel","checkerboard"],1,cuda = 0)

    z = realNVP._generateWithContraction(x,realNVP.mask,realNVP.mask_,2,True)
    print(realNVP._logProbabilityWithContraction(z,realNVP.mask,realNVP.mask_,2))
    zz = realNVP._inferenceWithContraction(z,realNVP.mask,realNVP.mask_,2,True)

    assert_array_almost_equal(x.cpu().data.numpy(),zz.cpu().data.numpy())
    assert_array_almost_equal(realNVP._generateLogjac.data.cpu().numpy(),-realNVP._inferenceLogjac.data.cpu().numpy())



if __name__ == "__main__":
    test_forward()
    #test_tempalte_contraction_mlp()
    #test_tempalte_invertibleMLP()
    #test_tempalte_invertible()
    #test_template_slice_function()
    #test_template_contraction_function()
    #test_slice_cudaNo0()
    #test_tempalte_contractionCNN_cuda()
    #test_forward()
