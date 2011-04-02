"""
Test functions for models.tools
"""

import numpy as np
from numpy.random import standard_normal
from numpy.testing import *

from scikits.statsmodels.tools import tools

class TestTools(TestCase):

    def test_recipr(self):
        X = np.array([[2,1],[-1,0]])
        Y = tools.recipr(X)
        assert_almost_equal(Y, np.array([[0.5,1],[0,0]]))

    def test_recipr0(self):
        X = np.array([[2,1],[-4,0]])
        Y = tools.recipr0(X)
        assert_almost_equal(Y, np.array([[0.5,1],[-0.25,0]]))

    def test_rank(self):
        X = standard_normal((40,10))
        self.assertEquals(tools.rank(X), 10)

        X[:,0] = X[:,1] + X[:,2]
        self.assertEquals(tools.rank(X), 9)

    def test_fullrank(self):
        X = standard_normal((40,10))
        X[:,0] = X[:,1] + X[:,2]

        Y = tools.fullrank(X)
        self.assertEquals(Y.shape, (40,9))
        self.assertEquals(tools.rank(Y), 9)

        X[:,5] = X[:,3] + X[:,4]
        Y = tools.fullrank(X)
        self.assertEquals(Y.shape, (40,8))
        self.assertEquals(tools.rank(Y), 8)

    def test_StepFunction(self):
        x = np.arange(20)
        y = np.arange(20)
        f = tools.StepFunction(x, y)
        assert_almost_equal(f( np.array([[3.2,4.5],[24,-3.1]]) ), [[ 3, 4], [19, 0]])

    def test_StepFunctionBadShape(self):
        x = np.arange(20)
        y = np.arange(21)
        self.assertRaises(ValueError, tools.StepFunction, x, y)
        x = np.zeros((2, 2))
        y = np.zeros((2, 2))
        self.assertRaises(ValueError, tools.StepFunction, x, y)

class TestCategoricalNumerical(object):
    #TODO: use assert_raises to check that bad inputs are taken care of
    def __init__(self):
        #import string
        stringabc = 'abcdefghijklmnopqrstuvwxy'
        self.des = np.random.randn(25,2)
        self.instr = np.floor(np.arange(10,60, step=2)/10)
        x=np.zeros((25,5))
        x[:5,0]=1
        x[5:10,1]=1
        x[10:15,2]=1
        x[15:20,3]=1
        x[20:25,4]=1
        self.dummy = x
        structdes = np.zeros((25,1),dtype=[('var1', 'f4'),('var2', 'f4'),
                    ('instrument','f4'),('str_instr','a10')])
        structdes['var1'] = self.des[:,0][:,None]
        structdes['var2'] = self.des[:,1][:,None]
        structdes['instrument'] = self.instr[:,None]
        string_var = [stringabc[0:5], stringabc[5:10],
                stringabc[10:15], stringabc[15:20],
                stringabc[20:25]]
        string_var *= 5
        self.string_var = np.array(sorted(string_var))
        structdes['str_instr'] = self.string_var[:,None]
        self.structdes = structdes
        self.recdes = structdes.view(np.recarray)

    def test_array2d(self):
        des = np.column_stack((self.des, self.instr, self.des))
        des = tools.categorical(des, col=2)
        assert_array_equal(des[:,-5:], self.dummy)
        assert_equal(des.shape[1],10)

    def test_array1d(self):
        des = tools.categorical(self.instr)
        assert_array_equal(des[:,-5:], self.dummy)
        assert_equal(des.shape[1],6)

    def test_array2d_drop(self):
        des = np.column_stack((self.des, self.instr, self.des))
        des = tools.categorical(des, col=2, drop=True)
        assert_array_equal(des[:,-5:], self.dummy)
        assert_equal(des.shape[1],9)

    def test_array1d_drop(self):
        des = tools.categorical(self.instr, drop=True)
        assert_array_equal(des, self.dummy)
        assert_equal(des.shape[1],5)

    def test_recarray2d(self):
        des = tools.categorical(self.recdes, col='instrument')
        # better way to do this?
        test_des = np.column_stack(([des[_] for _ in des.dtype.names[-5:]]))
        assert_array_equal(test_des, self.dummy)
        assert_equal(len(des.dtype.names), 9)

    def test_recarray2dint(self):
        des = tools.categorical(self.recdes, col=2)
        test_des = np.column_stack(([des[_] for _ in des.dtype.names[-5:]]))
        assert_array_equal(test_des, self.dummy)
        assert_equal(len(des.dtype.names), 9)
    
    def test_recarray1d(self):
        instr = self.structdes['instrument'].view(np.recarray)
        dum = tools.categorical(instr)
        test_dum = np.column_stack(([dum[_] for _ in dum.dtype.names[-5:]]))
        assert_array_equal(test_dum, self.dummy)
        assert_equal(len(dum.dtype.names), 6)

    def test_recarray1d_drop(self):
        instr = self.structdes['instrument'].view(np.recarray)
        dum = tools.categorical(instr, drop=True)
        test_dum = np.column_stack(([dum[_] for _ in dum.dtype.names]))
        assert_array_equal(test_dum, self.dummy)
        assert_equal(len(dum.dtype.names), 5)

    def test_recarray2d_drop(self):
        des = tools.categorical(self.recdes, col='instrument', drop=True)
        test_des = np.column_stack(([des[_] for _ in des.dtype.names[-5:]]))
        assert_array_equal(test_des, self.dummy)
        assert_equal(len(des.dtype.names), 8)

    def test_structarray2d(self):
        des = tools.categorical(self.structdes, col='instrument')
        test_des = np.column_stack(([des[_] for _ in des.dtype.names[-5:]]))
        assert_array_equal(test_des, self.dummy)
        assert_equal(len(des.dtype.names), 9)

    def test_structarray2dint(self):
        des = tools.categorical(self.structdes, col=2)
        test_des = np.column_stack(([des[_] for _ in des.dtype.names[-5:]]))
        assert_array_equal(test_des, self.dummy)
        assert_equal(len(des.dtype.names), 9)

    def test_structarray1d(self):
        instr = self.structdes['instrument'].view(dtype=[('var1', 'f4')])
        dum = tools.categorical(instr)
        test_dum = np.column_stack(([dum[_] for _ in dum.dtype.names[-5:]]))
        assert_array_equal(test_dum, self.dummy)
        assert_equal(len(dum.dtype.names), 6)

    def test_structarray2d_drop(self):
        des = tools.categorical(self.structdes, col='instrument', drop=True)
        test_des = np.column_stack(([des[_] for _ in des.dtype.names[-5:]]))
        assert_array_equal(test_des, self.dummy)
        assert_equal(len(des.dtype.names), 8)

    def test_structarray1d_drop(self):
        instr = self.structdes['instrument'].view(dtype=[('var1', 'f4')])
        dum = tools.categorical(instr, drop=True)
        test_dum = np.column_stack(([dum[_] for _ in dum.dtype.names]))
        assert_array_equal(test_dum, self.dummy)
        assert_equal(len(dum.dtype.names), 5)

#    def test_arraylike2d(self):
#        des = tools.categorical(self.structdes.tolist(), col=2)
#        test_des = des[:,-5:]
#        assert_array_equal(test_des, self.dummy)
#        assert_equal(des.shape[1], 9)

#    def test_arraylike1d(self):
#        instr = self.structdes['instrument'].tolist()
#        dum = tools.categorical(instr)
#        test_dum = dum[:,-5:]
#        assert_array_equal(test_dum, self.dummy)
#        assert_equal(dum.shape[1], 6)

#    def test_arraylike2d_drop(self):
#        des = tools.categorical(self.structdes.tolist(), col=2, drop=True)
#        test_des = des[:,-5:]
#        assert_array_equal(test__des, self.dummy)
#        assert_equal(des.shape[1], 8)

#    def test_arraylike1d_drop(self):
#        instr = self.structdes['instrument'].tolist()
#        dum = tools.categorical(instr, drop=True)
#        assert_array_equal(dum, self.dummy)
#        assert_equal(dum.shape[1], 5)


class TestCategoricalString(TestCategoricalNumerical):

# comment out until we have type coercion
#    def test_array2d(self):
#        des = np.column_stack((self.des, self.instr, self.des))
#        des = tools.categorical(des, col=2)
#        assert_array_equal(des[:,-5:], self.dummy)
#        assert_equal(des.shape[1],10)

#    def test_array1d(self):
#        des = tools.categorical(self.instr)
#        assert_array_equal(des[:,-5:], self.dummy)
#        assert_equal(des.shape[1],6)

#    def test_array2d_drop(self):
#        des = np.column_stack((self.des, self.instr, self.des))
#        des = tools.categorical(des, col=2, drop=True)
#        assert_array_equal(des[:,-5:], self.dummy)
#        assert_equal(des.shape[1],9)

    def test_array1d_drop(self):
        des = tools.categorical(self.string_var, drop=True)
        assert_array_equal(des, self.dummy)
        assert_equal(des.shape[1],5)

    def test_recarray2d(self):
        des = tools.categorical(self.recdes, col='str_instr')
        # better way to do this?
        test_des = np.column_stack(([des[_] for _ in des.dtype.names[-5:]]))
        assert_array_equal(test_des, self.dummy)
        assert_equal(len(des.dtype.names), 9)

    def test_recarray2dint(self):
        des = tools.categorical(self.recdes, col=3)
        test_des = np.column_stack(([des[_] for _ in des.dtype.names[-5:]]))
        assert_array_equal(test_des, self.dummy)
        assert_equal(len(des.dtype.names), 9)
    
    def test_recarray1d(self):
        instr = self.structdes['str_instr'].view(np.recarray)
        dum = tools.categorical(instr)
        test_dum = np.column_stack(([dum[_] for _ in dum.dtype.names[-5:]]))
        assert_array_equal(test_dum, self.dummy)
        assert_equal(len(dum.dtype.names), 6)

    def test_recarray1d_drop(self):
        instr = self.structdes['str_instr'].view(np.recarray)
        dum = tools.categorical(instr, drop=True)
        test_dum = np.column_stack(([dum[_] for _ in dum.dtype.names]))
        assert_array_equal(test_dum, self.dummy)
        assert_equal(len(dum.dtype.names), 5)

    def test_recarray2d_drop(self):
        des = tools.categorical(self.recdes, col='str_instr', drop=True)
        test_des = np.column_stack(([des[_] for _ in des.dtype.names[-5:]]))
        assert_array_equal(test_des, self.dummy)
        assert_equal(len(des.dtype.names), 8)

    def test_structarray2d(self):
        des = tools.categorical(self.structdes, col='str_instr')
        test_des = np.column_stack(([des[_] for _ in des.dtype.names[-5:]]))
        assert_array_equal(test_des, self.dummy)
        assert_equal(len(des.dtype.names), 9)

    def test_structarray2dint(self):
        des = tools.categorical(self.structdes, col=3)
        test_des = np.column_stack(([des[_] for _ in des.dtype.names[-5:]]))
        assert_array_equal(test_des, self.dummy)
        assert_equal(len(des.dtype.names), 9)

    def test_structarray1d(self):
        instr = self.structdes['str_instr'].view(dtype=[('var1', 'a10')])
        dum = tools.categorical(instr)
        test_dum = np.column_stack(([dum[_] for _ in dum.dtype.names[-5:]]))
        assert_array_equal(test_dum, self.dummy)
        assert_equal(len(dum.dtype.names), 6)

    def test_structarray2d_drop(self):
        des = tools.categorical(self.structdes, col='str_instr', drop=True)
        test_des = np.column_stack(([des[_] for _ in des.dtype.names[-5:]]))
        assert_array_equal(test_des, self.dummy)
        assert_equal(len(des.dtype.names), 8)

    def test_structarray1d_drop(self):
        instr = self.structdes['str_instr'].view(dtype=[('var1', 'a10')])
        dum = tools.categorical(instr, drop=True)
        test_dum = np.column_stack(([dum[_] for _ in dum.dtype.names]))
        assert_array_equal(test_dum, self.dummy)
        assert_equal(len(dum.dtype.names), 5)

    def test_arraylike2d(self):
        pass

    def test_arraylike1d(self):
        pass

    def test_arraylike2d_drop(self):
        pass

    def test_arraylike1d_drop(self):
        pass


def test_chain_dot():
    A = np.arange(1,13).reshape(3,4)
    B = np.arange(3,15).reshape(4,3)
    C = np.arange(5,8).reshape(3,1)
    assert_equal(tools.chain_dot(A,B,C), np.array([[1820],[4300],[6780]]))
