'''calculating anova and verifying with NIST test data

compares my implementations, stats.f_oneway and anova using statsmodels.OLS
'''
import os
import numpy as np
from scipy import stats

filenameli = ['SiRstv.dat', 'SmLs01.dat', 'SmLs02.dat', 'SmLs03.dat', 'AtmWtAg.dat',
              'SmLs04.dat', 'SmLs05.dat', 'SmLs06.dat', 'SmLs07.dat', 'SmLs08.dat', 
              'SmLs09.dat']
##filename = 'SmLs03.dat' #'SiRstv.dat' #'SmLs09.dat'#, 'AtmWtAg.dat' #'SmLs07.dat'


##path = __file__
##print locals().keys()
###print path


def getnist(filename):
    fname = os.path.abspath(os.path.join('./data', filename))
    content = file(fname,'r').read().split('\n')
    data = [line.split() for line in content[60:]]
    certified = [line.split() for line in content[40:48] if line]
    dataf = np.loadtxt(fname, skiprows=60)
    y,x = dataf.T
    y = y.astype(int)
    caty = np.unique(y)
    f = float(certified[0][-1])
    R2 = float(certified[2][-1])
    resstd = float(certified[4][-1])
    dfbn = int(certified[0][-4])
    dfwn = int(certified[1][-3])  # dfbn->dfwn is this correct
    prob = stats.f.sf(f,dfbn,dfwn)
    return y, x, np.array([f, prob, R2, resstd]), certified, caty
    

from try_catdata import groupsstats_dummy, groupstatsbin


def anova_oneway(y, x, seq=0):
    # new version to match NIST
    # no generalization or checking of arguments, tested only for 1d 
    yrvs = y[:,np.newaxis] #- min(y)
    #subracting mean increases numerical accuracy for NIST test data sets
    xrvs = x[:,np.newaxis] - x.mean() #for 1d#- 1e12  trick for 'SmLs09.dat'

    meang, varg, xdevmeangr, countg = groupsstats_dummy(yrvs[:,:1], xrvs[:,:1])#, seq=0)
    #the following does not work as replacement
    #gcount, gmean , meanarr, withinvar, withinvararr = groupstatsbin(y, x)#, seq=0)
    sswn = np.dot(xdevmeangr.T,xdevmeangr)
    ssbn = np.dot((meang-xrvs.mean())**2, countg.T)
    nobs = yrvs.shape[0]
    ncat = meang.shape[1]
    dfbn = ncat - 1
    dfwn = nobs - ncat
    msb = ssbn/float(dfbn)
    msw = sswn/float(dfwn)
    f = msb/msw
    prob = stats.f.sf(f,dfbn,dfwn)
    R2 = (ssbn/(sswn+ssbn))  #R-squared
    resstd = np.sqrt(msw) #residual standard deviation
    #print f, prob
    def _fix2scalar(z): # return number
        if np.shape(z) == (1, 1): return z[0,0]
        else: return z
    f, prob, R2, resstd = map(_fix2scalar, (f, prob, R2, resstd))
    return f, prob, R2, resstd

import scikits.statsmodels as sm
from try_ols_anova import data2dummy

def anova_ols(y, x):
    X = sm.add_constant(data2dummy(x))    
    res = sm.OLS(y, X).fit()
    return res.fvalue, res.f_pvalue, res.rsquared, np.sqrt(res.mse_resid)
    


if __name__ == '__main__':
    print '\n using new ANOVA anova_oneway'
    print 'f, prob, R2, resstd'
    for fn in filenameli:
        print fn
        y, x, cert, certified, caty = getnist(fn)
        res = anova_oneway(y, x)
        print np.array(res) - cert

    print '\n using stats ANOVA f_oneway'
    for fn in filenameli:
        print fn
        y, x, cert, certified, caty = getnist(fn)
        xlist = [x[y==ii] for ii in caty]
        res = stats.f_oneway(*xlist)
        print np.array(res) - cert[:2]

    print '\n using statsmodels.OLS'
    print 'f, prob, R2, resstd'
    for fn in filenameli[:]:
        print fn
        y, x, cert, certified, caty = getnist(fn)
        res = anova_ols(x, y)
        print np.array(res) - cert
    

