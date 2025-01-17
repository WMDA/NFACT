import argparse
from NFACT.base.utils import colours, no_args, verbose_help_message
from NFACT.base.base_args import cluster_args, parallel_args, set_up_args


def nfact_pp_args() -> dict:
    """
    Function to get arguements
    to run NFACT pre-processing

    Parameters
    -----------
    None

    Returns
    -------
    dict: dictionary object
        dict of arguments
    """
    base_args = argparse.ArgumentParser(
        prog="nfact_pp",
        description=print(nfact_pp_splash()),
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
    base_args.add_argument(
        "-O",
        "--overwrite",
        dest="overwrite",
        action="store_true",
        default=False,
        help="Overwrite previous file structure",
    )
    set_up_args(base_args, col)

    file_tree_input = base_args.add_argument_group(
        f"{col['plum']}Filetree mode arguments: {col['reset']}"
    )
    file_tree_input.add_argument(
        "-f",
        "--file_tree",
        dest="file_tree",
        default=False,
        help="""Use this option to provide name of predefined file tree to 
        perform whole brain tractography. NFACT_PP currently comes with HCP filetree. See documentation for further information.""",
    )
    tractography_input = base_args.add_argument_group(
        f"{col['pink']}Tractography arguments: {col['reset']}"
    )

    tractography_input.add_argument(
        "-s",
        "--seed",
        nargs="+",
        dest="seed",
        help="A single or list of seeds",
    )
    tractography_input.add_argument(
        "-w",
        "--warps",
        dest="warps",
        nargs="+",
        help="Path to warps inside a subjects directory (can accept multiple arguments)",
    )
    tractography_input.add_argument(
        "-b",
        "--bpx",
        dest="bpx_path",
        help="Path to Bedpostx folder inside a subjects directory.",
    )
    tractography_input.add_argument(
        "-m",
        "--medial_wall",
        dest="medial_wall",
        nargs="+",
        help="""REQUIRED FOR SURFACE MODE: Medial wall file. 
        Use when doing whole brain surface tractography to provide medial wall.""",
    )
    tractography_input.add_argument(
        "-i",
        "--ref",
        dest="ref",
        help="Standard space reference image. Default is $FSLDIR/data/standard/MNI152_T1_2mm_brain.nii.gz",
    )
    tractography_input.add_argument(
        "-t",
        "--target",
        dest="target2",
        default=False,
        help="Name of target. If not given will create a whole mask from reference image",
    )
    tractography_input.add_argument(
        "-N",
        "--nsamples",
        dest="nsamples",
        default=1000,
        help="Number of samples per seed used in tractography (default = 1000)",
    )
    tractography_input.add_argument(
        "-mm",
        "--mm_res",
        dest="mm_res",
        default=2,
        help="Resolution of target image (Default = 2 mm)",
    )
    tractography_input.add_argument(
        "-p",
        "--ptx_options",
        dest="ptx_options",
        help="Path to ptx_options file for additional options",
        default=False,
    )

    tractography_input.add_argument(
        "-e",
        "--exclusion",
        dest="exclusion",
        default=False,
        help="""
        Path to an exclusion mask. Will reject pathways passing through locations given by this mask
      """,
    )
    tractography_input.add_argument(
        "-S",
        "--stop",
        dest="stop",
        default=False,
        nargs="*",
        help="""
        Use wtstop and stop in the tractography. Takes a file path to a json file containing stop and wtstop masks, JSON keys must be stopping_mask and wtstop_mask.
        Argument can be used with the --filetree, in that case no json file is needed.
      """,
    )
    parallel_args(base_args, col)
    cluster_args(base_args, col)

    no_args(base_args)
    args = base_args.parse_args()
    if args.verbose_help:
        verbose_help_message(base_args, nfact_pp_example_usage())

    return vars(args)


def nfact_pp_splash() -> str:
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
 _   _ ______   ___   _____  _____     ______ ______ 
| \ | ||  ___| /   \ /  __ \|_   _|    | ___ \| ___ \\
|  \| || |_   / /_\ \| /  \/  | |      | |_/ /| |_/ /
|     ||  _|  |  _  || |      | |      |  __/ |  __/ 
| |\  || |    | | | || \__/\  | |      | |    | |    
\_| \_/\_|    \_| |_/ \____/  \_/      \_|    \_|  
{col['reset']} 
"""


def nfact_pp_example_usage() -> str:
    """
    Function to return example usage

    Parameters
    ----------
    None

    Returns
    -------
    str: str object
    """
    col = colours()
    return f"""
Example Usage:
    {col['purple']}Seed mode:{col['reset']}
           nfact_pp --list_of_subjects /home/study/sub_list
               --outdir /home/study   
               --bpx_path /path_to/.bedpostX 
               --seeds /path_to/L.white.32k_fs_LR.surf.gii /path_to/R.white.32k_fs_LR.surf.gii 
               --rois /path_to/L.atlasroi.32k_fs_LR.shape.gii /path_to/R.atlasroi.32k_fs_LR.shape.gii 
               --warps /path_to/stand2diff.nii.gz /path_to/diff2stand.nii.gz 
               --n_cores 3 

    {col['pink']}Volume mode:{col['reset']}
            nfact_pp --list_of_subjects /home/study/sub_list  
                --bpx_path /path_to/.bedpostX 
                --seeds /path_to/L.white.nii.gz /path_to/R.white.nii.gz 
                --warps /path_to/stand2diff.nii.gz /path_to/diff2stand.nii.gz 
                --ref MNI152_T1_1mm_brain.nii.gz 
                --target dlpfc.nii.gz

    {col['darker_pink']}Filestree mode:{col['reset']}
        nfact_pp --filestree hcp
            --list_of_subjects /home/study/sub_list  
            --outdir /home/study 
            --n_cores 3 
"""
