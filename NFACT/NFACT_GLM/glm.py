import numpy as np
from scipy.special import betainc, erfinv
from scipy.stats import t


# GLM Stuff
class GLM:
    """
    Class to peform regression on

    Usage
    -----
    """

    def __init__(
        self,
    ):
        self.X = None
        self.y = None
        self.beta = None
        self.dof = None
        self.sigma_sq = None
        # self.XtX_ = None

    def fit(self, X: np.array, y: np.array):
        self.X = X
        self.y = y
        self.beta = self.__beta()
        res = self.__residuals()
        self.dof = self.__dof()
        self.sigma_sq_ = self.__sigma_sq(res)
        self.XtX_ = self.__XtX()

    def __XtX(self):
        return self.X.T @ self.X

    def __sigma_sq(self, res):
        return np.sum(res**2, axis=0, keepdims=True) / self.dof

    def __residuals(self):
        return self.y - self.X @ self.beta

    def __dof(self):
        return self.X.shape[0] - np.linalg.matrix_rank(self.X)

    def __beta(self):
        return np.linalg.pinv(self.X) @ self.y

    def results(self, contrast: np.array):
        cope = contrast @ self.beta
        varcope = np.outer(np.diag(contrast @ self.XtX_ @ contrast.T), self.sigma_sq_)
        tstat = self.__t_statistic(cope, varcope)
        pval = self.__pval(tstat)
        return {"tstat": tstat, "pval": pval, "zstat": self.__zstat(tstat, self.dof_)}

    def __t_statistic(self, cope, varcope):
        return cope / np.sqrt(varcope)

    def __pval(self, tstat):
        return 2 * (t.cdf(np.abs(tstat), self.dof))

    def __zstat(self, tstat, dof):
        beta_func = (
            betainc(self.dof / 2.0, 1 / 2, self.dof / (self.dof + tstat**2)) / 2.0
        )
        return (np.sqrt(2) * erfinv(1 - 2 * beta_func)) * np.sign(tstat)

    def fit_transform(self, X, y):
        self.fit(X, y)
        return self.transform(X)

    def transform(self, X):
        if self.beta_ is not None:
            return X @ self.beta_
