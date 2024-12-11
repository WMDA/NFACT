from NFACT.base.utils import error_and_exit


def process_dim(dim: dict) -> dict:
    """
    Function to process dimensions from
    command line input.

    Parameters
    ----------
    dim: str
        number of dimensions
    Returns
    -------
    dim: int/float
        number of dimensions as
        float or int
    """
    dim = str(dim)
    if ".0" in dim:
        dim = float(dim)
    try:
        dim = int(dim)
    except Exception:
        error_and_exit(
            False,
            f"Dimmensions must be a interger value. {dim} is not a interger type",
        )

    return dim


def process_wta_zhr(wta_zthr: dict) -> dict:
    """
    Function to process wta threshold from
    command line input.

    Parameters
    ----------
    wta_zthr: str
        string of wta_zthr

    Returns
    -------
    wta_zthr: float
       wta_zhr as float
    """
    try:
        wta_zthr = float(wta_zthr)
    except Exception:
        error_and_exit(
            False,
            f"wta_thr must be a float value. {wta_zthr} is not a float",
        )
    return wta_zthr


def process_components(components: str, algo: str) -> dict:
    """
    Function to process number of pca components from
    command line input.

    Parameters
    ----------
    components: str
        number of components
    algo: str
        type of algo

    Returns
    -------
    components: int/float
        number of components either
        as a int or float
    """
    components = str(components)
    if ".0" in components:
        components = float(components)
    if algo != "nmf":
        if components:
            try:
                components = int(components)
            except Exception:
                error_and_exit(
                    False,
                    f"Number of components must be a interger value. {components} is not a interger type",
                )
    return components


def check_pca(pca_type):
    """
    Function to check the PCA type
    to use for ICA

    Parameters
    ----------
    algo: str
       string of decomp method.

    Returns
    -------
    algo: str
       returns lower case
       of str
    """
    pca_types = ["pca", "migp"]
    if pca_type.lower() not in pca_types:
        error_and_exit(
            False,
            f"{pca_type} is not implemented in NFACT. NFACT currently implements PCA and MIGP (case insensitive). Please specify with --pca_type",
        )
    return pca_type.lower()


def process_command_args(args: dict) -> dict:
    """
    Function to process command line arguments.

    Parameters
    ----------
    args: dict
        dictionary of command line
        arguments

    Returns
    -------
    args: dict
    """
    args["dim"] = process_dim(args["dim"])
    if args["wta_zthr"]:
        args["wta_zthr"] = process_wta_zhr(args["wta_zthr"])
    if args["algo"] == "nmf":
        return args
    args["components"] = process_components(args["components"], args["algo"])
    args["pca_type"] = check_pca(args["pca_type"])

    return args
