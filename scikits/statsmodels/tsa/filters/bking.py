import numpy as np
from scipy.signal import fftconvolve

def baxter_king(X, low_freq=6, high_freq=32, K=12):
    """
    Baxter-King bandpass filter

    Parameters
    ----------
    X : array-like
        A 1 or 2d ndarray. If 2d, variables are assumed to be in columns.
    low_freq : int
        Filter frequencies below `low_freq`, ie., Baxter and King suggest that
        the Burns-Mitchell U.S. business cycle has 6 for quarterly data and 
        1.5 for annual data.
    high_freq : int
        Filter frequencies above `high_freq`, ie., the BK suggest that the U.S.
        business cycle has 32 for quarterly data and 8 for annual data.
    K : int
        Maximum lag-length, Baxter and King propose a truncation lag-length
        of 12 for quarterly data and 3 for annual data.

    Returns
    -------
    Y : array
        Cyclical component of X

    References
    ----------
    Baxter, M. and R. G. King. "Measuring Business Cycles: Approximate 
        Band-Pass Filters for Economic Time Series." `Review of Economics and 
        Statistics`, 1999, 81(4), 575-593.
    
    Notes
    -----
    Returns a centered weighted moving average of the original series. Where
    the weights a[j] are computed

    a[j] = b[j] + theta, for j = 0, +/-1, +/-2, ... +/- K
    b[0] = (omega_2 - omega_1)/pi
    b[j] = 1/(pi*j)(sin(omega_2*j)-sin(omega_1*j), for j = +/-1, +/-2,...

    and theta is a normalizing constant

    theta = -sum(b)/(2K+1)

    Examples
    --------
    >>> import scikits.statsmodels.api as sm
    >>> dta = sm.datasets.macrodata.load()
    >>> X = dta.data['realinv']
    >>> Y = sm.tsa.filters.baxter_king(X, 6, 24, 12)
    """
#TODO: allow windowing functions to correct for Gibb's Phenomenon?
# adjust bweights (symmetrically) by below before demeaning
# Lancosz Sigma Factors np.sinc(2*j/(2.*K+1)) 
    if low_freq < 2:
        raise ValueError("low_freq cannot be less than 2")
    X = np.asarray(X)
    omega_1 = 2.*np.pi/high_freq # convert from freq. to periodicity
    omega_2 = 2.*np.pi/low_freq
    bweights = np.zeros(2*K+1)
    bweights[K] = (omega_2 - omega_1)/np.pi # weight at zero freq.
    j = np.arange(1,int(K)+1) 
    weights = 1/(np.pi*j)*(np.sin(omega_2*j)-np.sin(omega_1*j))
    bweights[K+j] = weights # j is an idx
    bweights[:K] = weights[::-1] # make symmetric weights
    bweights -= bweights.mean() # make sure weights sum to zero
    if X.ndim == 2:
        bweights = bweights[:,None]
    return fftconvolve(bweights, X, mode='valid') # get a centered moving avg/
                                                  # convolution
