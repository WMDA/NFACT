import argparse
from NFACT.utils.utils import colours


def cmd_args():
    p = argparse.ArgumentParser(
        prog="NFACT",
        description=print(splash()),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--ptxdir",
        required=True,
        nargs="+",
        metavar="<STR>",
        type=str,
        help="ProbTrackx Folder(s), or ascii list of folders",
    )
    p.add_argument(
        "--outdir", required=True, metavar="<STR>", type=str, help="Output Folder"
    )
    p.add_argument(
        "--dim", required=True, metavar="<INT>", type=int, help="Number of dimensions"
    )

    # Some optional arguments to be added here
    p.add_argument(
        "--ptx_seeds",
        required=False,
        nargs="+",
        metavar="<NIFTI or GIFTI>",
        type=str,
        help="Seeds used in PTX (if not provided, these will be taken from the log file)",
    )
    p.add_argument(
        "--migp",
        required=False,
        default=1000,
        metavar="<INT>",
        type=int,
        help="MIGP dimensionality (default is 1000. set to negative to skip MIGP)",
    )
    p.add_argument(
        "--mode",
        required=False,
        default="dualreg",
        type=str,
        help="What to do when provided with a list of ptx_folders. Options are 'dualreg' (default - runs decomp on average and produces single subject decomp using dual regression) or 'average' (only produces decomp of the average)",
    )
    p.add_argument(
        "--algo",
        required=False,
        default="ICA",
        type=str,
        help="What algorithm to run. Options are: ICA (default), or NMF.",
    )
    p.add_argument("--wta", action="store_true", help="Save winner-takes-all maps")
    p.add_argument(
        "--wta_zthr",
        required=False,
        default=0.0,
        type=float,
        help="Winner-takes-all threshold (default=0.)",
    )
    p.add_argument(
        "-N",
        "--normalise",
        dest="normalise",
        action="store_true",
        required=False,
        default=False,
        help="normalise components by scaling",
    )
    p.add_argument(
        "-S",
        "--sign_flip",
        dest="sign_flip",
        action="store_true",
        required=False,
        default=False,
        help="sign flip components",
    )

    # If a design is provided, run the stats
    p.add_argument(
        "--glm_mat",
        required=False,
        metavar="<design.mat>",
        help="Run a GLM using design and contrast matrices provided (only in dualreg mode)",
    )
    p.add_argument(
        "--glm_con",
        required=False,
        metavar="<design.con>",
        help="Run a GLM using design and contrast matrices provided (only in dualreg mode)",
    )

    return p.parse_args()


def splash() -> str:
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
