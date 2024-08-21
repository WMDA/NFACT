import numpy as np
from NFACT.NFACT_base.imagehandling import (
    save_grey_matter_components,
    save_white_matter,
)
from NFACT.NFACT_base.utils import colours
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
):
    """
    Function to save regression images
    TODO: combine with save_images function

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
    """

    col = colours()
    print(f"{col['purple']}Saving Dual regression components{col['reset']}\n")
    for comp, _ in components.items():
        algo_path = os.path.join(algo, "dual_reg")
        w_file_name = f"W_{sub}_dim{dim}"
        grey_prefix = f"G_{sub}"

        if "normalised" in comp:
            algo_path = os.path.join(algo, "dual_reg", "normalised")
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


def white_component(nfact_dir: str, algo: str) -> np.darray:
    """
    Function to get the group level
    white matter component for dual regression.

    Parameters
    ----------
    nfact_dir: str
    algo: str
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


def get_group_level_components(nfact_dir: str, algo: str):
    """
    Function to get group level components

    Parameters
    ----------
    nfact_dir: str
    algo: str
    """

    return {"white_component": white_component(nfact_dir, algo), "grey_component": ""}
