import argparse
from NFACT.NFACT_base.utils import colours, no_args


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
    option = argparse.ArgumentParser(
        prog="nfact_pp",
        description=print(nfact_pp_splash()),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=nfact_pp_example_usage(),
    )
    col = colours()
    option.add_argument(
        "-l",
        "--list_of_subjects",
        dest="list_of_subjects",
        help=f"""{col['red']}REQUIRED{col['reset']} A list of subjects in text form. If not provided NFACT PP will use all subjects in the study folder. 
        All subjects need full file path to subjects directory""",
    )
    option.add_argument(
        "-o",
        "--outdir",
        dest="outdir",
        help=f"{col['red']}REQUIRED{col['reset']} Directory to save results in",
    )
    option.add_argument(
        "-s",
        "--seed",
        nargs="+",
        dest="seed",
        help=f"{col['red']}REQUIRED{col['reset']} A single or list of seeds",
    )
    option.add_argument(
        "-w",
        "--warps",
        dest="warps",
        nargs="+",
        help=f"{col['red']}REQUIRED{col['reset']} Path to warps inside a subjects directory (can accept multiple arguments)",
    )
    option.add_argument(
        "-i",
        "--ref",
        dest="ref",
        help="Standard space reference image. Default is $FSLDIR/data/standard/MNI152_T1_2mm_brain.nii.gz",
    )
    option.add_argument(
        "-b",
        "--bpx",
        dest="bpx_path",
        help="Path to Bedpostx folder inside a subjects directory.",
    )
    option.add_argument(
        "-t",
        "--target",
        dest="target2",
        default=None,
        help="Name of target. If not given will create a whole mask from reference image",
    )

    option.add_argument(
        "-r",
        "--rois",
        dest="rois",
        nargs="+",
        help="A single or list of ROIS",
    )
    option.add_argument(
        "-H",
        "--hcp_stream",
        dest="hcp_stream",
        action="store_true",
        help="HCP stream option. Will search through HCP folder structure for L/R white.32k_fs_LR.surf.gii and ROIs. Then performs suface seed stream",
    )
    option.add_argument(
        "-N",
        "--nsamples",
        dest="nsamples",
        default=1000,
        help="Number of samples per seed used in tractography (default = 1000)",
    )
    option.add_argument(
        "-m",
        "--mm_res",
        dest="mm_res",
        default=2,
        help="Resolution of target image (Default = 2 mm)",
    )
    option.add_argument(
        "-p",
        "--ptx_options",
        dest="ptx_options",
        help="Path to ptx_options file for additional options",
        default=False,
    )
    option.add_argument(
        "-n",
        "--n_cores",
        dest="n_cores",
        help="If should parallel process and with how many cores",
        default=False,
    )
    option.add_argument(
        "-C",
        "--cluster",
        dest="cluster",
        action="store_true",
        default=False,
        help=f"Run on cluster. {col['red']}Currently not implemented{col['reset']} ",
    )
    option.add_argument(
        "-O",
        "--overwrite",
        dest="overwrite",
        action="store_true",
        default=False,
        help="Overwrite previous file structure",
    )
    no_args(option)

    return vars(option.parse_args())


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
    {col['purple']}Seed surface mode:{col['reset']}
           nfact_pp --list_of_subjects /home/mr_robot/sub_list  
               --bpx_path Diffusion.bedpostX 
               --seeds L.white.32k_fs_LR.surf.gii R.white.32k_fs_LR.surf.gii 
               --rois L.atlasroi.32k_fs_LR.shape.gii  R.atlasroi.32k_fs_LR.shape.gii 
               --warps standard2acpc_dc.nii.gz acpc_dc2standard.nii.gz 
               --n_cores 3 

    {col['pink']}Volume surface mode:{col['reset']}
            nfact_pp --list_of_subjects /home/mr_robot/sub_list  
                --bpx_path Diffusion.bedpostX 
                --seeds L.white.nii.gz R.white.nii.gz 
                --warps standard2acpc_dc.nii.gz acpc_dc2standard.nii.gz 
                --ref MNI152_T1_1mm_brain.nii.gz 
                --target dlpfc.nii.gz

    {col['darker_pink']}HCP mode:{col['reset']}
        nfact_pp --hcp_stream
            --list_of_subjects /home/mr_robot/for_axon/nfact_dev/sub_list  
            --n_cores 3 
            \n
"""
