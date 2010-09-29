'''Testing GenericLikelihoodModel variations on Poisson


'''
import numpy as np
from numpy.testing import assert_almost_equal
import scikits.statsmodels as sm
from scikits.statsmodels.miscmodels import PoissonGMLE, PoissonOffsetGMLE, \
                        PoissonZiGMLE

DEC = 1

class Compare(object):

    def test_params(self):
        assert_almost_equal(self.res.params, self.res_glm.params, DEC)
        assert_almost_equal(self.res.params, self.res_discrete.params, DEC)
        
    def test_cov_params(self):
        assert_almost_equal(self.res.bse, self.res_glm.bse, DEC)
        assert_almost_equal(self.res.bse, self.res_discrete.bse, DEC)
        assert_almost_equal(self.res.tval, self.res_glm.t(), DEC)
        #assert_almost_equal(self.res.params, self.res_discrete.params)


class TestPoissonMLE(Compare):
    
    def __init__(self):
        
        # generate artificial data
        np.random.seed(98765678)
        nobs = 200
        rvs = np.random.randn(nobs,6)
        data_exog = rvs
        data_exog = sm.add_constant(data_exog)
        xbeta = 1 + 0.1*rvs.sum(1)
        data_endog = np.random.poisson(np.exp(xbeta))
        
        #estimate generic MLE
        self.mod = PoissonGMLE(data_endog, data_exog)
        self.res = self.mod.fit()
        
        #estimate discretemod.Poisson as benchmark
        from scikits.statsmodels.discretemod import Poisson
        self.res_discrete = Poisson(data_endog, data_exog).fit()
        
        mod_glm = sm.GLM(data_endog, data_exog, family=sm.families.Poisson())
        self.res_glm = mod_glm.fit()

        
class TestPoissonOffset(Compare):
    def __init__(self):
        
        # generate artificial data
        np.random.seed(98765678)
        nobs = 200
        rvs = np.random.randn(nobs,6)
        data_exog = rvs
        data_exog = sm.add_constant(data_exog)
        xbeta = 1 + 0.1*rvs.sum(1)
        data_endog = np.random.poisson(np.exp(xbeta))
        
        #estimate generic MLE
        self.mod = PoissonGMLE(data_endog, data_exog)
        res = self.mod.fit()
        offset = res.params[0] * data_exog[:,0]  #1d ???
        #self.res = PoissonOffsetGMLE(data_endog, data_exog[:,1:], offset=offset).fit(start_params = np.ones(6)/2., method='nm')
        self.res = PoissonOffsetGMLE(data_endog, data_exog[:,1:], offset=offset).fit(start_params = 0.9*res.params[1:], method='nm')
        
        #estimate discretemod.Poisson as benchmark
        from scikits.statsmodels.discretemod import Poisson
        self.res_discrete = Poisson(data_endog, data_exog).fit()
        
        mod_glm = sm.GLM(data_endog, data_exog, family=sm.families.Poisson())
        self.res_glm = mod_glm.fit()
        
    def test_params(self):
        assert_almost_equal(self.res.params, self.res_glm.params[1:], DEC)
        assert_almost_equal(self.res.params, self.res_discrete.params[1:], DEC)
        
    def test_cov_params(self):
        assert_almost_equal(self.res.bse, self.res_glm.bse[1:], DEC)
        assert_almost_equal(self.res.bse, self.res_discrete.bse[1:], DEC)
        assert_almost_equal(self.res.tval, self.res_glm.t()[1:], DEC)
        #assert_almost_equal(self.res.params, self.res_discrete.params)
  
class TestPoissonZi(Compare):
    def __init__(self):
        
        # generate artificial data
        np.random.seed(98765678)
        nobs = 200
        rvs = np.random.randn(nobs,6)
        data_exog = rvs
        data_exog = sm.add_constant(data_exog)
        xbeta = 1 + 0.1*rvs.sum(1)
        data_endog = np.random.poisson(np.exp(xbeta))
        
        #estimate generic MLE
        self.mod = PoissonGMLE(data_endog, data_exog)
        res = self.mod.fit()
        offset = res.params[0] * data_exog[:,0]  #1d ???
        self.res = PoissonZiGMLE(data_endog, data_exog[:,1:],offset=offset).fit(start_params = np.r_[np.ones(6)/2.,10], method='nm')
        
        #estimate discretemod.Poisson as benchmark
        from scikits.statsmodels.discretemod import Poisson
        self.res_discrete = Poisson(data_endog, data_exog).fit()
        
        mod_glm = sm.GLM(data_endog, data_exog, family=sm.families.Poisson())
        self.res_glm = mod_glm.fit()
        
        self.decimal = 1

    def test_params(self):
        assert_almost_equal(self.res.params[:-1], self.res_glm.params[1:], self.decimal)
        assert_almost_equal(self.res.params[:-1], self.res_discrete.params[1:], self.decimal)
        
    def test_cov_params(self):
        assert_almost_equal(self.res.bse[:-1], self.res_glm.bse[1:], self.decimal)
        assert_almost_equal(self.res.bse[:-1], self.res_discrete.bse[1:], self.decimal)
        assert_almost_equal(self.res.tval[:-1], self.res_glm.t()[1:], self.decimal)




