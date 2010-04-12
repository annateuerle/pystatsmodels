"""
State Space Analysis using the Kalman Filter

References
-----------
Durbin., J and Koopman, S.J.  `Time Series Analysis by State Space Methods`.
    Oxford, 2001.

Hamilton, J.D.  `Time Series Analysis`.  Princeton, 1994.
"""

from scipy import optimize
from var import chain_dot #TODO: move this to tools

#TODO: split out the loglikelihood part into its own function

def kalmanfilter(F, A, H, Q, R, y, X, xi10, ntrain):
    """

    Parameters
    -----------
    f : array-like
        f is the transition matrix for the hidden state
    h : array-like
        Relates the observable state to the hidden state.
    y : array-like
        Observed data
    x10 : array-like
        Is the initial prior on the initial state vector
    q : array-like
        Variance/Covariance matrix on the error term in the hidden state
    ntrain : int
        The number of training periods for the filter.
    

    Returns
    -------
    likelihood 
        The negatiev of the log likelihood
    history or priors, history of posterior
    
    TODO: change API, update names

    No input checking is done.
    """
# uses log of Hamilton 13.4.1
    F = np.asarray(F)
    H = np.asarray(H)
    y = np.asarray(y)
    A = np.asarray(A)
    if y.ndim == 1: # note that Y is in rows for now
        y = y[:,None]
    nobs = y.shape[0]
    xi10 = np.asarray(xi10)
    if xi10.ndim == 1:
        xi10[:,None]
#    if history is True:
#        state_vector = [xi10]
#        forecast_vector = []
#        update_history = lambda x : x
    Q = np.asarray(Q)
    r = xi10.shape[0]
# Eq. 12.2.21, other version says P0 = Q
#    p10 = np.dot(np.linalg.inv(np.eye(r**2)-np.kron(F,F)),Q.ravel('F')) 
#    p10 = np.reshape(P0, (r,r), order='F')

# Assume a fixed, known intial point and set P0 = Q?
# this one doesn't take as long and gets "closer" to the answer.
    p10 = Q

    loglikelihood = 0
    for i in range(nobs):
        if i > ntrain:
            HTPHR = chain_dot(H.T,p10,H)+R
            if HTPHR.ndim == 1:
                HTPHRinv = 1./HTPHR
            else:
                HTPHRinv = np.linalg.inv(HTPHR)
    #        FPH = chain_dot(F,P,H)
            part1 = y[i] - np.dot(A.T,X) - np.dot(H.T,xi10)
            HTPHRdet = np.linalg.det(HTPHR)
            part2 = -.5*chain_dot(part1.T,HTPHRinv,part1)
# I don't think these values can ever be returned.  There will be another
# error.  Need to test with ill-conditioned problem.
#            if HTPHRdet > 10e-300: # not singular
            loglike_interm = (-nobs/2.) * np.log(2*np.pi) - .5*\
                        np.log(HTPHRdet) + part2
#                if loglike_interm > 10e300:
#                    raise ValueError("""There was an error in forming likelihood.
#Derivative term is greater than 10e300.""")
            loglikelihood += loglike_interm

            # 13.2.15 Update linear project, guess xi now based on y
            xi11 = xi10 + chain_dot(p10, H, HTPHRinv, part1)
            # 13.2.16 MSE of that update projection
            p11 = p10 - chain_dot(p10, H, HTPHRinv, H.T, p10)
            # 13.2.17 Update forecast about xi based on our guess of F
            xi10 = np.dot(F,xi11)
            # 13.2.21 Update the MSE of the forecast
            p10 = chain_dot(F,p11,F.T) + Q
    return -loglikelihood 

# The below is Luca's version
#    n = H.shape[1]
#    nobs = y.shape[1]
#    if history == False:
#        xi10History = xi10
#        xi11History = xi10History

#    p10 = q # eq 13.2.21
#    loglikelihood = 0

#    for i in range(nobs):
#        hP_p10_h = np.linalg.inv(chain_dot(h.T,p10,h))
#        part1 = y[:,i] - np.dot(h.T,xi10History)
        
        # after training, don't throw this away
#        if i > ntrain:
#            part2 = -0.5 * chain_dot(part1.T,hP_p10_h,part1)
#            det_hpp10h = np.linalg.det(chain_dot(h.T,p10,h))
#            if det_hpp10h > 10e-300: # not singular
#                loglike_int = (-n/2.)*np.log(2*np.pi)-.5*np.log(det_hpp10h)+part2
#                if loglike_int > 10e300:
#                    raise ValueError("There was an error in forming likelihood")
#                loglikelihood += loglike_int

        # 13.2.15
#        xi11History = xi10History + chain_dot(p10,h,hP_p10_h,
#                part1)
        # 13.2.16   

#        p11 = p10 - chain_dot(p10,h,hP_p10_h,h.T,p10)
        # 13.2.17
#        xi10History = np.dot(f,xi11History)
        # 13.2.21
#        p10 = chain_dot(f,p11,f.T) + q
#    return -loglikelihood

#TODO: make a state space model
class StateSpaceModel(object):
    def __init__(self, endog, exog=None):
        """
        Parameters
        ----------
        endog : array-like
            A (nobs x n) array of observations.
        exog : array-like, optional
            A (nobs x k) array of covariates.

        Notes
        -----
        exog are not handled right now.
        Created with a (V)ARMA in mind.
        """
        endog = np.asarray(endog)
        if endog.ndim == 1:
            endog = endog[:,None]
        self.endog = endog
        n = endog.shape[1]
        self.n = n
        self.nobs = endog.shape[0]
        self.exog = exog
#        xi10 = np.ararray(xi10)
#        if xi10.ndim == 1:
#            xi10 = xi10[:,None]
#        self.xi10 = xi10
#        self.ntrain = ntrain
#        self.p = ARMA[0]
#        self.q = ARMA[1]
#        self.pq = max(ARMA)
#        self.r = xi10.shape[1]
#        self.A = A
#        self.Q = Q
#        self.F = F
#        self.Hmat =
#        if n == 1:
#            F = 
#        self._updatematrices(start_params)

    def _updateloglike(self, params, ntrain, penalty, upperbounds, lowerbounds, 
            F,A,H,Q,R):  
        """
        """
        paramsorig = params
        # are the bounds binding?
        params = np.min((np.max((lowerbounds, params), axis=0),upperbounds),
                axis=0)
        #TODO: does it make sense for all of these to be allowed to be None?
        if F != None and callable(F):
            F = F(params)
        elif F == None:
            F = 0
        if A != None and callable(A):
            A = A(params)
        elif A == None:
            A = 0
        if H != None and callable(H):
            H = H(params)
        elif H == None:
            H = 0
        if Q != None and callable(Q):
            Q = Q(params)
        elif Q == None:
            Q = 0
        if R != None and callable(R):
            R = R(params)
        elif R == None:
            R = 0
        X = self.exog
        if X == None:
            X = 0
        y = self.endog
        loglike = kalmanfilter(F,A,H,Q,R,y,X, xi10, ntrain)
        # use a quadratic penalty function to move away from bounds
        loglike += penalty * np.sum((paramsorig-params)**2)
        return loglike
        
#        r = self.r
#        n = self.n
#        F = np.diagonal(np.ones(r-1), k=-1) # think this will be wrong for VAR
                                            # cf. 13.1.22 but think VAR
#        F[0] = params[:p] # assumes first p start_params are coeffs
                                # of obs. vector, needs to be nxp for VAR?
#        self.F = F
#        cholQ = np.diag(start_params[p:]) # fails for bivariate
                                                        # MA(1) section
                                                        # 13.4.2
#        Q = np.dot(cholQ,cholQ.T)
#        self.Q = Q
#        HT = np.zeros((n,r))
#        xi10 = self.xi10
#        y = self.endog
#        ntrain = self.ntrain
 #       loglike = kalmanfilter(F,H,y,xi10,Q,ntrain)

    def fit_kalman(self, start_params, ntrain=1, F=None, A=None, H=None, Q=None, 
            R=None, method="bfgs", penalty=True, upperbounds=None, 
            lowerbounds=None):
        """
        Parameters
        ----------
        method : str
            Only "bfgs" is currently accepted.
        start_params : array-like
            The first guess on all parameters to be estimated.  This can
            be in any order as long as the F,A,H,Q, and R functions handle
            the parameters appropriately.
        xi10 : arry-like
            The (r x 1) vector of initial states.  See notes.
        F,A,H,Q,R : functions or array-like, optional
            If functions, they should take start_params (or the current
            value of params during iteration and return the F,A,H,Q,R matrices).
            See notes.  If they are constant then can be given as array-like 
            objects.  If not included in the state-space representation then
            can be left as None.  See example in class docstring.
        penalty : bool,
            Whether or not to include a penalty for solutions that violate
            the bounds given by `lowerbounds` and `upperbounds`.
        lowerbounds : array-like
            Lower bounds on the parameter solutions.  Expected to be in the 
            same order as `start_params`.
        upperbounds : array-like
            Upper bounds on the parameter solutions.  Expected to be in the 
            same order as `start_params`
        """
        y = self.endog
#        xi10 = self.xi10
#        Q = self.Q
        ntrain = ntrain
        _updateloglike = self._updateloglike
        params = start_params
        if method.lower() == 'bfgs':
            results = optimize.fmin_bfgs(_updateloglike, params, 
                    args = (ntrain, penalty, upperbounds, lowerbounds,
                        F,A,H,Q,R), gtol= 1e-8, epsilon=1e-10)
            #TODO: provide more options to user for optimize
        self.params = results



def updatematrices(params, y, xi10, ntrain, penalty, upperbound, lowerbound):
    """
    TODO: change API, update names

    This isn't general
    """
    paramsorig = params
    # are the bounds binding?
    params = np.min((np.max((lowerbound,params),axis=0),upperbound), axis=0)
    rho = params[0]
    sigma1 = params[1]
    sigma2 = params[2]

    F = np.array([[rho, 0],[0,0]])
    cholQ = np.array([[sigma1,0],[0,sigma2]])
    H = np.ones((2,1))
    q = np.dot(cholQ,cholQ.T)
    loglike = kalmanfilter(F,0,H,q,0, y, 0, xi10, ntrain)
    loglike = loglike + penalty*np.sum((paramsorig-params)**2)
    return loglike


if __name__ == "__main__":
    import numpy as np
    # Make our observations as in 13.1.13
    np.random.seed(54321)
    nobs = 600
    y = np.zeros(nobs)
    rho = [.5, -.25, .35, .25]
    sigma = 2.0 # std dev. or noise
    for i in range(4,nobs):
        y[i] = np.dot(rho,y[i-4:i][::-1]) + np.random.normal(scale=sigma)
    y = y[100:]

    # make an MA(2) observation equation as in example 13.3
    # y = mu + [1 theta][e_t e_t-1]'
    mu = 2.
    theta = .8
    rho = np.array([1, theta])
    np.random.randn(54321)
    e = np.random.randn(101)
    y = mu + rho[0]*e[1:]+rho[1]*e[:-1]
    # might need to add an axis
    r = len(rho)
    x = np.ones_like(y)
    
    # For now, assume that F,Q,A,H, and R are known 
    F = np.array([[0,0],[1,0]])
    Q = np.array([[1,0],[0,0]])
    A = np.array([mu])
    H = rho[:,None]
    R = 0
    
    # remember that the goal is to solve recursively for the
    # state vector, xi, given the data, y (in this case)
    # we can also get a MSE matrix, P, associated with *each* observation

    # given that our errors are ~ NID(0,variance)
    # the starting E[e(1),e(0)] = [0,0]
    xi0 = np.array([[0],[0]])
    # with variance = 1 we know that 
#    P0 = np.eye(2)  # really P_{1|0}

# Using the note below
    P0 = np.dot(np.linalg.inv(np.eye(r**2)-np.kron(F,F)),Q.ravel('F')) 
    P0 = np.reshape(P0, (r,r), order='F')

    # more generally, if the eigenvalues for F are in the unit circle 
    # (watch out for rounding error in LAPACK!) then
    # the DGP of the state vector is var/cov stationary, we know that
    # xi0 = 0
    # Furthermore, we could start with
    # vec(P0) = np.dot(np.linalg.inv(np.eye(r**2) - np.kron(F,F)),vec(Q))
    # where vec(X) = np.ravel(X, order='F') with a possible [:,np.newaxis]
    # if you really want a "2-d" array
    # a fortran (row-) ordered raveled array
    # If instead, some eigenvalues are on or outside the unit circle
    # xi0 can be replaced with a best guess and then 
    # P0 is a positive definite matrix repr the confidence in the guess
    # larger diagonal elements signify less confidence


    # we also know that y1 = mu
    # and MSE(y1) = variance*(1+theta**2) = np.dot(np.dot(H.T,P0),H)

    state_vector = [xi0]
    forecast_vector = [mu]
    MSE_state = [P0]    # will be a list of matrices
    MSE_forecast = []
    # must be numerical shortcuts for some of this...
    # this should be general enough to be reused
    for i in range(len(y)-1):
        # update the state vector
        sv = state_vector[i]
        P = MSE_state[i]
        HTPHR = np.dot(np.dot(H.T,P),H)+R
        if np.ndim(HTPHR) < 2: # we have a scalar
            HTPHRinv = 1./HTPHR
        else:
            HTPHRinv = np.linalg.inv(HTPHR)
        FPH = np.dot(np.dot(F,P),H)
        gain_matrix = np.dot(FPH,HTPHRinv)  # correct
        new_sv = np.dot(F,sv)
        new_sv += np.dot(gain_matrix,y[i] - np.dot(A.T,x[i]) -
                np.dot(H.T,sv))
        state_vector.append(new_sv)
        # update the MSE of the state vector forecast using 13.2.28
        new_MSEf = np.dot(np.dot(F - np.dot(gain_matrix,H.T),P),F.T - np.dot(H,
            gain_matrix.T)) + np.dot(np.dot(gain_matrix,R),gain_matrix.T) + Q
        MSE_state.append(new_MSEf)
        # update the in sample forecast of y
        forecast_vector.append(np.dot(A.T,x[i+1]) + np.dot(H.T,new_sv))
        # update the MSE of the forecast
        MSE_forecast.append(np.dot(np.dot(H.T,new_MSEf),H) + R)
    MSE_forecast = np.array(MSE_forecast).squeeze()
    MSE_state = np.array(MSE_state)
    forecast_vector = np.array(forecast_vector)
    state_vector = np.array(state_vector).squeeze()

##########
#    Luca's example
    # choose parameters governing the signal extraction problem
    rho = .9
    sigma1 = 1
    sigma2 = 1
    nobs = 100

# get the state space representation (Hamilton's notation)\
    F = np.array([[rho, 0],[0, 0]])
    cholQ = np.array([[sigma1, 0],[0,sigma2]])
    H = np.ones((2,1))

# generate random data
    np.random.seed(12345)
    xihistory = np.zeros((2,nobs))
    for i in range(1,nobs):
        xihistory[:,i] = np.dot(F,xihistory[:,i-1]) + \
                np.dot(cholQ,np.random.randn(2,1)).squeeze() 
                # this makes an ARMA process?
                # check notes, do the math
    y = np.dot(H.T, xihistory)
    y = y.T

    params = np.array([rho, sigma1, sigma2])
    penalty = 1e5
    upperbounds = np.array([.999, 100, 100])
    lowerbounds = np.array([-.999, .001, .001])
    xi10 = xihistory[:,0]
    ntrain = 1
    bounds = zip(lowerbounds,upperbounds) # if you use fmin_l_bfgs_b
    results = optimize.fmin_bfgs(updatematrices, params, 
        args=(y,xi10,ntrain,penalty,upperbounds,lowerbounds),
        gtol = 1e-8, epsilon=1e-10)
#    array([ 0.83111567,  1.2695249 ,  0.61436685])


    F = lambda x : np.array([[x[0],0],[0,0]])
    def Q(x):
        cholQ = np.array([[x[1],0],[0,x[2]]])
        return np.dot(cholQ,cholQ.T)
    H = np.ones((2,1))
    ssm_model = StateSpaceModel(y)
    ssm_model.fit_kalman(start_params=params, F=F, Q=Q, H=H, 
            upperbounds=upperbounds, lowerbounds=lowerbounds)
# why does the above take 3 times as many iterations?


