"""
Statistical tools for time series analysis
"""

import numpy as np
from scipy import stats, signal
import scikits.statsmodels as sm
from scikits.statsmodels.sandbox.tsa.tsatools import lagmat, lagmat2ds
from adfvalues import *
#from scikits.statsmodels.sandbox.rls import RLS

#NOTE: now in two places to avoid circular import
#TODO: I like the bunch pattern for this too.
class ResultsStore(object):
    def __str__(self):
        return self._str

#TODO: include drift keyword, only valid with regression == "c"
# just changes the distribution of the test statistic to a t distribution
def adfuller(x, maxlag=None, regression="c", autolag='AIC', 
    store=False):
    '''Augmented Dickey-Fuller unit root test

    The Augmented Dickey-Fuller test can be used to test for a unit root in a 
    univariate process in the presence of serial correlation.
    
    Parameters
    ----------
    x : array_like, 1d
        data series
    maxlag : int
        Maximum lag which is included in test, default 12*(nobs/100)^{1/4}
    regression : str {'c','ct','ctt','nc'}
        Constant and trend order to include in regression
        * 'c' : constant only
        * 'ct' : constant and trend
        * 'ctt' : constant, and linear and quadratic trend
        * 'nc' : no constant, no trend
    autolag : {'AIC', 'BIC', 't-stat', None}
        * if None, then maxlag lags are used
        * if 'AIC' or 'BIC', then the number of lags is chosen to minimize the
          corresponding information criterium
        * 't-stat' based choice of maxlag.  Starts with maxlag and drops a 
          lag until the t-statistic on the last lag length is significant at
          the 95 % level.
    store : {False, True}
        If True, then a result instance is returned additionally to
        the adf statistic
        
    Returns
    -------
    adf : float
        Test statistic
    usedlag : int
        Number of lags used.
    pvalue : float
        MacKinnon's approximate p-value based on MacKinnon (1994)
    critical values : dict
        Critical values for the test statistic at the 1 %, 5 %, and 10 % levels.
        Based on MacKinnon (2010)
    resstore : (optional) instance of ResultStore
        an instance of a dummy class with results attached as attributes
    
    Notes
    -----
    If the p-value is close to significant, then the critical values should be
    used to judge whether to accept or reject the null.

    The pvalues are (will be) interpolated from the table of critical
    values. NOT YET DONE
    
    still requires pvalues and maybe some cleanup
    
    ''Verification''
    
    Looks correctly sized in Monte Carlo studies.
    Differs from R tseries results in second decimal, based on a few examples
    
    Examples
    --------
    see example script
    
    References
    ----------
    Greene
    Hamilton

    Critical Values (Canonical reference)
    Fuller, W.A. 1996. `Introduction to Statistical Time Series.` 2nd ed.
        New York: Wiley.

    P-Values (regression surface approximation)
    MacKinnon, J.G. 1994.  "Approximate asymptotic distribution functions for 
        unit-root and cointegration tests.  `Journal of Business and Economic
        Statistics` 12, 167-76.

    '''
    regression = regression.lower()
    if regression not in ['c','nc','ct','ctt']:
        raise ValueError("regression option %s not understood") % regression
    x = np.asarray(x)
    nobs = x.shape[0]
    if maxlag is None:
        #from Greene referencing Schwert 1989
        maxlag = 12. * np.power(nobs/100., 1/4.)

    xdiff = np.diff(x)

    xdall = lagmat(xdiff[:,None], maxlag, trim='both')
    nobs = xdall.shape[0]
    if regression == 'c':
        trendorder = 0
    elif regression == 'nc':
        trendorder = -1
    elif regression == 'ct':
        trendorder = 1
    elif regression == 'ctt':
        trendorder = 2
    trend = np.vander(np.arange(nobs), trendorder+1)
    xdall[:,0] = x[-nobs-1:-1] # replace 0 xdiff with level of x
    xdshort = xdiff[-nobs:]
#    xdshort = x[-nobs:]
#TODO: allow for this as endog, with Phillips Perron or DF test?

    if store: 
        resstore = ResultsStore()

    if autolag:
        autolag = autolag.lower()
        #search for lag length with highest information criteria
        #Note: I use the same number of observations to have comparable IC
        results = {}
        for mlag in range(1,int(maxlag+1)):  # +1 so maxlag is inclusive
            results[mlag] = sm.OLS(xdshort, np.column_stack([xdall[:,:mlag+1],
                trend])).fit()
            #NOTE: mlag+1 since level is in first column.

        if autolag == 'aic':                    
            icbest, bestlag = max((v.aic,k) for k,v in results.iteritems())
        elif autolag == 'bic':                    
            icbest, bestlag = max((v.bic,k) for k,v in results.iteritems())
        elif autolag == 't-stat':
            lags = sorted(results.keys())[::-1]
            stop = stats.norm.ppf(.95)
            i = 0
            lastt, bestlag = results[lags[i]].t(-trendorder-1)
            i += 1
            while not (abs(lastt) >= stop):
                lastt, bestlag = results[lags[i]].t(-trendorder-1)
                i += 1
        else:
            raise ValueError("autolag can be None, 'aic', 'bic', or 't-stat'")

        #rerun ols with best autolag  
#        xdall = lagmat(xdiff[:,None], bestlag, trim='forward')
        xdall = lagmat(xdiff[:,None], bestlag, trim='both')
        # Why trim forward here and not above?
        nobs = xdall.shape[0]
        trend = np.vander(np.arange(nobs), trendorder+1)
        xdall[:,0] = x[-nobs-1:-1] # replace 0 xdiff with level of x
        xdshort = xdiff[-nobs:]
#        xdshort = x[-nobs:]
# NOTE: switched the above.  xdiff should be endog for augmented df
        usedlag = bestlag
    else:
        usedlag = maxlag
        
    resols = sm.OLS(xdshort, np.column_stack([xdall[:,:usedlag+1],trend])).fit()
    #NOTE: should be usedlag+1 since the first column is the level?
    adfstat = resols.t(0)
#    adfstat = (resols.params[0]-1.0)/resols.bse[0]
# the "asymptotically correct" z statistic is obtained as 
# nobs/(1-np.sum(resols.params[1:-(trendorder+1)])) (resols.params[0] - 1)
# I think this is the statistic that is used for series that are integrated
# for orders higher than I(1), ie., not ADF but cointegration tests.

    # Get approx p-value and critical values
    pvalue = mackinnonp(adfstat, regression=regression, N=1)
    critvalues = mackinnoncrit(N=1, regression=regression, nobs=nobs)
    critvalues = {"1%" : critvalues[0], "5%" : critvalues[1],
            "10%" : critvalues[2]}
    if store:
        resstore.resols = resols
        resstore.usedlag = usedlag
        resstore.adfstat = adfstat
        resstore.critvalues = critvalues
        resstore.H0 = "The coefficient on the lagged level equals 1"
        resstore.HA = "The coefficient on the lagged level < 1"
        return adfstat, pvalue, critvalues, resstore
    else:
        return adfstat, usedlag, pvalue, critvalues

def acovf(x, unbiased=False, demean=True):
    ''' 
    Autocovariance for 1D
    
    Parameters
    ----------
    x : array
       time series data
    unbiased : boolean
       if True, then denominators is n-k, otherwise n 
       
    Returns
    -------
    acovf : array
        autocovariance function

    Notes
    -----
    This uses np.correlate which does full convolution. For very long time
    series it is recommended to use fft convolution instead.
    
    '''
    n = len(x)
    if demean:
        xo = x - x.mean();
    else:
        xo = x
    if unbiased:
        xi = np.ones(n);
        d = np.correlate(xi, xi, 'full')
    else:
        d = n
    return (np.correlate(xo, xo, 'full') / d)[n-1:]

#eye-balled vs stata.  compare to Josef's Ljung Box
def boxpierce(x,nobs):
    """
    Return's Box-Pierce Q Statistic.

    x : array-like
        Array of autocorrelation coefficients

    Returns
    -------
    q-stat : array
        Q-statistic for autocorrelation parameters
    p-value : array
        P-value of the Q statistic

    Notes
    ------
    Written to be used with acf.
    """
    x = np.asarray(x)
    ret = nobs*(nobs+2)*np.cumsum((1./(nobs-np.arange(1,
        len(x)+1)))*x**2)
    chi2 = stats.chi2.sf(ret,np.arange(1,len(x)+1))
    return ret,chi2

#NOTE: Changed unbiased to False
#see for example
# http://www.itl.nist.gov/div898/handbook/eda/section3/autocopl.htm
def acf(x, unbiased=False, nlags=40, confint=None):
    '''
    Autocorrelation function for 1d arrays.
    
    Parameters
    ----------
    x : array
       Time series data
    unbiased : bool
       If True, then denominators for autocovariance are n-k, otherwise n
    nlags: int, optional
        Number of lags to return autocorrelation for.
    confint : float or None, optional
        If True, the confidence intervals for the given level are returned.
        For instance if confint=95, 95 % confidence intervals are returned.

    Returns
    -------
    acf : array
        autocorrelation function
    confint : array, optional
        Confidence intervals for the ACF. Returned if confint != None.

    Notes
    -----
    The acf at lag 0 is *not* returned.

    This is based np.correlate which does full convolution. For very long time
    series it is recommended to use fft convolution instead.

    If unbiased is true, the denominator for the autocovariance is adjusted
    but the autocorrelation is not an unbiased estimtor. 
    '''
    
    avf = acovf(x, unbiased=unbiased, demean=True)
    acf = np.take(avf/avf[0], range(1,nlags+1))
    if not confint:
        return acf
    if confint:
# Based on Bartlett's formula for MA(q) processes
# var(rho) = 1/n for v = 1
#          = 1/n * (1+2*np.cumsum(rho**2) for v > 1

        nobs = len(avf)
        varacf = np.ones(nlags)/nobs
#        varacf[1:] *= 1 + 2*np.cumsum(acf[1:]**2)
        varacf[1:] *= 1 + 2*np.cumsum(acf[:-1]**2)
        interval = stats.norm.ppf(1-(100-confint)/200.)*np.sqrt(varacf)
        return acf, np.array(zip(acf-interval, acf+interval)), boxpierce(acf,
                nobs)



def pacorr(X,nlags=40, method="ols"):
    """
    Partial autocorrelation function
    """
    X = np.asarray(X).squeeze()
    nobs = float(len(X))
    if nlags > nobs:
        raise ValueError, "X does not have %s observations" % nlags
    pacf = np.zeros(nlags)
    for i in range(1,nlags+1):
        pacf[i-1] = sm.OLS(X[i:],sm.add_constant(lagmat(X, i, 
            trim="both")[:,1:], prepend=True)).fit().params[-1]
    return pacf

def pacf_yw(x, maxlag=20, method='unbiased'):
    '''Partial autocorrelation estimated with non-recursive yule_walker

    Parameters
    ----------
    x : 1d array
        observations of time series for which pacf is calculated
    maxlag : int
        largest lag for which pacf is returned
    method : 'unbiased' (default) or 'mle'
        method for the autocovariance calculations in yule walker

    Returns
    -------
    pacf : 1d array
        partial autocorrelations, maxlag+1 elements

    Notes
    -----
    This solves yule_walker for each desired lag and contains
    currently duplicate calculations.

    '''
    xm = x - x.mean()
    pacf = [1.]
    for k in range(1, maxlag+1):
        pacf.append(sm.regression.yule_walker(x, k, method=method)[0][-1])
    return np.array(pacf)

def pacf_ols(x, maxlag=20):
    '''Partial autocorrelation estimated with non-recursive OLS

    Parameters
    ----------
    x : 1d array
        observations of time series for which pacf is calculated
    maxlag : int
        largest lag for which pacf is returned

    Returns
    -------
    pacf : 1d array
        partial autocorrelations, maxlag+1 elements

    Notes
    -----
    This solves a separate OLS estimation for each desired lag.
    
    '''
    from scikits.statsmodels.sandbox.tools.tools_tsa import lagmat
    xlags = lagmat(x-x.mean(), maxlag)
    pacfols = [1.]
    for k in range(1, maxlag+1):
        res = sm.OLS(xlags[k:,0], xlags[k:,1:k+1]).fit()
        #print res.params
        pacfols.append(res.params[-1])
    return np.array(pacfols)

def pergram(X, kernel='bartlett', log=True):
    """
    Returns the (log) periodogram for the natural frequency of X

    Parameters
    ----------
    X
    M : int
        Should this be hardcoded?
    kernel : str, optional
    Notes
    -----
    The autocovariances are normalized by len(X).
    The frequencies are calculated as 
    If len(X) is odd M = (len(X) - 1)/2 else M = len(X)/2. Either way
        freq[i] = 2*[i+1]/T and len(freq) == M


    Reference
    ----------
    Based on Lutkepohl; Hamilton.

    Notes
    -----
    Doesn't look right yet.
    """
    X = np.asarray(X).squeeze()
    nobs = len(X)
    M = np.floor(nobs/2.)
    acov = np.zeros(M+1)
    acov[0] = np.var(X)
    Xbar = X.mean()
    for i in range(1,int(M+1)):
        acov[i] = np.dot(X[i:] - Xbar,X[:-i] - Xbar)
    acov /= nobs
    #    #TODO: make a list to check window
#    ell = np.r_[1,np.arange(1,M+1)*np.pi/nobs]
    if kernel == "bartlett":
        w = 1 - np.arange(M+1)/M

#    weights = exec('signal.'+window+'(M='str(M)')')
    j = np.arange(1,M+1)
    ell = np.linspace(0,np.pi,M)
    pergr = np.zeros_like(ell)
    for i,L in enumerate(ell):
        pergr[i] = 1/(2*np.pi)*acov[0] + 2 * np.sum(w[1:]*acov[1:]*np.cos(L*j))
    return pergr

def grangercausalitytests(x, maxlag):
    '''four tests for granger causality of 2 timeseries

    this is a proof-of concept implementation
    not cleaned up, has some duplicate calculations,
    memory intensive - builds full lag array for variables
    prints results
    not verified with other packages,
    all four tests give similar results (1 and 4 identical)
    
    Parameters
    ----------
    x : array, 2d, (nobs,2)
        data for test whether the time series in the second column Granger
        causes the time series in the first column
    maxlag : integer
        the Granger causality test results are calculated for all lags up to
        maxlag
    
    Returns
    -------
    None : no returns
        all test results are currently printed
        
    Notes
    -----
    TODO: convert to function that returns and compare with other packages
    
    '''
    from scipy import stats # lazy import
    import scikits.statsmodels as sm  # absolute import for now
    
    for mlg in range(1, maxlag+1):
        print '\nGranger Causality'
        print 'number of lags (no zero)', mlg
        mxlg = mlg + 1 # Note number of lags starting at zero in lagmat

        # create lagmat of both time series
        dta = lagmat2ds(x, mxlg, trim='both', dropex=1)

        #add constant
        dtaown = sm.add_constant(dta[:,1:mxlg])
        dtajoint = sm.add_constant(dta[:,1:])

        #run ols on both models without and with lags of second variable
        res2down = sm.OLS(dta[:,0], dtaown).fit()
        res2djoint = sm.OLS(dta[:,0], dtajoint).fit()

        #print results
        #for ssr based tests see: http://support.sas.com/rnd/app/examples/ets/granger/index.htm
        #the other tests are made-up

        # Granger Causality test using ssr (F statistic)
        fgc1 = (res2down.ssr-res2djoint.ssr)/res2djoint.ssr/(mxlg-1)*res2djoint.df_resid
        print 'ssr based F test:         F=%-8.4f, p=%-8.4f, df_denom=%d, df_num=%d' % \
              (fgc1, stats.f.sf(fgc1, mxlg-1, res2djoint.df_resid), res2djoint.df_resid, mxlg-1)

        # Granger Causality test using ssr (ch2 statistic)
        fgc2 = res2down.nobs*(res2down.ssr-res2djoint.ssr)/res2djoint.ssr
        print 'ssr based chi2 test:   chi2=%-8.4f, p=%-8.4f, df=%d' %  \
              (fgc2, stats.chi2.sf(fgc2, mxlg-1), mxlg-1)

        #likelihood ratio test pvalue:
        lr = -2*(res2down.llf-res2djoint.llf)
        print 'likelihood ratio test: chi2=%-8.4f, p=%-8.4f, df=%d' %  \
              (lr, stats.chi2.sf(lr, mxlg-1), mxlg-1)

        # F test that all lag coefficients of exog are zero
        rconstr = np.column_stack((np.zeros((mxlg-1,mxlg-1)), np.eye(mxlg-1, mxlg-1),\
                                   np.zeros((mxlg-1, 1))))
        ftres = res2djoint.f_test(rconstr)
        print 'parameter F test:         F=%-8.4f, p=%-8.4f, df_denom=%d, df_num=%d' % \
              (ftres.fvalue, ftres.pvalue, ftres.df_denom, ftres.df_num)



if __name__=="__main__":
    data = sm.datasets.macrodata.load().data
    x = data['realgdp']
# adf is tested now.
#    adf = adfuller(x,4, autolag=None)
    
    acf1,ci1,Q = acf(x, nlags=40, confint=95)

    pacf_ = pacorr(x)
    y = np.random.normal(size=(100,2))
    grangercausalitytests(y,2)

