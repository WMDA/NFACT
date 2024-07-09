import scipy.sparse as sps
import numpy as np
from tqdm import tqdm
from scipy.sparse.linalg import eigsh
from NFACT.utils.utils import Timer


# This function loads a omatrix2 matrix
def load_mat2(matfile):
    """Loads ptx sparse matrix format"""
    mat = np.loadtxt(matfile)
    # Reading these with pandas is MUCH faster than numpy. Nope not true
    # mat = pd.read_csv(matfile, header=None, dtype={0:np.int32, 1:np.int32, 2:np.float32}, delim_whitespace=True).to_numpy()
    data = mat[:-1, -1]
    rows = np.array(mat[:-1, 0] - 1, dtype=int)
    cols = np.array(mat[:-1, 1] - 1, dtype=int)
    nrows, ncols = int(mat[-1, 0]), int(mat[-1, 1])
    M = sps.csc_matrix((data, (rows, cols)), shape=(nrows, ncols)).toarray()
    return M


# Average matrices across subjects
def avg_matrix2(list_of_matfiles):
    M = 0.0
    for mat in tqdm(list_of_matfiles):
        M += load_mat2(mat)

    M /= len(list_of_matfiles)
    return M


# demean a matrix
def demean(X, axis=0):
    return X - np.mean(X, axis=axis, keepdims=True)


# Implementation of incremental PCA for matrix2
def matrix_MIGP(C, n_dim=1000, d_pca=1000, keep_mean=False):
    """Apply incremental PCA to C
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
