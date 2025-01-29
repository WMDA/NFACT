import pathlib
import os
from fsl.data.image import Image
import nibabel as nib
import numpy as np
import re
from .utils import error_and_exit


def imaging_type(path: str) -> str:
    """
    Function to return imaging
    type based on extension.

    Parameters
    ----------
    path: str
        path to str

    Return
    ------
    str: string
        str of nifit or gifti
    """
    file_extensions = get_imaging_details_from_path(path)["file_extensions"]
    if ".nii" in file_extensions:
        return "nifti"
    if ".gii" in file_extensions:
        return "gifti"


def mat2vol(matrix: np.array, lut_vol: object) -> np.ndarray:
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
    path: str
        file path

    Returns
    -------
    None
    """
    file_details = get_imaging_details_from_path(path)
    error_and_exit(
        [
            file
            for file in file_details["file_extensions"]
            if file in [".gii", ".nii", ".mat"]
        ],
        f'{file_details["file"]} for {file_details["subject"]} is an incorrect file type (not gii or nii)',
    )


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
    if sum(lut_vol.data.flatten() > 0) != white_matter_components.shape[1]:
        error_and_exit(
            False,
            f"Lookup_tractspace_fdt_matrix2 (size={sum(lut_vol.data.flatten()>0)} is not compatible with output white matter component (size={white_matter_components.shape[1]})",
        )

    white_matter_vol = mat2vol(white_matter_components, lut_vol)
    Image(white_matter_vol, header=lut_vol.header).save(out_file)


def save_grey_matter_volume(
    grey_matter_component: np.array,
    file_name: str,
    seed: str,
    x_y_z_coordinates: np.array,
) -> None:
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
    grey_component: np.array, file_name: str, seed: str, medial_wall: str
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
    medial_wall: str
        str to medial wall path

    Returns
    -------
    None
    """
    surf = nib.load(seed)
    m_wall = nib.load(medial_wall).darrays[0].data != 0
    grey_matter_component = np.zeros((m_wall.shape[0], grey_component.shape[1]))
    grey_matter_component[m_wall == 1, :] = grey_component

    darrays = [
        nib.gifti.GiftiDataArray(
            data=np.array(col, dtype=float),
            datatype="NIFTI_TYPE_FLOAT32",
            intent=2001,
            meta=surf.darrays[0].meta,
        )
        for col in grey_matter_component.T
    ]
    nib.GiftiImage(darrays=darrays).to_filename(f"{file_name}.func.gii")


def rename_seed(seeds: list) -> list:
    """
    Function to renmae seed. Either
    will rename it as left_seed or
    right_seed. Or removes unecessary extensions

    Parameters
    ----------
    seed: list
        list of seed names

    Returns
    -------
    seed: list
        list of processed seed names.
    """

    return [
        (
            "left_seed"
            if "L" in (seed_extension := os.path.basename(seed).split("."))
            else "right_seed"
            if "R" in seed_extension
            else re.sub(r".gii|.surf", "", os.path.basename(seed))
        )
        for seed in seeds
        if (seed_extension := seed.split("."))
    ]


def name_seed(seed: str, nfact_path: str, directory: str, prefix: str, dim: int) -> str:
    """
    Function to return file path of seed.
    Correctly names seed

    Parameters
    -----------
    seed: str
        name of seed
    nfact_path: str
        path to nfact directory
    directory: str
        path to directory to save
        file
    prefix:
        prefix of seed
    dim: int
        number of dimensions from
        decomp
    """
    seed_name = rename_seed([seed])[0]
    file_name = f"{prefix}_dim{dim}_{seed_name}"
    return os.path.join(
        nfact_path,
        directory,
        file_name,
    )


def save_grey_matter_components(
    grey_matter_components: np.array,
    nfact_path: str,
    seeds: list,
    directory: str,
    dim: int,
    coord_path: str,
    medial_wall: list,
    prefix: str = "G",
) -> None:
    """
    Function wrapper to save grey matter
    components.

    Parameters
    ----------

    grey_matter_components: str
        grey_matter_component matrix
    nfact_path: str
        str to nfact directory
    seeds: list
        list of seeds
    directory: str
        str of directory to save component to
    dim: int
        number of dimensions
        used for naming output
    medial_wall: list
        list of medial path
    Returns
    -------
    None
    """
    coord_mat2 = np.loadtxt(coord_path, dtype=int)
    seeds_id = coord_mat2[:, -2]
    for idx, seed in enumerate(seeds):
        save_type = imaging_type(seed)
        mask_to_get_seed = seeds_id == idx
        grey_matter_seed = grey_matter_components[mask_to_get_seed, :]
        file_name = name_seed(seed, nfact_path, directory, prefix, dim)

        if save_type == "gifti":
            file_name = re.sub("_gii", "", file_name)
            mw = medial_wall[idx]
            save_grey_matter_gifit(grey_matter_seed, file_name, seed, mw)

        if save_type == "nifti":
            file_name = re.sub("_nii", "", file_name)
            if "_gz" in file_name:
                file_name = re.sub("_gz", "", file_name)
            save_grey_matter_volume(
                grey_matter_seed, file_name, seed, coord_mat2[mask_to_get_seed, :3]
            )
