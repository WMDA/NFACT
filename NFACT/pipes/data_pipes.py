import numpy as np
from sklearn.preprocessing import StandardScaler
import os
from fsl.data.image import Image
import NFACT.pipes.image_handling as img


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
    if not (img.is_gifti(seed[0]) or img.is_nifti(seed[0])):
        seed = read_ascii_list(seed[0])
    # check that the files exist
    for s in seed:
        try:
            Image(s)
        except:
            if not os.path.exists(s):
                raise (Exception(f"Cannot read file {s}"))
    return seed
