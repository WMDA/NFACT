import argparse
from NFACT.utils.utils import colours


def nfact_args() -> dict:
    """
    Function to define cmd arguments

    Parameters
    ----------
    None

    Returns
    -------
    dict: dictionary
        dictionary of cmd arguments
    """
    args = argparse.ArgumentParser(
        prog="nfact",
        description=print(nfact_splash()),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    args.add_argument(
        "-p",
        "--ptxdir",
        nargs="+",
        dest="ptxdir",
        help="List of file paths to probtrackx directories. If not provided will then --list_ofsubjects must be provided",
    )
    args.add_argument(
        "-l",
        "--list_of_subjects",
        dest="list_of_subjects",
        help="Filepath to a list of subjects. If not given then --ptxdir must be",
    )
    args.add_argument("-o", "--outdir", dest="outdir", help="Path to output folder")
    args.add_argument("-d", "--dim", dest="dim", help="Number of dimensions/components")

    args.add_argument(
        "--seeds",
        "-s",
        dest="seeds",
        nargs="+",
        help="Seeds used in NFACT_PP/probtrackx",
    )
    args.add_argument(
        "-M",
        "--migp",
        dest="migp",
        default=1000,
        help="MELODIC's Incremental Group-PCA dimensionality (default is 1000)",
    )
    args.add_argument(
        "-S" "--skip_dual_reg",
        dest="skip_dual_reg",
        action="store_true",
        default=False,
        help="Options to skip dual regression",
    )
    args.add_argument(
        "-a",
        "--algo",
        required=False,
        default="ICA",
        help="What algorithm to run. Options are: ICA (default), or NMF.",
    )
    args.add_argument(
        "-W",
        "--wta",
        dest="wta",
        action="store_true",
        default=False,
        help="Save winner-takes-all maps",
    )

    args.add_argument(
        "-Z",
        "--wta_zthr",
        dest="wta_zthr",
        default=0.0,
        help="Winner-takes-all threshold (default=0.)",
    )
    args.add_argument(
        "-N",
        "--normalise",
        dest="normalise",
        action="store_true",
        default=False,
        help="normalise components by scaling",
    )
    args.add_argument(
        "-S",
        "--sign_flip",
        dest="sign_flip",
        action="store_true",
        default=False,
        help="sign flip components",
    )

    # If a design is provided, run the stats
    args.add_argument(
        "-G",
        "--glm_mat",
        dest="glm_mat",
        help="Run a GLM using design and contrast matrices provided (only in dualreg mode)",
    )
    args.add_argument(
        "-C",
        "--glm_con",
        dest="glm_con",
        help="Run a GLM using design and contrast matrices provided (only in dualreg mode)",
    )

    return vars(args.parse_args())


def nfact_splash() -> str:
    """
    Function to return NFACT splash

    Parameters
    ----------
    None

    Returns
    -------
    str: splash
    """
    col = colours()
    return f"""
{col['pink']} 
 _   _ ______   ___   _____  _____    
| \ | ||  ___| /   \ /  __ \|_   _|    
|  \| || |_   / /_\ \| /  \/  | |      
|     ||  _|  |  _  || |      | |    
| |\  || |    | | | || \__/\  | |    
\_| \_/\_|    \_| |_/ \____/  \_/ 
{col['reset']} 
"""
