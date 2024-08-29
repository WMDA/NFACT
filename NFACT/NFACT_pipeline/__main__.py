from .nfact_pipeline_args import nfact_args
from .nfact_pipeline_functions import (
    pipeline_args_check,
    build_module_arguments,
    write_decomp_list,
)
from NFACT.NFACT_base.config import get_nfact_arguments
from NFACT.NFACT_base.utils import error_and_exit, colours
from NFACT.NFACT_base.filesystem import make_directory, read_file_to_list
from NFACT.NFACT_base.setup import does_list_of_subjects_exist
from NFACT.NFACT_PP.__main__ import nfact_pp_main
from NFACT.NFACT_PP.nfactpp_args import nfact_pp_splash
from NFACT.NFACT_decomp.__main__ import nfact_decomp_main
from NFACT.NFACT_decomp.setup.args import nfact_decomp_splash
from NFACT.NFACT_DR.nfact_dr_args import nfact_dr_splash
from NFACT.NFACT_DR.__main__ import nfact_dr_main

import os
import shutil


def nfact_pipeline_main(args: dict) -> None:
    """
    Main function for NFACT pipeline

    Parameters
    ----------
    None

    Returns
    ------
    None
    """

    col = colours()

    if not args["input"]["config"]:
        pipeline_args_check(args)
        global_arguments = get_nfact_arguments()

    nfact_pp_args = build_module_arguments(
        global_arguments["nfact_pp"], args, "pre_process"
    )
    error_and_exit(
        does_list_of_subjects_exist(nfact_pp_args["list_of_subjects"]),
        "List of subjects doesn't exist. Used in this mode NFACT PP cannot get subjects from folder.",
    )

    nfact_decomp_args = build_module_arguments(
        global_arguments["nfact_decomp"], args, "decomp"
    )

    nfact_dr_args = build_module_arguments(global_arguments["nfact_dr"], args, "decomp")
    nfact_tmp_location = os.path.join(nfact_decomp_args["outdir"], ".nfact_tmp")

    make_directory(nfact_tmp_location, overwrite=True)
    write_decomp_list(
        nfact_pp_args["list_of_subjects"], nfact_pp_args["out"], nfact_tmp_location
    )

    if not args["input"]["config"]:
        from NFACT.NFACT_PP.nfactpp_setup import check_fsl_is_installed
        from NFACT.NFACT_PP.probtrackx_functions import get_probtrack2_arguments

        print("Checking GPU status")
        error_and_exit(
            check_fsl_is_installed(),
            "FSLDIR not in path. Check FSL is installed or has been loaded correctly",
        )
        nfact_pp_args["gpu"] = True if get_probtrack2_arguments(bin=True) else False
        print("GPU found, Using GPU\n") if nfact_pp_args["gpu"] else print(
            "No GPU. USing CPU version\n"
        )

    print(f'{col["plum"]}Running NFACT PP{col["reset"]}')
    print(nfact_pp_splash())

    nfact_pp_main(nfact_pp_args)
    print(f'{col["plum"]}Setting up and running NFACT DR{col["reset"]}')

    nfact_decomp_args["list_of_subjects"] = os.path.join(
        os.path.dirname(nfact_pp_args["list_of_subjects"]),
        ".nfact_tmp",
        "nfact_decomp_sub_list",
    )

    sub_nfactpp_dir = read_file_to_list(nfact_pp_args["list_of_subjects"])[0]
    shutil.copy(
        os.path.join(sub_nfactpp_dir, nfact_pp_args["out"], "seeds.txt"),
        nfact_tmp_location,
    )

    nfact_decomp_args["seeds"] = os.path.join(nfact_tmp_location, "seeds.txt")

    print(nfact_decomp_splash())
    nfact_decomp_main(nfact_decomp_args)

    print(f'{col["plum"]}Setting up and running NFACT DR{col["reset"]}')
    shutil.move(
        nfact_tmp_location, os.path.join(nfact_decomp_args["outdir"], "nfact", "files")
    )

    try:
        shutil.rmtree(nfact_tmp_location)
    except Exception:
        pass

    nfact_dr_args["nfact_dir"] = os.path.join(nfact_decomp_args["outdir"], "nfact")
    nfact_dr_args["seeds"] = os.path.join(
        nfact_dr_args["nfact_dir"], "files", "seeds.txt"
    )

    print(nfact_dr_splash())
    nfact_dr_main()
    exit(0)


if __name__ == "__main__":
    args = nfact_args()
    nfact_pipeline_main(args)
