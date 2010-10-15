"""Linear Model with Student-t distributed errors


Created on 2010-09-24
Author: josef-pktd
License: BSD

TODO
----
* add starting values based on OLS
* bugs: store_params doesn't seem to be defined, I think this was a module
        global for debugging - commented out
* parameter restriction: check whether version with some fixed parameters works
  

"""
#mostly copied from the examples directory written for trying out generic mle.

import numpy as np
from scipy import special #, stats
#redefine some shortcuts
np_log = np.log
np_pi = np.pi
sps_gamln = special.gammaln


from scikits.statsmodels.model import GenericLikelihoodModel

class TLinearModel(GenericLikelihoodModel):
    '''Maximum Likelihood Estimation of Linear Model with t-distributed errors
    
    This is an example for generic MLE.
    
    Except for defining the negative log-likelihood method, all
    methods and results are generic. Gradients and Hessian
    and all resulting statistics are based on numerical
    differentiation.
    
    '''

    
    def loglike(self, params):
        return -self.nloglikeobs(params).sum(0)
    
    def nloglikeobs(self, params):
        """
        Loglikelihood of linear model with t distributed errors. 

        Parameters
        ----------
        params : array
            The parameters of the model. The last 2 parameters are degrees of
            freedom and scale. 

        Returns
        -------
        loglike : array, (nobs,)
            The log likelihood of the model evaluated at `params` for each
            observation defined by self.endog and self.exog.

        Notes
        -----
        .. math :: \\ln L=\\sum_{i=1}^{n}\\left[-\\lambda_{i}+y_{i}x_{i}^{\\prime}\\beta-\\ln y_{i}!\\right]

        The t distribution is the standard t distribution and not a standardized
        t distribution, which means that the scale parameter is not equal to the
        standard deviation.

        self.fixed_params and self.expandparams can be used to fix some
        parameters. (I doubt this has been tested in this model.)
        
        """
        #print len(params),
        #store_params.append(params)
        if not self.fixed_params is None:
            #print 'using fixed'
            params = self.expandparams(params)
            
        beta = params[:-2]
        df = params[-2]
        scale = params[-1]
        loc = np.dot(self.exog, beta)
        endog = self.endog
        x = (endog - loc)/scale
        #next part is stats.t._logpdf
        lPx = sps_gamln((df+1)/2) - sps_gamln(df/2.)
        lPx -= 0.5*np_log(df*np_pi) + (df+1)/2.*np_log(1+(x**2)/df)
        lPx -= np_log(scale)  # correction for scale
        return -lPx
