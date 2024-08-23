from sklearn.preprocessing import StandardScaler
import scipy.sparse as sps
from NFACT.NFACT_base.utils import colours, nprint
import numpy as np


def normalise_components(
    grey_matter: np.array, white_matter: np.array, demean: bool = True
) -> dict:
    """
    Normalise components.
    Useful for visulaization

    Parameters
    ----------
    grey_matter: np.array
        grey matter component
    white_matter: np.array
        white matter component
    demean: bool
        Demean matrix. default is True


    Returns
    -------
    dict: dictionary.
        dictionary of normalised components
    """
    col = colours()
    nprint(f"{col['plum']}Normalising components{col['reset']}")

    return {
        "grey_matter": StandardScaler(with_mean=demean).fit_transform(grey_matter),
        "white_matter": StandardScaler(with_mean=demean)
        .fit_transform(white_matter.T)
        .T,
    }


def load_fdt_matrix(matfile: str) -> np.ndarray:
    """
    Function to load a single fdt matrix
    as a ptx sparse matrix format.

    Parameters
    ----------
    matfile: str
       path to file

    Returns
    -------
    sparse_matrix: np.array
       sparse matrix in numpy array
       form.
    """
    mat = np.loadtxt(matfile)
    data = mat[:-1, -1]
    rows = np.array(mat[:-1, 0] - 1, dtype=int)
    cols = np.array(mat[:-1, 1] - 1, dtype=int)
    nrows = int(mat[-1, 0])
    ncols = int(mat[-1, 1])
    return sps.csc_matrix((data, (rows, cols)), shape=(nrows, ncols)).toarray()