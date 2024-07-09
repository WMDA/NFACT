from sklearn.decomposition import FastICA, NMF
from sklearn.preprocessing import StandardScaler
import numpy as np

from NFACT.decomposition.matrix_handling import matrix_MIGP
from NFACT.utils.utils import Timer


def SignFlip(X, thr=0):
    """Sign flip the rows of X such that the heavy tail is >0"""
    Y = []
    for row in X:
        rowthr = row[np.abs(row) > thr]
        # nothing above thresh
        if np.min(np.abs(rowthr)) == 0:
            Y.append(row)
        # all > 0:
        elif all(rowthr > 0):
            Y.append(row)
        elif all(rowthr < 0):
            Y.append(-row)
        else:
            right = np.mean(row[rowthr > 0])
            left = -np.mean(row[rowthr < 0])
            skew = np.sign(right - left)
            if skew == 0:
                Y.append(row)
            else:
                Y.append(row * skew)
    return np.asarray(Y)


def matrix_decomposition(
    C, n_components, normalise=True, sign_flip=True, do_migp=True, algo="ICA", **kwargs
):
    """Decompose matrix2 as C = G*W

    Starts with MIGP then ICA t get G then Regression to get W

    """

    if do_migp:
        C_small = matrix_MIGP(C, **kwargs)
    else:
        C_small = C

    print("...Decomposition")
    t = Timer()
    t.tic()
    if algo == "ICA":
        decomp = FastICA(n_components=n_components)
    elif algo == "NMF":
        decomp = NMF(
            n_components=n_components,
            alpha_W=0.1,
            l1_ratio=1,
            init="nndsvd",
            random_state=1,
        )
    else:
        raise (Exception(f"Unknown algo {algo}. Should be one of 'ICA' or 'NMF'"))

    # To get G:
    G = decomp.fit_transform(C_small)
    # To get W:
    W = decomp.components_
    # np.linalg.pinv(G)@C
    # #Note: this is W.T as it is more convenient to store W.T

    print(f"...Decomposition done in {t.toc()} secs.")
    if normalise:
        print("...Normalise components")
        G = StandardScaler().fit_transform(G)
        W = StandardScaler().fit_transform(W.T).T
    if sign_flip:
        print("...Sign-flip components")
        G = SignFlip(G.T).T
        W = SignFlip(W)

    return G, W
