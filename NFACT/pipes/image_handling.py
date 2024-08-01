from fsl.data.image import Image
import nibabel as nib
import numpy as np
from sklearn.preprocessing import StandardScaler
import numpy as np
import os
from NFACT.utils.utils import error_and_exit, colours
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


def save_grey_matter_volume(
    grey_matter_component: np.array,
    file_name: str,
    seed: str,
    x_y_z_coordinates: np.array,
):
    """

    Function to save grey matter component as
    a volume

    Parameters
    ----------
    grey_matter_component: np.array
        grey matter component for a
        single seed
    file_name: str
        file name
    seed: str
        path to seed
    x_y_z_coordinates: np.array
        array of x, y, z co-ordinates

    Returns
    -------
    None
    """

    vol = Image(seed)
    xyz_idx = np.ravel_multi_index(x_y_z_coordinates.T, vol.shape)
    ncols = grey_matter_component.shape[1]
    out = np.zeros(vol.shape + (ncols,)).reshape(-1, ncols)
    for idx, col in enumerate(grey_matter_component.T):
        out[xyz_idx, idx] = col
    Image(out.reshape(vol.shape + (ncols,)), header=vol.header).save(file_name)


def save_grey_matter_gifit(
    grey_matter_component: np.array, file_name: str, seed: str
) -> None:
    """
    Function to save grey matter as gifti

    Parameters
    ----------
    grey_matter_component: np.array
        grey matter component for a
        single seed
    file_name: str
        file name
    seed: str
        path to seed

    Returns
    -------
    None
    """
    surf = nib.load(seed)
    darrays = [
        nib.gifti.GiftiDataArray(
            data=np.array(col, dtype=float),
            datatype="NIFTI_TYPE_FLOAT32",
            intent=2001,
            meta=surf.darrays[0].meta,
        )
        for col in grey_matter_component.T
    ]
    nib.GiftiImage(darrays=darrays).to_filename(file_name)


def save_grey_matter_cifit():
    return None


def save_grey_matter_components(
    save_type: str,
    grey_matter_components: np.array,
    nfact_path: str,
    seeds: list,
    algo: str,
    dim: int,
) -> None:
    """
    Function wrapper to save grey matter
    components.

    Parameters
    ----------
    save_type: str
        should grey matter be saved as
        gifti, nifit or cifti
    grey_matter_components: str
        grey_matter_component matrix
    nfact_path: str
        str to nfact directory
    seeds: list
        list of seeds
    algo: str
        str of algo
    dim: int
        number of dimensions
        used for naming output

    Returns
    -------
    None
    """

    coord_mat2 = np.loadtxt(
        os.path.join(nfact_path, "group_averages", "coords_for_fdt_matrix2"), dtype=int
    )
    seeds_id = coord_mat2[:, -2]
    for idx, seed in enumerate(seeds):
        mask_to_get_seed = seeds_id == idx
        grey_matter_seed = grey_matter_components[mask_to_get_seed, :]
        file_name = os.path.join(
            nfact_path, algo, f"G_{dim}_{os.path.basename(seed).replace('.', '_')}"
        )
        if save_type == "gifti":
            save_grey_matter_gifit(grey_matter_seed, file_name, seed)
        if save_type == "nifti":
            save_grey_matter_volume(
                grey_matter_seed, file_name, seed, coord_mat2[mask_to_get_seed, :3]
            )
        if save_type == "cifti":
            return None


def save_images(
    save_type: str, components: dict, nfact_path: str, seeds: list, algo: str, dim: int
):
    """
    Function to save  grey and white
    components.

    Parameters
    ----------
    save_type: str
        should grey matter be saved as
        gifti, nifit or cifti
    components: dict
        dictionary of components
    nfact_path: str
        str to nfact directory
    seeds: list
        list of seeds
    algo: str
        str of algo
    dim: int
        number of dimensions
        used for naming output

    Returns
    -------
    None
    """

    col = colours()
    for comp, _ in components.items():
        algo_path = algo
        if "normalised":
            algo_path = os.path.join(algo, "normalised")
        if "grey" in comp:
            print(f"{col['pink']}Saving {comp}{col['reset']}")
            save_grey_matter_components(
                save_type, components[comp], nfact_path, seeds, algo_path, dim
            )
        if "white" in comp:
            print(f"{col['purple']}Saving {comp}{col['reset']}")
            save_white_matter(
                components[comp],
                os.path.join(
                    nfact_path, "group_averages", "lookup_tractspace_fdt_matrix2.nii.gz"
                ),
                os.path.join(nfact_path, algo_path, f"W_dim{dim}"),
            )


def winner_takes_all(X, axis=1, z_thr=0.0):
    # must apply scaling for z_thr to make sense
    Xs = StandardScaler().fit_transform(X)
    Xs_max = np.max(Xs, axis=axis, keepdims=True)
    Xs_wta = np.argmax(Xs, axis=axis, keepdims=True) + 1
    Xs_wta[Xs_max < z_thr] = 0.0
    return np.array(Xs_wta, dtype=int)


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
