from sklearn.decomposition import FastICA, NMF
from sklearn.preprocessing import StandardScaler
import numpy as np
from sklearn.utils._testing import ignore_warnings
from sklearn.exceptions import ConvergenceWarning
import warnings

warnings.filterwarnings("ignore")

from NFACT.NFACT_decomp.decomposition.matrix_handling import (
    melodic_incremental_group_pca,
)
from NFACT.NFACT_decomp.utils.utils import error_and_exit, colours
from NFACT.NFACT_config.nfact_config_functions import create_combined_algo_dict


@ignore_warnings(category=ConvergenceWarning)
def ICA_decomp(parameters: dict, pca_matrix: np.array, fdt_matrix: np.array) -> dict:
    """
    Function to perform ica decomposition

    Parameters
    ----------
    parameters: dict
        dictionary of hyperparameters
    pca_matrix: np.array
        matrix that has been reduced.
    fdt_matrix: np.array
        matrix to perform decomposition
        on

    Returns
    -------
    dict: dictionary
        dictionary of grey and white matter
        components
    """

    decomp = FastICA(**parameters)

    try:
        decomp.fit(pca_matrix)
        grey_matter = decomp.transform(pca_matrix)
    except Exception as e:
        error_and_exit(False, f"Unable to perform ICA due to {e}")
    return {
        "grey_components": grey_matter,
        "white_components": np.linalg.pinv(grey_matter) @ fdt_matrix,
    }


@ignore_warnings(category=ConvergenceWarning)
def NFM_decomp(parameters: dict, fdt_matrix: np.array) -> dict:
    """
    Function to perform NFM.

    Parameters
    ----------
    parameters: dict
        dictionary of hyperparameters
    fdt_matrix: np.array
        matrix to perform decomposition
        on

    Returns
    -------
    dict: dictionary
        dictionary of grey and white matter
        components
    """
    decomp = NMF(**parameters)
    try:
        grey_matter = decomp.fit_transform(fdt_matrix)
    except Exception as e:
        error_and_exit(False, f"Unable to perform NFM due to {e}")
    return {"grey_components": grey_matter, "white_components": decomp.components_}


def get_parameters(parameters: dict, algo: str, n_components: int) -> dict:
    """
    Function to get parameters for
    decomp. If no parameters are
    given then for ICA will use sckit learn defaults
    for NFM it will use defaults aside from
    alpha_w, random_state, l1_ratio and init.

    Parameters
    ----------
    parameters: dict
       dictionary of parameters
    algo: str
       str of algo to use
    n_components: int
        number of components

    Returns
    -------
    parameters: dict
        dictionary of parameters
    """
    if parameters:
        parameters["n_components"] = n_components
        return parameters

    parameters = create_combined_algo_dict()[algo]
    parameters["n_components"] = n_components
    if algo == "nfm":
        parameters["alpha_W"] = 0.1
        parameters["init"] = "nndsvd"
        parameters["random_state"] = 1
        parameters["l1_ratio"] = 1
    return parameters


def matrix_decomposition(
    fdt_matrix: np.array,
    algo: str,
    normalise: bool,
    sign_flip: bool,
    pca_dim: int,
    parameters: dict,
) -> dict:
    """
    Wrapper function to decompose a matrix2 into
    grey * white matter components.

    Performs either ICA or NFM depending on input.
    Will normalise components however with NFM it does
    not demean components to keep values positive.

    Parameters
    ----------
    fdt_matrix: np.array
        matrix to decompose
    algo: str
        which algo
    normalise: bool
        to z score normalise components
    sign_flip: bool
        to sign flip ICA components so heavy tail is > 0
    pca_dim: int
        number of pca dimensions for ICA

    Returns
    -------
    dict: dictionary
        dict of components
    """

    if algo == "ica":
        # TODO: either change function to accept single argument or offer differnt inputs
        pca_matrix = melodic_incremental_group_pca(fdt_matrix, pca_dim, pca_dim)
        components = ICA_decomp(parameters, pca_matrix, fdt_matrix)

        if sign_flip:
            print("Sign-flipping components")
            components["grey_components"] = SignFlip(components["grey_components"].T).T
            components["white_components"] = SignFlip(components["white_components"])

    if algo == "nfm":
        components = NFM_decomp(parameters, fdt_matrix)

    demean = True if algo == "ica" else False

    if normalise:
        normalised = normalise_components(
            components["grey_components"], components["white_components"], demean
        )
        components["normalised_white"] = normalised["white_matter"]
        components["normalised_grey"] = normalised["grey_matter"]

    return components


def normalise_components(
    grey_matter: np.array, white_matter: np.array, demean: bool = True
) -> dict:
    """
    Normalise components.
    Useful for visulaization

    Parameters
    ----------
    grey_matter: np.array
        grey matter component
    white_matter: np.array
        white matter component
    demean: bool
        Demean matrix. default is True


    Returns
    -------
    dict: dictionary.
        dictionary of normalised components
    """
    col = colours()
    print(f"{col['plum']}Normalising components\n{col['reset']}")

    return {
        "grey_matter": StandardScaler(with_mean=demean).fit_transform(grey_matter),
        "white_matter": StandardScaler(with_mean=demean)
        .fit_transform(white_matter.T)
        .T,
    }


def SignFlip(decomp_matrix: np.array, thr: int = 0) -> np.ndarray:
    """
    Function to sign flip the rows of
    the decomp matrix so that the heavy tail
    is > 0.

    Parameters
    ----------
    decomp_matrix: np.array
        decomposition matrix

    thr: int=0
        threshold value

    Returns
    -------
    signflip_decomp_matrix: np.array
        array of signfliped matrix
    """

    signflip_decomp_matrix = np.empty_like(decomp_matrix)
    for index in range(decomp_matrix.shape[0]):
        row = decomp_matrix[index]
        rowthr = row[np.abs(row) > thr]

        if rowthr.size == 0 or np.min(np.abs(rowthr)) == 0:
            signflip_decomp_matrix[index] = row
            continue

        positive_elements = row[row > thr]
        negative_elements = row[row < -thr]

        positive_mean = np.mean(positive_elements) if positive_elements.size > 0 else 0
        negative_mean = -np.mean(negative_elements) if negative_elements.size > 0 else 0

        skew = np.sign(positive_mean - negative_mean)
        signflip_decomp_matrix[index] = row if skew == 0 else row * skew

    return signflip_decomp_matrix
