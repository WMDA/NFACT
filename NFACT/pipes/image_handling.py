from fsl.data.image import Image
import nibabel as nib
import numpy as np
from sklearn.preprocessing import StandardScaler
import numpy as np
import os
from NFACT.utils.utils import error_and_exit
import pathlib
import re


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


def get_imaging_details_from_path(path: str) -> dict:
    """
    Function to return imaging suffix,
    subject and file from a path.

    Parameters
    ----------
    path: str
        path as a string

    Returns
    --------
    dict: dictionary
        dict of file extension,
        subject and file.
    """
    return {
        "file_extensions": pathlib.Path(path).suffixes,
        "subject": re.findall(r"\b(sub(?:ject)?-?\d+)\b", path),
        "file": os.path.basename(path),
    }


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
    file_details = get_imaging_details_from_path(path)
    file_extensions = file_details["file_extensions"]
    file = file_details["file"]
    sub = file_details["subject"]
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


def save_white_matter(
    white_matter_components: np.array, path_to_lookup_vol: str, out_file: str
) -> None:
    """
    Function to save white matter compponents
    as a volume.

    Parameters
    ----------
    white_matter_components: np.array
        The white matter components from ICA/NFM
        to save
    path_to_lookup_vol: str
        path to look up volume from probtrackx
    out_file: str
        string to path to save images

    Returns
    -------
    None

    """
    lut_vol = Image(path_to_lookup_vol)
    # check that lookup is compatible with matrix
    if sum(lut_vol.data.flatten() > 0) != white_matter_components.shape[1]:
        error_and_exit(
            False,
            f"Lookup_tractspace_fdt_matrix2 (size={sum(lut_vol.data.flatten()>0)} is not compatible with output W matrix (size={white_matter_components.shape[1]})",
        )

    White_matter_vol = mat2vol(white_matter_components, lut_vol)
    Image(White_matter_vol, header=lut_vol.header).save(out_file)


def save_grey_matter_volume(grey_matter_components, ptx_folder, out_file, seeds):
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


def save_grey_matter_gifit(grey_matter_seeds, file_name, seed):
    surf = nib.load(seed)
    darrays = [
        nib.gifti.GiftiDataArray(
            data=np.array(x, dtype=float),
            datatype="NIFTI_TYPE_FLOAT32",
            intent=2001,
            meta=surf.darrays[0].meta,
        )
        for x in grey_matter_seeds.T
    ]
    nib.GiftiImage(darrays=darrays).to_filename(file_name)


def save_grey_matter_cifit():
    return None


def save_grey_matter_components(
    save_type: str, grey_matter_components: np.array, coord_mat2_path: str, seeds: list
):
    coord_mat2 = np.loadtxt(coord_mat2_path, dtype=int)
    seeds_id = coord_mat2[:, -2]
    for idx, seed in enumerate(seeds):
        mask_to_get_seed = seeds_id == idx
        grey_matter_seed = grey_matter_components[mask_to_get_seed, :]

    return None


def winner_takes_all(X, axis=1, z_thr=0.0):
    # must apply scaling for z_thr to make sense
    Xs = StandardScaler().fit_transform(X)
    Xs_max = np.max(Xs, axis=axis, keepdims=True)
    Xs_wta = np.argmax(Xs, axis=axis, keepdims=True) + 1
    Xs_wta[Xs_max < z_thr] = 0.0
    return np.array(Xs_wta, dtype=int)


# Helper functions to save the results
def mat2vol(matrix: np.array, lut_vol: object) -> np.array:
    """
    Function to reshape a matrix
    to be saved as a volume.

    Parameters
    ----------
    matrix: np.array
        array to  be saved as volume
    lut_vol: object
        image object of lookup volume

    Returns
    -------
    matvol: np.array
        array reformatted to be converted to
        a volume
    """
    mask = lut_vol.data > 0
    matvol = np.zeros(lut_vol.shape + (len(matrix),))

    for row in range(len(matrix)):
        matvol.reshape(-1, len(matrix))[mask.flatten(), row] = matrix[
            row, lut_vol.data[mask] - 1
        ]

    return matvol


def save_components(components: dict, nfact_directory: str):
    """
    Function to save components.

    Parameters
    ----------
    """

    lookup_img = os.path.join(nfact_directory, "lookup_tractspace_fdt_matrix2")
    coord_mat2 = np.loadtxt(
        os.path.join(nfact_directory, "coords_for_fdt_matrix2"), dtype=int
    )

    return None
