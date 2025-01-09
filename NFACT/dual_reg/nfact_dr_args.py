import argparse
from NFACT.base.utils import colours, no_args, verbose_help_message


def nfactdr_args() -> dict:
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
    base_args = argparse.ArgumentParser(
        prog="nfact_dr",
        description=print(nfact_dr_splash()),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    col = colours()
    base_args.add_argument(
        "-hh",
        "--verbose_help",
        dest="verbose_help",
        default=False,
        action="store_true",
        help="""
        Prints help message and example usages
      """,
    )
    set_up_args = base_args.add_argument_group(
        f"{col['deep_pink']}Set Up Arguments{col['reset']}"
    )
    set_up_args.add_argument(
        "-l",
        "--list_of_subjects",
        dest="list_of_subjects",
        help="Filepath to a list of subjects",
    )
    set_up_args.add_argument(
        "-o",
        "--outdir",
        dest="outdir",
        help="Path to output directory",
    )
    dr_args = base_args.add_argument_group(
        f"{col['pink']}Dual Regression Arguments{col['reset']}"
    )
    dr_args.add_argument(
        "-a",
        "--algo",
        dest="algo",
        help="Which NFACT algorithm to perform dual regression on",
    )
    dr_args.add_argument(
        "--seeds",
        "-s",
        dest="seeds",
        help="File of seeds used in NFACT_PP/probtrackx",
    )
    dr_args.add_argument(
        "--medial_wall",
        "-m",
        dest="medial_wall",
        default=False,
        help="""
        Medial wall images if surface seeds given.
        """,
    )
    dr_args.add_argument(
        "-n",
        "--nfact_decomp_dir",
        dest="nfact_decomp_dir",
        help="Filepath to the NFACT_decomp directory. Use this if you have ran NFACT decomp",
    )
    dr_args.add_argument(
        "-d",
        "--decomp_dir",
        dest="decomp_dir",
        help="""Filepath to decomposition components. 
        WARNING NFACT decomp expects components to be named in a set way. See documentation for further info.""",
    )
    dr_args.add_argument(
        "-N",
        "--normalise",
        dest="normalise",
        action="store_true",
        default=False,
        help="normalise components by scaling",
    )

    cluster_args = base_args.add_argument_group(
        f"{col['amethyst']}Cluster Arguments{col['reset']}"
    )

    cluster_args.add_argument(
        "-C",
        "--cluster",
        dest="cluster",
        action="store_true",
        default=False,
        help="Use cluster enviornment",
    )
    cluster_args.add_argument(
        "-cq",
        "--queue",
        dest="cluster_queue",
        default=None,
        help="Cluster queue to submit to",
    )
    cluster_args.add_argument(
        "-cr",
        "--cluster_ram",
        dest="cluster_ram",
        default="60",
        help="Ram that job will take. Default is 60",
    )
    cluster_args.add_argument(
        "-ct",
        "--cluster_time",
        dest="cluster_time",
        default=False,
        help="Time that job will take. nfact_pp will assign a time if none given",
    )
    cluster_args.add_argument(
        "-cqos",
        "--cluster_qos",
        dest="cluster_qos",
        default=False,
        help="Set the qos for the cluster",
    )

    no_args(base_args)
    options = base_args.parse_args()
    if options.verbose_help:
        verbose_help_message(base_args, nfact_dr_usage())
    return vars(options)


def nfact_dr_splash() -> str:
    """
    Function to return NFACT DR splash

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
 _   _ ______   ___   _____  _____  ______ ______ 
| \ | ||  ___| / _ \ /  __ \|_   _| |  _  \| ___ \\
|  \| || |_   / /_\ \| /  \/  | |   | | | || |_/ /
| . ` ||  _|  |  _  || |      | |   | | | ||    / 
| |\  || |    | | | || \__/\  | |   | |/ / | |\ \ 
\_| \_/\_|    \_| |_/ \____/  \_/   |___/  \_| \_|
{col['reset']}                                                                              
"""


def nfact_dr_usage() -> str:
    """
    Function to print examples on how to use
    nfact_dr.

    Parameteres
    -----------
    None

    Returns
    -------
    str: str
        string of help message
    """
    col = colours()
    return f"""
{col['darker_pink']}Dual regression usage:{col['reset']}
    nfact_dr --list_of_subjects /path/to/nfact_config_sublist \\
        --seeds /path/to//seeds.txt \\
        --nfact_decomp_dir /path/to/nfact_decomp \\
        --outdir /path/to/output_directory \\
        --algo NMF 

{col['darker_pink']}ICA Dual regression usage:{col['reset']}
    nfact_dr --list_of_subjects /path/to/nfact_config_sublist \\
        --seeds /path/to//seeds.txt \\
        --nfact_decomp_dir /path/to/nfact_decomp \\
        --outdir /path/to/output_directory \\
        --algo ICA 

{col['darker_pink']}Dual regression with medial wall seeds usage:{col['reset']}
    nfact_dr --list_of_subjects /path/to/nfact_config_sublist \\
        --seeds /path/to/seeds.txt \\
        --nfact_decomp_dir /path/to/nfact_decomp \\
        --outdir /path/to/output_directory \\
        --medial_wall /path/to/medial_wall.txt \\
        --algo NMF 
"""
