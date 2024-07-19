from sklearn.decomposition import FastICA, NMF
from sklearn.preprocessing import StandardScaler
import numpy as np

from NFACT.decomposition.matrix_handling import matrix_MIGP
from NFACT.utils.utils import Timer

# TODO: rename variables as better names


def ICA_decomp(n_components: int, fdt_matrix: np.array) -> dict:
    """
    Function to perform ica decomposition

    Parameters
    ----------
    n_components: int
        number of components
    fdt_matrix: np.array
        matrix to perform decomposition
        on

    Returns
    -------
    dict: dictionary
        dictionary of grey and white matter
        components
    """
    decomp = FastICA(n_components=n_components)
    grey_matter = decomp.fit_transform(fdt_matrix)
    white_matter = np.linalg.pinv(grey_matter) @ fdt_matrix
    return {"grey_components": grey_matter, "white_components": white_matter}


def NFM_decomp(n_components: int, fdt_matrix: np.array) -> dict:
    """
    Function to perform NFM.

    Parameters
    ----------
    n_components: int
        number of components
    fdt_matrix: np.array
        matrix to perform decomposition
        on

    Returns
    -------
    dict: dictionary
        dictionary of grey and white matter
        components
    """
    decomp = NMF(
        n_components=n_components,
        alpha_W=0.1,
        l1_ratio=1,
        init="nndsvd",
        random_state=1,
    )
    grey_matter = decomp.fit_transform(fdt_matrix)
    white_matter = decomp.components_
    return {"grey_components": grey_matter, "white_components": white_matter}


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

    print(f"...Decomposition done in {t.toc()} secs.")

    if sign_flip:
        print("...Sign-flip components")
        G = SignFlip(G.T).T
        W = SignFlip(W)

    return G, W


def normalise_components(G, W, demean: bool = True) -> dict:
    """
    Normalise components.
    Useful for visulaization

    Parameters
    ----------


    Returns
    -------
    dict: dictionary.

    """
    print("Normalising components")

    return {
        "G": StandardScaler(with_mean=demean).fit_transform(G),
        "W": StandardScaler(with_mean=demean).fit_transform(W.T).T,
    }


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
