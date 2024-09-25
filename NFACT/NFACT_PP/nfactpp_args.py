import argparse
from NFACT.NFACT_base.utils import colours


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
        help="""A list of subjects in text form. If not provided NFACT PP will use all subjects in the study folder. 
        All subjects need full file path to subjects directory""",
    )

    option.add_argument(
        "-i",
        "--ref",
        dest="ref",
        help=f"{col['red']}REQUIRED{col['reset']} Standard space reference image",
    )

    option.add_argument(
        "-f",
        "--study_folder",
        dest="study_folder",
        help="In place of a list of subjects a study folder can be given to get subject.",
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
        help="Path to target image. If not given will create a whole mask from reference image",
    )
    option.add_argument(
        "-s",
        "--seed",
        nargs="+",
        dest="seed",
        help="A single or list of seeds",
    )
    option.add_argument(
        "-r",
        "--rois",
        dest="rois",
        nargs="+",
        help="A single or list of ROIS",
    )
    option.add_argument(
        "-w",
        "--warps",
        dest="warps",
        nargs="+",
        help="Path to warps inside a subjects directory (can accept multiple arguments)",
    )
    option.add_argument(
        "-o",
        "--out",
        dest="out",
        help="Directory to save results in",
    )
    option.add_argument(
        "-H",
        "--hcp_stream",
        dest="hcp_stream",
        action="store_true",
        help="HCP stream option. Will search through HCP folder structure for L/R white.32k_fs_LR.surf.gii and ROIs. Then performs suface seed stream",
    )
    option.add_argument(
        "-g",
        "--gpu",
        dest="gpu",
        action="store_true",
        help="Use GPU version",
    )
    option.add_argument(
        "-N",
        "--nsamples",
        dest="nsamples",
        default=1000,
        help="Number of samples per seed used in tractography (default = 1000)",
    )
    option.add_argument(
        "-R",
        "--res",
        dest="res",
        default=2,
        help="Resolution of NMF volume components (Default = 2 mm)",
    )
    option.add_argument(
        "-P",
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
        help="Run on cluster",
    )
    option.add_argument(
        "-D",
        "--dont_log",
        dest="dont_log",
        action="store_true",
        default=False,
        help="Run on cluster",
    )
    option.add_argument(
        "-O",
        "--overwrite",
        dest="overwrite",
        action="store_true",
        default=False,
        help="Overwrite previous file structure",
    )
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
           nfact_pp --study_folder /home/mr_robot/subjects 
               --list /home/mr_robot/sub_list  
               --bpx_path Diffusion.bedpostX 
               --seeds L.white.32k_fs_LR.surf.gii R.white.32k_fs_LR.surf.gii 
               --rois L.atlasroi.32k_fs_LR.shape.gii  R.atlasroi.32k_fs_LR.shape.gii 
               --warps standard2acpc_dc.nii.gz acpc_dc2standard.nii.gz 
               --image_standard_space $FSLDIR/data/standard/MNI152_T1_2mm_brain.nii.gz 
               --gpu --n_cores 3 
           \n
    {col['pink']}Volume surface mode:{col['reset']}
            nfact_pp --study_folder /home/mr_robot/subjects 
                --list /home/mr_robot/sub_list  
                --bpx_path Diffusion.bedpostX 
                --seeds L.white.nii.gz R.white.nii.gz 
                --warps standard2acpc_dc.nii.gz acpc_dc2standard.nii.gz 
                --image_standard_space $FSLDIR/data/standard/MNI152_T1_2mm_brain.nii.gz 
                --target dlpfc.nii.gz
                --gpu --n_cores 3 
        \n
    {col['darker_pink']}HCP mode:{col['reset']}
        nfact_pp --hcp_stream
            --study_folder /home/mr_robot/subjects  
            --list /home/mr_robot/for_axon/nfact_dev/sub_list  
            --image_standard_space $FSLDIR/data/standard/MNI152_T1_2mm_brain.nii.gz 
            --gpu --n_cores 3 
            \n
"""
