import numpy as np
from scipy.special import betainc, erfinv
from scipy.stats import t


# GLM Stuff
class GLM:
    def __init__(self):
        self.beta_ = None
        self.res_ = None
        self.dof_ = None
        self.sigma_sq_ = None
        self.XtX_ = None

    def fit(self, X, y):
        self.beta_ = np.linalg.pinv(X) @ y
        self.res_ = y - X @ self.beta_
        self.dof_ = self.res_.shape[0] - np.linalg.matrix_rank(X)
        self.sigma_sq_ = np.sum(self.res_**2, axis=0, keepdims=True) / self.dof_
        self.XtX_ = X.T @ X

    def calc_stats(self, C):
        if self.beta_ is not None:
            C = np.array(C)
            cope = C @ self.beta_
            varcope = np.outer(np.diag(C @ self.XtX_ @ C.T), self.sigma_sq_)
            # t-stat
            tstat = cope / np.sqrt(varcope)
            pval = 1 - t.cdf(tstat, self.dof_)
            return {"tstat": tstat, "pval": pval, "zstat": self.ttoz(tstat, self.dof_)}

    @staticmethod
    def ttoz(t, dof):
        def tdist(t, v):
            return betainc(v / 2.0, 1 / 2, v / (v + t**2)) / 2.0

        return (np.sqrt(2) * erfinv(1 - 2 * tdist(t, dof))) * np.sign(t)

    def fit_transform(self, X, y):
        self.fit(X, y)
        return self.transform(X)

    def transform(self, X):
        if self.beta_ is not None:
            return X @ self.beta_
