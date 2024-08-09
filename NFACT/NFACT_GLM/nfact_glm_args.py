import argparse
from NFACT.NFACT_decomp.utils.utils import colours


def nfact_glm_args() -> dict:
    """
    Function to get arguements
    to run NFACT GLM

    Parameters
    -----------
    None

    Returns
    -------
    dict: dictionary object
        dict of arguments
    """
    option = argparse.ArgumentParser(
        prog="nfact_glm",
        description=print(nfact_glm_splash()),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    col = colours()

    option.add_argument(
        "-d",
        "--design_matrix",
        dest="design_matrix",
        help="A path to a GLM design matrix",
    )
    option.add_argument(
        "-c",
        "--contrasts",
        dest="contrast",
        help="A path to a contrast matrix",
    )
    return vars(option.parse_args())


def nfact_glm_splash() -> str:
    """
    Function to get NFACT GLM splash

    Parameters
    ----------
    None

    Returns
    -------
    str: string
        splash of NFACT GLM
    """
    col = colours()
    return f"""
    {col['pink']}
 _   _ ______   ___   _____  _____   _____  _     ___  ___
| \ | ||  ___| / _ \ /  __ \|_   _| |  __ \| |    |  \/  |
|  \| || |_   / /_\ \| /  \/  | |   | |  \/| |    | .  . |
| . ` ||  _|  |  _  || |      | |   | | __ | |    | |\/| |
| |\  || |    | | | || \__/\  | |   | |_\ \| |____| |  | |
\_| \_/\_|    \_| |_/ \____/  \_/    \____/\_____/\_|  |_/
{col['reset']}
"""
