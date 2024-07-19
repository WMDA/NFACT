import scipy.sparse as sps
import numpy as np
from tqdm import tqdm
from scipy.sparse.linalg import eigsh
import os
from NFACT.utils.utils import Timer, error_and_exit, colours


def process_fdt_matrix2(
    list_of_fdt: list, directory: str, group_mode: bool
) -> np.array:
    """
    Function to get group average matrix

    Parameters
    ----------
    list_of_fdt: list
        list of fdt2 dot files

    Returns
    -------
    matrcies: np.array
       np.array of fdt2 matrix either averaged
       across subjects or single subjects
    """

    if group_mode:
        try:
            fdt_matrix2 = avg_fdt(list_of_fdt)
        except Exception as e:
            error_and_exit(False, f"Unable to load fdt_matrix2 due to {e}")
    if not group_mode:
        try:
            fdt_matrix2 = load_fdt_matrix(list_of_fdt[0])
        except Exception as e:
            error_and_exit(False, f"Unable to load fdt_matrix2 due to {e}")
    save_avg_matrix(fdt_matrix2, directory)
    return fdt_matrix2


def load_previous_matrix(path: str) -> np.array:
    """
    Function to load previous matrix.

    Parameters
    ----------
    path: str
       path to matrix

    Returns
    -------
    array: np.array
        fdt2 matrix.
    """
    if os.path.exists(path):
        print("Loading previously saved matrix")
        return np.load(os.path.join(path))
    return None


def save_avg_matrix(matrix: np.array, directory: str) -> None:
    """
    Function to save average matrix as npz file

    Parameters
    ----------
    matrix: np.array
        fdt2 matrix
    directory: str
        path to group_average folder in the nfact
        folder

    Returns
    -------
    None
    """
    try:
        print(f'Saving matrix to {os.path.join(directory, "group_averages")}')
        np.save(os.path.join(directory, "group_averages", "average_matrix2"), matrix)
    except Exception as e:
        error_and_exit(False, f"Unable to save matrix due to {e}")


def load_fdt_matrix(matfile: str) -> np.array:
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
    nrows, ncols = int(mat[-1, 0]), int(mat[-1, 1])
    sparse_matrix = sps.csc_matrix((data, (rows, cols)), shape=(nrows, ncols)).toarray()
    return sparse_matrix


def avg_fdt(list_of_matfiles: list) -> np.array:
    """
    Function to create and create
    an average group matrix.

    Parameters
    ----------
    list_of_matfiles: list
        list of matricies
        for the group.

    Returns
    -------
    sparse_matrix: np.array
        np.array of sparse matrix.
    """
    sparse_matrix = 0.0

    for matrix in tqdm(list_of_matfiles, colour="magenta"):
        sparse_matrix += load_fdt_matrix(matrix)

    sparse_matrix /= len(list_of_matfiles)
    return sparse_matrix


def demean(matrix: np.array, axis: int = 0):
    """
    Function to demean a matrix

    Parameters
    ----------
    matrix: np.array
        matrix
    axis: int
        which axis to calculate
        the mean from
    """
    return matrix - np.mean(matrix, axis=axis, keepdims=True)


def matrix_MIGP(C, n_dim=1000, d_pca=1000, keep_mean=False):
    """
    Apply incremental PCA to C
    Inputs:
    C (2D array) : should be wide i.e. nxN where N bigger than n
    We pretend that the matrix C is made of column blocks, each block is
    one 'subject', and 'time' is the column dimension.

    n_dim (int)  : C is split up into nXn_dim matrices
    n_pca (int)  : maximum number of pcs kept (set to n_dim if larger than n_dim)
    keep_mean (bool) : keep the mean of C

    Returns:
    reduced version of C (size nxmin(n_dim,n_pca)
    """
    # Random order for columns of C (create a view rather than copy the data)

    if keep_mean:
        C_mean = np.mean(C, axis=1, keepdims=True)
        # raise(Exception('Not implemented keep_mean yet!'))

    if d_pca > n_dim:
        d_pca = n_dim

    print("...Starting MIGP")
    t = Timer()
    t.tic()
    _, N = C.shape
    random_idx = np.random.permutation(N)
    Cview = C[:, random_idx]
    W = None
    for i in tqdm(range(0, N, n_dim)):
        data = Cview[
            :, i : min(i + n_dim, N + 1)
        ].T  # transpose to get time as 1st dimension
        if W is not None:
            W = np.concatenate((W, demean(data)), axis=0)
        else:
            W = demean(data)
        k = min(d_pca, n_dim)
        _, U = eigsh(W @ W.T, k)

        W = U.T @ W

    data = W[: min(W.shape[0], d_pca), :].T

    # Add mean back
    if keep_mean:
        print("... Adding back mean.")
        data = data + C_mean

    print(f"...Old matrix size : {C.shape[0]}x{C.shape[1]}")
    print(f"...New matrix size : {data.shape[0]}x{data.shape[1]}")
    print(f"...MIGP done in {t.toc()} secs.")
    return data
