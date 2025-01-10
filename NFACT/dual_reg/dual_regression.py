import numpy as np
from scipy.optimize import nnls


def ica_dual_regression(components: dict, connectivity_matrix: np.ndarray) -> dict:
    """
    Dual regression function for ICA.
    Regresses the invidiual connectivity matrix
    onto the group components.
    If white matter component then regresses
    grey matter map onto connectivity matrix and vice versa.

    Parameters
    ----------
    components: dict
        dictionary of components
    connectivity_matrix: np.ndarray
        subjects loaded connectivity matrix

    Returns
    -------
    dict: dictionary
        dictionary of components
    """

    wm_component_grey_map = (
        np.linalg.pinv(components["white_components"].T) @ connectivity_matrix.T
    ).T
    wm_component_white_map = np.linalg.pinv(wm_component_grey_map) @ connectivity_matrix
    gm_component_grey = (
        np.linalg.pinv(components["grey_components"]) @ connectivity_matrix
    )
    gm_component_grey_map = (
        np.linalg.pinv(gm_component_grey.T) @ connectivity_matrix.T
    ).T

    return {
        "grey_components": gm_component_grey_map,
        "white_components": wm_component_white_map,
    }


def nmf_dual_regression(components: dict, connectivity_matrix: np.ndarray) -> dict:
    """
    Dual regression method for NMF.

    Parameters
    ----------
    components: dict
        dictionary of components
    connectivity_matrix: np.ndarray
        subjects loaded connectivity matrix

    Returns
    -------
    dict: dictionary
        dictionary of components
    """

    wm_component_white_map = np.array(
        [
            nnls(components["grey_components"], connectivity_matrix[:, col])[0]
            for col in range(connectivity_matrix.shape[1])
        ]
    ).T

    gm_component_grey_map = np.array(
        [
            nnls(wm_component_white_map.T, connectivity_matrix.T[:, col])[0]
            for col in range(connectivity_matrix.shape[0])
        ]
    )

    return {
        "grey_components": gm_component_grey_map,
        "white_components": wm_component_white_map,
    }
