import numpy as np
from sklearn.preprocessing import StandardScaler
import numpy as np
import os
from NFACT.NFACT_base.imagehandling import (
    save_white_matter,
    save_grey_matter_components,
)
from NFACT.NFACT_base.utils import colours


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
        algo_path = os.path.join("components", algo, "decomp")
        w_file_name = f"W_dim{dim}"
        grey_prefix = "G"

        if "normalised" in comp:
            algo_path = os.path.join("components", algo, "normalised")
            w_file_name = f"W_norm_dim{dim}"
            grey_prefix = "G_norm"

        if "grey" in comp:
            print(f"{col['pink']}Saving {comp}{col['reset']}")
            save_grey_matter_components(
                save_type,
                components[comp],
                nfact_path,
                seeds,
                algo_path,
                dim,
                os.path.join(nfact_path, "group_averages", "coords_for_fdt_matrix2"),
                grey_prefix,
            )
        if "white" in comp:
            print(f"{col['purple']}Saving {comp}{col['reset']}")
            save_white_matter(
                components[comp],
                os.path.join(
                    nfact_path, "group_averages", "lookup_tractspace_fdt_matrix2.nii.gz"
                ),
                os.path.join(nfact_path, algo_path, w_file_name),
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
    grey_wta_map = create_wta_map(components["grey_components"], 1, z_thr, demean)
    save_white_matter(
        white_wta_map,
        os.path.join(
            nfact_path, "group_averages", "lookup_tractspace_fdt_matrix2.nii.gz"
        ),
        os.path.join(nfact_path, "components", algo, "WTA", f"W_WTA_dim{dim}"),
    )
    save_grey_matter_components(
        save_type,
        grey_wta_map,
        nfact_path,
        seeds,
        os.path.join(nfact_path, "components", algo, "WTA"),
        dim,
        os.path.join(nfact_path, "group_averages", "coords_for_fdt_matrix2"),
        "G_WTA",
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
