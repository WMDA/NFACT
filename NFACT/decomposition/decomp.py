from sklearn.decomposition import FastICA, NMF
from sklearn.preprocessing import StandardScaler
import numpy as np
from sklearn.utils._testing import ignore_warnings
from sklearn.exceptions import ConvergenceWarning

from NFACT.decomposition.matrix_handling import matrix_MIGP


@ignore_warnings(category=ConvergenceWarning)
def ICA_decomp(n_components: int, fdt_matrix: np.array) -> dict:
    """
    Function to perform ica decomposition

    Parameters
    ----------
    n_components: int
        number of components
    fdt_matrix: np.array
        matrix to perform decomposition
        on

    Returns
    -------
    dict: dictionary
        dictionary of grey and white matter
        components
    """
    decomp = FastICA(n_components=n_components)
    grey_matter = decomp.fit_transform(fdt_matrix)
    white_matter = np.linalg.pinv(grey_matter) @ fdt_matrix
    return {"grey_components": grey_matter, "white_components": white_matter}


@ignore_warnings(category=ConvergenceWarning)
def NFM_decomp(n_components: int, fdt_matrix: np.array) -> dict:
    """
    Function to perform NFM.

    Parameters
    ----------
    n_components: int
        number of components
    fdt_matrix: np.array
        matrix to perform decomposition
        on

    Returns
    -------
    dict: dictionary
        dictionary of grey and white matter
        components
    """
    decomp = NMF(
        n_components=n_components,
        alpha_W=0.1,
        l1_ratio=1,
        init="nndsvd",
        random_state=1,
    )
    grey_matter = decomp.fit_transform(fdt_matrix)
    white_matter = decomp.components_
    return {"grey_components": grey_matter, "white_components": white_matter}


def matrix_decomposition(
    fdt_matrix: np.array,
    n_components: int,
    algo: str,
    normalise: bool,
    sign_flip: bool,
    pca_dim: int,
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
    n_components: int
        number of components
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
        pca_matrix = matrix_MIGP(fdt_matrix, pca_dim, pca_dim)
        components = ICA_decomp(n_components, pca_matrix)

        if sign_flip:
            print("Sign-flipping components")
            components["grey_components"] = SignFlip(components["grey_components"].T).T
            components["white_components"] = SignFlip(components["white_components"])

    if algo == "nfm":
        components = NFM_decomp(n_components, fdt_matrix)

    demean = True if algo == "ica" else False

    if normalise:
        components["normalised_grey"] = normalise_components(
            components["grey_components"], demean
        )
        components["normalised_white"] = normalise_components(
            components["white_components"], demean
        )

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
    print("Normalising components")

    return {
        "grey_matter": StandardScaler(with_mean=demean).fit_transform(grey_matter),
        "white_matter": StandardScaler(with_mean=demean)
        .fit_transform(white_matter.T)
        .T,
    }


def SignFlip(decomp_matrix: np.array, thr: int = 0) -> np.array:
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
