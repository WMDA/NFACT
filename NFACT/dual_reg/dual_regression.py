from NFACT.base.utils import error_and_exit
import numpy as np
from scipy.optimize import nnls
from joblib import Parallel, delayed


def run_decomp(decomp: object, connectivity_matrix: np.ndarray) -> dict:
    """
    Function to
    """
    try:
        components = decomp(connectivity_matrix)
    except ValueError as e:
        error_and_exit(
            False,
            f"Components have incompatable size with connectivity Matrix {e}",
        )
    except Exception as e:
        error_and_exit(False, f"Unable to perform dual regression due to {e}")
    return components


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


def nmf_dual_regression(
    components: dict, connectivity_matrix: np.ndarray, n_jobs: int = -1
) -> dict:
    """
    Dual regression function for NMF with optimized performance.

    Parameters
    ----------
    components: dict
        Dictionary of components.
    connectivity_matrix: np.ndarray
        Subjects' loaded connectivity matrix.
    n_jobs: int
        Number of parallel jobs for computation.
        Default is -1 (all available CPUs).

    Returns
    -------
    dict
        Dictionary of components.
    """

    grey_components = components["grey_components"]
    wm_component_white_map = np.array(
        Parallel(n_jobs=n_jobs)(
            delayed(lambda col: nnls(grey_components, connectivity_matrix[:, col])[0])(
                col
            )
            for col in range(connectivity_matrix.shape[1])
        )
    ).T

    wm_component_white_map_T = wm_component_white_map.T
    gm_component_grey_map = np.array(
        Parallel(n_jobs=n_jobs)(
            delayed(
                lambda col: nnls(
                    wm_component_white_map_T, connectivity_matrix.T[:, col]
                )[0]
            )(col)
            for col in range(connectivity_matrix.shape[0])
        )
    )

    return {
        "grey_components": gm_component_grey_map,
        "white_components": wm_component_white_map,
    }
