from .nfactpp import pre_processing
from .probtrackx_functions import to_use_gpu
from .nfactpp_functions import seedref
from .nfactpp_args import nfact_pp_args
from .nfactpp_setup import check_ptx_options_are_valid, check_provided_img
from NFACT.base.utils import error_and_exit, colours
from NFACT.base.signithandler import Signit_handler
from NFACT.base.filesystem import read_file_to_list, make_directory, delete_folder
from NFACT.base.setup import (
    check_subject_exist,
    return_list_of_subjects_from_file,
    does_list_of_subjects_exist,
    check_arguments,
    check_fsl_is_installed,
)
from NFACT.base.cluster_support import processing_cluster
import os


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

    if arg["n_cores"] and arg["cluster"]:
        error_and_exit(
            False,
            "Unclear whether to parallel process locally or to submit to cluster. Remove either --n_cores or --cluster",
        )
    # Error handle if FSL not installed or loaded
    check_fsl_is_installed()

    # Error handle list of subjects
    error_and_exit(
        does_list_of_subjects_exist(arg["list_of_subjects"]),
        "List of subjects doesn't exist.",
    )
    arg["list_of_subjects"] = return_list_of_subjects_from_file(arg["list_of_subjects"])
    check_subject_exist(arg["list_of_subjects"])

    if not arg["gpu"]:
        print(f"{col['deep_pink']}Checking:{col['reset']} GPU status")
        arg["gpu"] = to_use_gpu()
        print(f"{col['amethyst']}Using:{col['reset']} GPU\n") if arg["gpu"] else print(
            f"{col['amethyst']}Using:{col['reset']} CPU\n"
        )
    else:
        print(
            f"{col['amethyst']}Using:{col['reset']} GPU (Override option given. This may cause nfact_pp to crash if no GPU available)\n"
        )

    if arg["cluster"]:
        arg = processing_cluster(arg)

    print(
        f'{col["darker_pink"]}Filetree:{col["reset"]} {arg["file_tree"].lower()} '
    ) if arg["file_tree"] else None

    if arg["stop"] == []:
        arg["stop"] = True
    if type(arg["stop"]) is list:
        arg["stop"] = arg["stop"][0]

    if arg["exclusion"]:
        check_provided_img(arg["exclusion"], "Cannot find exclusion mask")

    if arg["ptx_options"]:
        try:
            arg["ptx_options"] = read_file_to_list(arg["ptx_options"])
            arg["ptx_options"] = [arg.strip() for arg in arg["ptx_options"]]

        except Exception as e:
            error_and_exit(False, f"Unable to read ptx_options text file due to {e}")
        check_ptx_options_are_valid(arg["ptx_options"])

    arg["seedref"] = seedref(arg["seedref"])

    nfact_pp_directory = os.path.join(arg["outdir"], "nfact_pp")
    if arg["overwrite"]:
        delete_folder(nfact_pp_directory)

    make_directory(nfact_pp_directory)
    pre_processing(arg, handler)

    if to_exit:
        print("NFACT PP has Finished")
        exit(0)


if __name__ == "__main__":
    nfact_pp_main()
