import numpy as np
from NFACT.NFACT_base.imagehandling import (
    save_grey_matter_components,
    save_white_matter,
)
from NFACT.NFACT_base.utils import colours, nprint
import os
from fsl.data.image import Image
import nibabel as nb
from glob import glob


def vol2mat(matvol: np.ndarray, lut_vol: object) -> np.ndarray:
    """
    Function to reshape a volume back into
    the original matrix format.

    Parameters
    ----------
    matvol: np.ndarray
        array reformatted as a volume
    lut_vol: object
        image object of lookup volume

    Returns
    -------
    matrix: np.ndarray
        array converted back to original matrix form
    """
    mask = lut_vol.data > 0
    num_rows = matvol.shape[-1]
    matrix = np.zeros((num_rows, np.max(lut_vol.data)))

    for row in range(num_rows):
        matrix[row, lut_vol.data[mask] - 1] = matvol.reshape(-1, num_rows)[
            mask.flatten(), row
        ]

    return matrix


def save_dual_regression_images(
    save_type: str,
    components: dict,
    nfact_path: str,
    seeds: list,
    algo: str,
    dim: int,
    sub: str,
    ptx_directory: str,
) -> None:
    """
    Function to save regression images
    TODO: paths need changing

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
    sub: str
        Subject id in string format

    Returns
    -------
    None
    """

    col = colours()
    nprint(f"{col['purple']}Saving Dual regression components{col['reset']}\n")
    for comp, _ in components.items():
        algo_path = algo
        w_file_name = f"W_{sub}_dim{dim}"
        grey_prefix = f"G_{sub}"

        if "normalised" in comp:
            algo_path = os.path.join(algo, "normalised")
            w_file_name = f"W_{sub}_norm_dim{dim}"
            grey_prefix = f"G_{sub}_norm"

        if "grey" in comp:
            save_grey_matter_components(
                save_type,
                components[comp],
                nfact_path,
                seeds,
                algo_path,
                dim,
                os.path.join(ptx_directory, "coords_for_fdt_matrix2"),
                grey_prefix,
            )
        if "white" in comp:
            save_white_matter(
                components[comp],
                os.path.join(ptx_directory, "lookup_tractspace_fdt_matrix2.nii.gz"),
                os.path.join(nfact_path, algo_path, w_file_name),
            )


def white_component(nfact_dir: str, algo: str) -> np.ndarray:
    """
    Function to get the group level
    white matter component for dual regression.

    Parameters
    ----------
    nfact_dir: str
        path to the nfact directory
    algo: str
        The algorithm for dual regression

    Returns
    -------
    np.darray: np.array
        array of white matter component
        from the volume
    """
    lookup_vol = Image(
        os.path.join(
            nfact_dir, "group_averages", "lookup_tractspace_fdt_matrix2.nii.gz"
        )
    )
    white_matter = nb.load(
        glob(os.path.join(nfact_dir, "components", algo.upper(), "decomp", "W_dim*"))[0]
    )
    return vol2mat(white_matter.get_fdata(), lookup_vol)


def load_grey_matter_component(file_name: str) -> np.array:
    """
    Load grey matter component from a GIFTI file.

    Parameters
    ----------
    file_name: str
        Path to the GIFTI file.

    Returns
    -------
    grey_matter_component: np.array
        Reconstructed grey matter component.
    """

    gifti_img = nb.load(file_name)
    return np.column_stack([darray.data for darray in gifti_img.darrays])


def grey_components(seeds: list, nfact_dir, algo):
    """
    Function to get grey components from seeds.

    Parameters
    ----------
    nfact_dir: str
        path to the nfact directory
    algo: str
        The algorithm for dual regression
    seeds: list
        A list of seeds
    """
    grey_matter = glob(
        os.path.join(nfact_dir, "components", algo.upper(), "decomp", "G_dim*")
    )
    sorted_components = [
        seed for _, seed in sorted(zip(seeds, grey_matter), key=lambda pair: pair[0])
    ]
    return np.vstack([load_grey_matter_component(seed) for seed in sorted_components])


def get_group_level_components(nfact_dir: str, algo: str, seeds: list):
    """
    Function to get group level components

    Parameters
    ----------
    nfact_dir: str
        path to the nfact directory
    algo: str
        The algorithm for dual regression
    seeds: list
        A list of seeds

    Returns
    -------
    dict: dictionary
        dict of components
    """

    return {
        "white_components": white_component(nfact_dir, algo),
        "grey_components": grey_components(seeds, nfact_dir, algo),
    }
