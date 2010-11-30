import numpy as np
from numpy.testing import assert_almost_equal
import scikits.statsmodels.sandbox.tsa.fftarma as fa
#from scikits.statsmodels.tsa.descriptivestats import TsaDescriptive
from scikits.statsmodels.tsa.arma_mle import Arma
from scikits.statsmodels.tsa.arima import ARMA
from results import results_arma


DECIMAL_4 = 4

y_arma = np.genfromtxt('./results/y_arma_data.csv', delimiter=",", 
        skip_header=1, dtype=float)


def test_compare_arma():
    #this is a preliminary test to compare arma_kf, arma_cond_ls and arma_cond_mle
    #the results returned by the fit methods are incomplete
    #for now without random.seed
    
    #np.random.seed(9876565)
    x = fa.ArmaFft([1, -0.5], [1., 0.4], 40).generate_sample(size=200, burnin=1000)

# this used kalman filter through descriptive
#    d = ARMA(x)
#    d.fit((1,1), trend='nc')
#    dres = d.res
    
    from scikits.statsmodels.tsa.arima import ARMA
    modkf = ARMA(x)
    ##rkf = mkf.fit((1,1))
    ##rkf.params
    reskf = modkf.fit((1,1), trend='nc')
    dres = reskf

    modc = Arma(x)
    resls = modc.fit(order=(1,1))
    rescm = modc.fit_mle(order=(1,1), start_params=[0.4,0.4, 1.])

    #decimal 1 corresponds to threshold of 5% difference
    #still different sign  corrcted
    #assert_almost_equal(np.abs(resls[0] / d.params), np.ones(d.params.shape), decimal=1)
    assert_almost_equal(resls[0] / dres.params, np.ones(dres.params.shape), decimal=1)
    #rescm also contains variance estimate as last element of params
    
    #assert_almost_equal(np.abs(rescm.params[:-1] / d.params), np.ones(d.params.shape), decimal=1)
    assert_almost_equal(rescm.params[:-1] / dres.params, np.ones(dres.params.shape), decimal=1)
    #return resls[0], d.params, rescm.params

class CheckArmaResults(object):
    """
    res2 are the results from gretl.  They are in results/results_arma.
    res1 are from statsmodels
    """
    def test_params(self):
        assert_almost_equal(self.res1.params, self.res2.params, DECIMAL_4)

    def test_aic(self):
        assert_almost_equal(self.res1.aic, self.res2.aic, DECIMAL_4)

    def test_bic(self):
        assert_almost_equal(self.res1.bic, self.res2.bic, DECIMAL_4)

    def test_arroots(self):
        assert_almost_equal(self.res1.arroots, self.res2.arroots, DECIMAL_4)

    def test_maroots(self):
        assert_almost_equal(self.res1.maroots, self.res2.maroots, DECIMAL_4)

    def test_bse(self):
        assert_almost_equal(self.res1.bse, self.res2.bse, DECIMAL_4)

    def test_covparams(self):
        assert_almost_equal(self.res1.cov_params(), self.res2.cov_params, 
                DECIMAL_4)

    def test_hqic(self):
        assert_almost_equal(self.res1.hqic, self.res2.hqic, DECIMAL_4)

    def test_llf(self):
        assert_almost_equal(self.res1.llf, self.res2.llf, DECIMAL_4)

    def test_resid(self):
        assert_almost_equal(self.res1.resid, self.res2.resid, DECIMAL_4)

    def test_fittedvalues(self):
        assert_almost_equal(self.res1.fittedvalues, self.res2.fittedvalues, 
                DECIMAL_4)

    def test_pvalues(self):
        assert_almost_equal(self.res1.pvalues, self.res2.pvalues, DECIMAL_4)

    def test_tvalues(self):
        assert_almost_equal(self.res1.t(), self.res2.tvalues, DECIMAL_4)

    def test_sigma2(self):
        assert_almost_equal(self.res1.sigma2, self.res2.sigma2, DECIMAL_4)


class Test_Y_ARMA11_NoConst(CheckArmaResults):
    def __init__(self):
        endog = y_arma[:,0]
        self.res1 = ARMA(endog).fit(order=(1,1))
        self.res2 = results_arma.Y_arma11()

#class Test_Y_ARMA14_NoConst(CheckArmaResults):
#    def __init__(self):
#        endog = y_arma[:,1]
#        self.res1 = ARMA(endog).fit(order=(1,4))
#        self.res2 = results_arma.Y_arma14()
#
#
#
#class Test_Y_ARMA41_NoConst(CheckArmaResults):
#    def __init__(self):
#        endog = y_arma[:,2]
#        self.res1 = ARMA(endog).fit(order=(4,1))
#        self.res2 = results_arma.Y_arma41()
#
#
#
#class Test_Y_ARMA22_NoConst(CheckArmaResults):
#    def __init__(self):
#        endog = y_arma[:,3]
#        self.res1 = ARMA(endog).fit(order=(2,2))
#        self.res2 = results_arma.Y_arma22()
#
#
#
#class Test_Y_ARMA50_NoConst(CheckArmaResults):
#    def __init__(self):
#        endog = y_arma[:,4]
#        self.res1 = ARMA(endog).fit(order=(5,0))
#        self.res2 = results_arma.Y_arma50()
#
#
#
#class Test_Y_ARMA02_NoConst(CheckArmaResults):
#    def __init__(self):
#        endog = y_arma[:,5]
#        self.res1 = ARMA(endog).fit(order=(0,2))
#        self.res2 = results_arma.Y_arma02()
#
#
#
#class Test_Y_ARMA11_Const(CheckArmaResults):
#    def __init__(self):
#        endog = y_arma[:,6]
#        self.res1 = ARMA(endog).fit(order=(1,1), trend="c")
#        self.res2 = results_arma.Y_arma11c()
#
#
#
#class Test_Y_ARMA14_Const(CheckArmaResults):
#    def __init__(self):
#        endog = y_arma[:,7]
#        self.res1 = ARMA(endog).fit(order=(1,4), trend="c")
#        self.res2 = results_arma.Y_arma14c()
#
#
#
#class Test_Y_ARMA41_Const(CheckArmaResults):
#    def __init__(self):
#        endog = y_arma[:,8]
#        self.res1 = ARMA(endog).fit(order=(4,1), trend="c")
#        self.res2 = results_arma.Y_arma41c()
#
#
#
#class Test_Y_ARMA22_Const(CheckArmaResults):
#    def __init__(self):
#        endog = y_arma[:,9]
#        self.res1 = ARMA(endog).fit(order=(2,2), trend="c")
#        self.res2 = results_arma.Y_arma22c()
#
#
#
#class Test_Y_ARMA50_Const(CheckArmaResults):
#    def __init__(self):
#        endog = y_arma[:,10]
#        self.res1 = ARMA(endog).fit(order=(5,0), trend="c")
#        self.res2 = results_arma.Y_arma50c()
#
#
#
#class Test_Y_ARMA02_Const(CheckArmaResults):
#    def __init__(self):
#        endog = y_arma[:,11]
#        self.res1 = ARMA(endog).fit(order=(0,2), trend="c")
#        self.res2 = results_arma.Y_arma02c()
#
#
#class Test_Y_ARMA11_NoConst_CSS(CheckArmaResults):
#    def __init__(self):
#        endog = y_arma[:,0]
#        self.res1 = ARMA(endog).fit(order=(1,1), method="css")
#        self.res2 = results_arma.Y_arma11("css")
#
#
#class Test_Y_ARMA14_NoConst_CSS(CheckArmaResults):
#    def __init__(self):
#        endog = y_arma[:,1]
#        self.res1 = ARMA(endog).fit(order=(1,4), method="css")
#        self.res2 = results_arma.Y_arma14("css")
#
#
#
#class Test_Y_ARMA41_NoConst_CSS(CheckArmaResults):
#    def __init__(self):
#        endog = y_arma[:,2]
#        self.res1 = ARMA(endog).fit(order=(4,1), method="css")
#        self.res2 = results_arma.Y_arma41("css")
#
#
#
#class Test_Y_ARMA22_NoConst_CSS(CheckArmaResults):
#    def __init__(self):
#        endog = y_arma[:,3]
#        self.res1 = ARMA(endog).fit(order=(2,2), method="css")
#        self.res2 = results_arma.Y_arma22("css")



#class Test_Y_ARMA50_NoConst_CSS(CheckArmaResults):
#    def __init__(self):
#        endog = y_arma[:,4]
#        self.res1 = ARMA(endog).fit(order=(5,0), method="css")
#        self.res2 = results_arma.Y_arma50("css")
#
#
#
#class Test_Y_ARMA02_NoConst_CSS(CheckArmaResults):
#    def __init__(self):
#        endog = y_arma[:,5]
#        self.res1 = ARMA(endog).fit(order=(0,2), method="css")
#        self.res2 = results_arma.Y_arma02("css")
#
#
#
#class Test_Y_ARMA11_Const_CSS(CheckArmaResults):
#    def __init__(self):
#        endog = y_arma[:,6]
#        self.res1 = ARMA(endog).fit(order=(1,1), trend="c", method="css")
#        self.res2 = results_arma.Y_arma11c("css")
#
#
#
#class Test_Y_ARMA14_Const_CSS(CheckArmaResults):
#    def __init__(self):
#        endog = y_arma[:,7]
#        self.res1 = ARMA(endog).fit(order=(1,4), trend="c", method="css")
#        self.res2 = results_arma.Y_arma14c("css")
#
#
#
#class Test_Y_ARMA41_Const_CSS(CheckArmaResults):
#    def __init__(self):
#        endog = y_arma[:,8]
#        self.res1 = ARMA(endog).fit(order=(4,1), trend="c", method="css")
#        self.res2 = results_arma.Y_arma41c("css")
#
#
#
#class Test_Y_ARMA22_Const_CSS(CheckArmaResults):
#    def __init__(self):
#        endog = y_arma[:,9]
#        self.res1 = ARMA(endog).fit(order=(2,2), trend="c", method="css")
#        self.res2 = results_arma.Y_arma22c("css")
#
#
#
#class Test_Y_ARMA50_Const_CSS(CheckArmaResults):
#    def __init__(self):
#        endog = y_arma[:,10]
#        self.res1 = ARMA(endog).fit(order=(5,0), trend="c", method="css")
#        self.res2 = results_arma.Y_arma50c("css")
#
#
#
#class Test_Y_ARMA02_Const_CSS(CheckArmaResults):
#    def __init__(self):
#        endog = y_arma[:,11]
#        self.res1 = ARMA(endog).fit(order=(0,2), trend="c", method="css")
#        self.res2 = results_arma.Y_arma02c("css")

if __name__ == "__main__":
    import nose
    nose.runmodule(argv=[__file__, '-vvs', '-x', '--pdb'], exit=False)
