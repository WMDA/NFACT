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
        '-n',
        "--nfact_dir",
        dest='nfact_dir',
        help=f"{col['red']}REQUIRED:{col['reset']} Path to nfact directory"
    )
    option.add_argument(
        '-t',
        "-type_of_decomp",
        dest="type_of_decomp",
       help=f"{col['red']}REQUIRED:{col['reset']} type of decompoistion to regress on. Options are nfm and ica (case insensitive)",
    )
    option.add_argument(
        "-d",
        "--design_matrix",
        dest="design_matrix",
        help=f"{col['red']}REQUIRED:{col['reset']} A path to a GLM design matrix",
    )
    option.add_argument(
        "-c",
        "--contrasts",
        dest="contrast",
        help=f"{col['red']}REQUIRED:{col['reset']} A path to a contrast matrix",
    )

    option.add_argument(
        '-a',
        '--analysis_name',
        dest='analysis_name',
        default='nfact_glm',
        help="Optional name to give analysis. Default is nfact_glm"
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
