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
    nrows = int(mat[-1, 0])
    ncols = int(mat[-1, 1])
    return sps.csc_matrix((data, (rows, cols)), shape=(nrows, ncols)).toarray()


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


def melodic_incremental_group_pca(
    fdt_matrix: np.array, n_dim: int = 1000, d_pca: int = 1000, keep_mean: bool = False
):
    """
    Function wrapper around matrix_MIGP.

    Parameters
    ----------
    fdt_matrix: np.array,
        Should be wide i.e. nxN where N bigger than n t
        fdt_matrix is made of column blocks, each block is
        one 'subject', and 'time' is the column dimension
    n_dim: int
        number of dimensions that fdt_matrix is split into.
        Default is 1000.
    d_pca: int
        maximum number of prinicple components kept
        (set to n_dim if larger than n_dim) Default is 1000.


    Returns
    -------
    pca_matrix: np.array
        matrix that has been reduced.

    """

    migpa_timer = Timer()
    migpa_timer.tic()
    col = colours()
    print(f"{col['purple']}\nPerforming MIGP{col['reset']}")
    if keep_mean:
        matrix_mean = np.mean(fdt_matrix, axis=1, keepdims=True)

    if d_pca > n_dim:
        d_pca = n_dim

    pca_matrix = matrix_MIGP(fdt_matrix, n_dim, d_pca)

    if keep_mean:
        pca_matrix = pca_matrix + matrix_mean

    print(f"Old matrix size was: {fdt_matrix.shape[0]}x{fdt_matrix.shape[1]}")
    print(f"New matrix size is : {pca_matrix.shape[0]}x{pca_matrix.shape[1]}")
    print(f"MIGP finished in : {migpa_timer.toc()} secs.")
    return pca_matrix


def matrix_MIGP(
    fdt_matrix: np.array,
    n_dim: int = 1000,
    d_pca: int = 1000,
):
    """
    Function to apply
    MELODIC's Incremental Group-PCA dimensionality to
    a given matrix.

    Parameters
    ----------
    fdt_matrix: np.array,
        Should be wide i.e. nxN where N bigger than n t
        fdt_matrix is made of column blocks, each block is
        one 'subject', and 'time' is the column dimension
    n_dim: int
        number of dimensions that fdt_matrix is split into.
        Default is 1000.
    d_pca: int
        maximum number of prinicple components kept
        (set to n_dim if larger than n_dim) Default is 1000.


    Returns
    -------
    pca_matrix: np.array
        matrix that has been reduced.
    """

    random_idx = np.random.permutation(fdt_matrix.shape[1])
    shuffled_column = fdt_matrix[:, random_idx]
    intermediary_matrix = None

    for matrix_index in tqdm(range(0, fdt_matrix.shape[1], n_dim), colour="magenta"):
        pca_matrix = shuffled_column[
            :, matrix_index : min(matrix_index + n_dim, fdt_matrix.shape[1] + 1)
        ].T

        if intermediary_matrix is not None:
            intermediary_matrix = np.concatenate(
                (intermediary_matrix, demean(pca_matrix)), axis=0
            )
        else:
            intermediary_matrix = demean(pca_matrix)

        k = min(d_pca, n_dim)
        _, k_eignvectors = eigsh(intermediary_matrix @ intermediary_matrix.T, k)

        intermediary_matrix = k_eignvectors.T @ intermediary_matrix

    pca_matrix = intermediary_matrix[: min(intermediary_matrix.shape[0], d_pca), :].T

    return pca_matrix
