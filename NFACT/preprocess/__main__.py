from .nfactpp import pre_processing
from .probtrackx_functions import to_use_gpu
from .nfactpp_args import nfact_pp_args
from .nfactpp_setup import (
    check_fsl_is_installed,
    check_ptx_options_are_valid,
    check_exclusion_mask,
)
from NFACT.base.utils import error_and_exit, colours
from NFACT.base.signithandler import Signit_handler
from NFACT.base.filesystem import read_file_to_list, make_directory
from NFACT.base.setup import (
    check_subject_exist,
    return_list_of_subjects_from_file,
    does_list_of_subjects_exist,
    check_arguments,
)
from NFACT.base.cluster_support import (
    Cluster_parameters,
    NoClusterQueuesException,
    no_cluster_queues,
)
import os
import shutil


def nfact_pp_main(arg: dict = None):
    """
    Main nfact_pp function.

    Parameters
    ----------
    arg: dict
        Set of command line arguments
        from nfact_pipeline
        Default is None

    Returns
    -------
    None
    """

    to_exit = False
    if not arg:
        arg = nfact_pp_args()
        to_exit = True

    handler = Signit_handler()
    col = colours()
    # Check that complusory arguments given
    if not arg["file_tree"]:
        check_arguments(arg, ["outdir", "list_of_subjects", "seed", "warps"])

    # Error handle if FSL not installed or loaded
    error_and_exit(
        check_fsl_is_installed(),
        "FSLDIR not in path. Check FSL is installed or has been loaded correctly",
    )

    # Error handle list of subjects
    error_and_exit(
        does_list_of_subjects_exist(arg["list_of_subjects"]),
        "List of subjects doesn't exist.",
    )
    arg["list_of_subjects"] = return_list_of_subjects_from_file(arg["list_of_subjects"])
    check_subject_exist(arg["list_of_subjects"])

    print(f"{col['deep_pink']}Checking:{col['reset']} GPU status")
    arg["gpu"] = to_use_gpu()
    print(f"{col['amethyst']}Using:{col['reset']} GPU\n") if arg["gpu"] else print(
        f"{col['amethyst']}Using:{col['reset']} CPU\n"
    )

    if arg["cluster"]:
        print(f"{col['deep_pink']}Checking:{col['reset']} Cluster Availability\n")
        try:
            arg = Cluster_parameters(arg).process_parameters()
            print(f"{col['amethyst']}Using: Cluster")
        except NoClusterQueuesException:
            arg["cluster"] = no_cluster_queues()

    print(
        f'{col["darker_pink"]}Filetree:{col["reset"]} {arg["file_tree"].lower()} '
    ) if arg["file_tree"] else None
    if not arg["ref"]:
        arg["ref"] = os.path.join(
            os.getenv("FSLDIR"), "data", "standard", "MNI152_T1_2mm_brain.nii.gz"
        )

    if arg["stop"] == []:
        arg["stop"] = True
    if type(arg["stop"]) is list:
        arg["stop"] = arg["stop"][0]

    if arg["exclusion"]:
        check_exclusion_mask(arg["exclusion"])

    if arg["ptx_options"]:
        try:
            arg["ptx_options"] = read_file_to_list(arg["ptx_options"])
            arg["ptx_options"] = [arg.strip() for arg in arg["ptx_options"]]

        except Exception as e:
            error_and_exit(False, f"Unable to read ptx_options text file due to {e}")
        check_ptx_options_are_valid(arg["ptx_options"])

    nfact_pp_directory = os.path.join(arg["outdir"], "nfact_pp")
    if arg["overwrite"]:
        if os.path.exists(nfact_pp_directory):
            print(f'{col["red"]}Overwriting:{col["reset"]} {nfact_pp_directory}.')
            shutil.rmtree(nfact_pp_directory, ignore_errors=True)

    make_directory(nfact_pp_directory)
    pre_processing(arg, handler)

    if to_exit:
        print("NFACT PP has Finished")
        exit(0)


if __name__ == "__main__":
    nfact_pp_main()
