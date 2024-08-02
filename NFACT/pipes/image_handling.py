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
    directory: str,
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
    directory: str
        str of directory to save component to
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
            nfact_path, directory, f"G_{dim}_{os.path.basename(seed).replace('.', '_')}"
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
) -> None:
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


def winner_takes_all(
    components: dict,
    z_thr: float,
    algo: str,
    nfact_path: str,
    save_type: str,
    seeds: list,
    dim: str,
) -> None:
    """
    Wrapper function around creating WTA and saving
    the components

    Parameters
    ---------
    components: dict
        dictionary of components
    z_thr: float
        threshold the map at
    algo: str
        ICA or NFM
    nfact_path: str
        Path to NFACT directory
    save_type: str
        Should grey components be gifti/nifit
    seeds: list
        list of seeds
    dim: str
        number of dimensions (for saving files)
    """
    demean = True if algo == "ICA" else False
    white_wta_map = create_wta_map(components["white_components"], 0, z_thr, demean)
    grey_wta_map = create_wta_map(components["grey_components"], 1, z_thr)
    save_white_matter(
        white_wta_map,
        os.path.join(
            nfact_path, "group_averages", "lookup_tractspace_fdt_matrix2.nii.gz"
        ),
        os.path.join(nfact_path, algo, "WTA", f"W_dim{dim}"),
    )
    save_grey_matter_components(
        save_type,
        grey_wta_map,
        nfact_path,
        seeds,
        os.path.join(nfact_path, algo, "WTA"),
        dim,
    )


def create_wta_map(
    component: np.array,
    axis: int,
    z_thr: float,
    demean: bool,
) -> np.ndarray:
    """
    Function to create a winner takes all
    map from a component

    Parameters
    ----------
    component: np.array
        component to create a
    axis: int
        axis to get max values
        from
    z_thr: float
        threshold the map at
    demean: bool
        to demean when z scoring

    Returns
    -------
    np.array: array
        array of thresholded component
    """

    component_zscored = StandardScaler(with_mean=demean).fit_transform(component)
    component_max = np.max(component_zscored, axis=axis, keepdims=True)
    component_wta = np.argmax(component_zscored, axis=axis, keepdims=True) + 1
    component_wta[component_max < z_thr] = 0.0
    return np.array(component_wta, dtype=int)


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
