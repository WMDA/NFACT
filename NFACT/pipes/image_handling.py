from fsl.data.image import Image
import nibabel as nib
import numpy as np
from sklearn.preprocessing import StandardScaler
import numpy as np
import os
from NFACT.utils.utils import error_and_exit
import pathlib


def get_file(img_file: list, sub: str) -> list:
    """
    Function to get an imaging file
    type and returns it. Checks that file
    is correct file type and exists.

    Parameters
    ----------
    img_file: list
        a list of imaging files
    sub: str
       path to subjects directory.

    Returns
    -------
    img_files: list
        list of imging files

    """
    img_files = [os.path.join(sub, file) for file in img_file]
    [
        error_and_exit(
            os.path.exists(path), f"Unable to find {path}. Please check it exists"
        )
        for path in img_files
    ]
    [check_files_are_imaging_files(path) for path in img_files]
    return img_files


def check_files_are_imaging_files(path: str) -> bool:
    """
    Function to check that imaging files
    are actually imaging files.

    Parameters
    ----------

    Returns
    -------
    None
    """
    accepted_extenions = [".gii", ".nii"]
    file_extensions = pathlib.Path(path).suffixes
    file = os.path.basename(path)
    sub = os.path.basename(os.path.dirname(path))
    error_and_exit(
        [file for file in file_extensions if file in accepted_extenions],
        f"{file} for {sub} is an incorrect file type (not gii or nii)",
    )


# TODO: fade these functions out in favour of checking file extensions as faster
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


def save_G(G, ptx_folder, out_file, seeds):
    # get seed files and work out if they are surfaces of volumes
    coord_mat2 = np.loadtxt(
        os.path.join(ptx_folder, "coords_for_fdt_matrix2"), dtype=int
    )
    seeds_id = coord_mat2[:, -2]
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
