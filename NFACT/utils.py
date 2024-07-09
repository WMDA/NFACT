#!/usr/bin/env python

# utils.py - helper functions for ptx_matrix_tools
#
# Author: Saad Jbabdi <saad@fmrib.ox.ac.uk>
#         Rogier Mars <rogier.mars@ndcn.ox.ac.uk>
#
# Copyright (C) 2023 University of Oxford
# SHBASECOPYRIGHT


# imports
import numpy as np
import time
from tqdm import tqdm
from sklearn.preprocessing import StandardScaler
import os
import nibabel as nib
from fsl.data.image import Image
from scipy.special import betainc, erfinv
from sklearn.decomposition import FastICA, NMF
import scipy.sparse as sps
from scipy.sparse.linalg import eigsh
from scipy.stats import t

import warnings

warnings.filterwarnings("ignore")


class dotdict(dict):
    """dot.notation access to dictionary attributes"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


# Helper class for timing
class timer:
    def __init__(self):
        """
        Matlab-style timer class
        t = timer()
        t.tic()
        .... do stuff
        t.toc()
        """
        self._t = time.time()

    def tic(self):
        self._t = time.time()

    def toc(self):
        return f"{time.time()-self._t:.2f}"


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
    t = timer()
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
    t = timer()
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
    W = (
        decomp.components_
    )  # np.linalg.pinv(G)@C   #Note: this is W.T as it is more convenient to store W.T

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


def dualreg(Cs, X, normalise=False):
    """Dual regression of C on X where C is a group mat and X is either G or W
    We have :  C = G*W
    So either:
        Cs = G*Ws
    or:
        Cs' = W'*Gs'
    Input:
    Cs: 2d array - individual subject connectivity matrix
    Outputs:
    Gs : 2d array
    Ws : 2d array
    """
    # if X is G, then X.shape[0] is same as Cs.shape[0]
    if X.shape[0] == Cs.shape[0]:
        # X is G
        Ws = np.linalg.pinv(X) @ Cs
        Gs = (np.linalg.pinv(Ws.T) @ Cs.T).T
    # if X is W, then X.shape[1] is same as Cs.shape[1] (remember W is in fact W.T)
    elif X.shape[1] == Cs.shape[1]:
        # X is W
        Gs = (np.linalg.pinv(X.T) @ Cs.T).T
        Ws = np.linalg.pinv(Gs) @ Cs

    if normalise:
        Gs = StandardScaler().fit_transform(Gs)
        Ws = StandardScaler().fit_transform(Ws.T).T

    return Gs, Ws


def winner_takes_all(X, axis=1, z_thr=0.0):
    # must apply scaling for z_thr to make sense
    Xs = StandardScaler().fit_transform(X)
    Xs_max = np.max(Xs, axis=axis, keepdims=True)
    Xs_wta = np.argmax(Xs, axis=axis, keepdims=True) + 1
    Xs_wta[Xs_max < z_thr] = 0.0
    return np.array(Xs_wta, dtype=int)


# Helper functions to save the results
def mat2vol(mat, lut_vol):
    mask = lut_vol.data > 0
    matvol = np.zeros(lut_vol.shape + (len(mat),))

    for i in range(len(mat)):
        matvol.reshape(-1, len(mat))[mask.flatten(), i] = mat[i, lut_vol.data[mask] - 1]

    return matvol


# IO stuff
def is_gifti(filename):
    try:
        x = nib.load(filename)
        return type(x) == nib.gifti.gifti.GiftiImage
    except:
        return False


def is_nifti(filename):
    try:
        x = nib.load(filename)
        return type(x) == nib.nifti1.Nifti1Image
    except:
        try:
            Image(filename)
            return True
        except:
            return False


def read_ascii_list(my_list):
    with open(my_list, "r") as f:
        lines = f.readlines()
    return [l.strip() for l in lines]


def is_ptx_log(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
    for l in lines:
        if "probtrackx" in l:
            return True
    return False


def get_seed(ptx_folder, check_exists=True):
    # read last command
    logfile = os.path.join(ptx_folder, "probtrackx.log")
    if not is_ptx_log(logfile):
        raise (Exception(f"{logfile} is not a probtrackx log file"))

    with open(logfile, "r") as f:
        lines = f.readlines()
    cmd = lines[-3].split(" ")
    print(cmd)
    # get the seed(s):
    seed = [x.split("=")[-1] for x in cmd if "--seed=" in x]
    # if len(seed)==0, user may have used '-x' instead of '--seed'
    if len(seed) == 0:
        seed = [cmd[cmd.index("-x") + 1]]
    if not check_exists:
        return seed
    # check if it is a list of files or a file
    if not (is_gifti(seed[0]) or is_nifti(seed[0])):
        seed = read_ascii_list(seed[0])
    # check that the files exist
    for s in seed:
        try:
            Image(s)
        except:
            if not os.path.exists(s):
                raise (Exception(f"Cannot read file {s}"))
    return seed


def save_W(W, ptx_folder, out_file):
    lut_vol = Image(os.path.join(ptx_folder, "lookup_tractspace_fdt_matrix2"))
    # check that lookup is compatible with matrix
    if sum(lut_vol.data.flatten() > 0) != W.shape[1]:
        raise (
            Warning(
                f"Lookup_tractspace_fdt_matrix2 (size={sum(lut_vol.data.flatten()>0)} does not seem to be compatible with output W matrix (size={W.shape[1]})"
            )
        )
    Wvol = mat2vol(W, lut_vol)
    tmp = Image(Wvol, header=lut_vol.header)
    tmp.save(out_file)


def save_G(G, ptx_folder, out_file, seeds=None):
    # get seed files and work out if they are surfaces of volumes
    coord_mat2 = np.loadtxt(
        os.path.join(ptx_folder, "coords_for_fdt_matrix2"), dtype=int
    )
    seeds_id = coord_mat2[:, -2]
    if seeds is None:
        seeds = get_seed(ptx_folder)
    for idx, seed in enumerate(seeds):
        G_seed = G[seeds_id == idx, :]
        if is_gifti(seed):
            surf = nib.load(seed)
            # Why does the below not preserve the structure code?
            darrays = [
                nib.gifti.GiftiDataArray(
                    data=np.array(x, dtype=float),
                    datatype="NIFTI_TYPE_FLOAT32",
                    intent=2001,
                    meta=surf.darrays[0].meta,
                )
                for x in G_seed.T
            ]
            gii = nib.GiftiImage(darrays=darrays)
            if len(seeds) > 1:
                gii.to_filename(out_file + f"_{idx}.func.gii")
            else:
                gii.to_filename(out_file + ".func.gii")
        elif is_nifti(seed):
            vol = Image(seed)
            xyz = coord_mat2[seeds_id == idx, :3]
            xyz_idx = np.ravel_multi_index(xyz.T, vol.shape)
            ncols = G_seed.shape[1]
            out = np.zeros(vol.shape + (ncols,)).reshape(-1, ncols)
            for i, g in enumerate(G_seed.T):
                out[xyz_idx, i] = g
            img = Image(out.reshape(vol.shape + (ncols,)), header=vol.header)
            img.save(out_file + f"_{idx}")


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
            return dotdict(
                {"tstat": tstat, "pval": pval, "zstat": self.ttoz(tstat, self.dof_)}
            )

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
