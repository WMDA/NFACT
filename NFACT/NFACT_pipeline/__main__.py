from .nfact_pipeline_args import nfact_args
from .nfact_pipeline_functions import (
    pipeline_args_check,
    build_module_arguments,
    write_decomp_list,
)
from NFACT.NFACT_base.config import get_nfact_arguments, process_dictionary_arguments
from NFACT.NFACT_base.utils import error_and_exit, colours, Timer
from NFACT.NFACT_base.filesystem import make_directory, load_json, read_file_to_list
from NFACT.NFACT_base.setup import does_list_of_subjects_exist
from NFACT.NFACT_PP.__main__ import nfact_pp_main
from NFACT.NFACT_PP.nfactpp_args import nfact_pp_splash
from NFACT.NFACT_decomp.__main__ import nfact_decomp_main
from NFACT.NFACT_decomp.setup.args import nfact_decomp_splash
from NFACT.NFACT_DR.nfact_dr_args import nfact_dr_splash
from NFACT.NFACT_DR.__main__ import nfact_dr_main

import os
import shutil


def nfact_pipeline_main() -> None:
    """
    Main function for NFACT pipeline

    Parameters
    ----------
    None

    Returns
    ------
    None
    """

    time = Timer()
    time.tic()
    col = colours()
    args = nfact_args()

    # Build out command line argument input
    if not args["input"]["config"]:
        print("Building out NFACT arguments. Check logs for specifics")
        from NFACT.NFACT_PP.nfactpp_setup import check_fsl_is_installed
        from NFACT.NFACT_PP.probtrackx_functions import get_probtrack2_arguments

        pipeline_args_check(args)

        global_arguments = get_nfact_arguments()
        nfact_pp_args = build_module_arguments(
            global_arguments["nfact_pp"], args, "pre_process"
        )
        nfact_decomp_args = build_module_arguments(
            global_arguments["nfact_decomp"], args, "decomp"
        )
        nfact_dr_args = build_module_arguments(
            global_arguments["nfact_dr"], args, "decomp"
        )

        # Check to use probtrackx GPU or not
        if not args["input"]["skip"]:
            print("Checking GPU status")
            error_and_exit(
                check_fsl_is_installed(),
                "FSLDIR not in path. Check FSL is installed or has been loaded correctly",
            )
            nfact_pp_args["gpu"] = True if get_probtrack2_arguments(bin=True) else False
            print("GPU found, Using GPU\n") if nfact_pp_args["gpu"] else print(
                "No GPU. USing CPU version\n"
            )

    # Build out arguments from config file
    if args["input"]["config"]:
        print(
            "WARNING: No argument checking of config files occurs before modules are loaded."
        )
        global_arguments = load_json(args["input"]["config"])
        nfact_pp_args = global_arguments["nfact_pp"]
        nfact_decomp_args = global_arguments["nfact_decomp"]
        nfact_dr_args = global_arguments["nfact_dr"]

    nfact_pp_args["outdir"] = os.path.join(nfact_pp_args["outdir"], "nfact")
    nfact_decomp_args["outdir"] = os.path.join(nfact_decomp_args["outdir"], "nfact")
    nfact_dr_args["outdir"] = os.path.join(nfact_dr_args["outdir"], "nfact")
    nfact_dr_args["nfact_decomp_dir"] = os.path.join(
        nfact_dr_args["outdir"], "nfact_decomp"
    )

    print(f'NFACT directory is at {nfact_pp_args["outdir"]}')
    make_directory(nfact_pp_args["outdir"], ignore_errors=True)

    # Build out temporary locations of arguments
    nfact_tmp_location = os.path.join(nfact_decomp_args["outdir"], ".nfact_tmp")
    nfact_decomp_args["list_of_subjects"] = os.path.join(
        nfact_tmp_location,
        "nfact_decomp_sub_list",
    )
    nfact_decomp_args["seeds"] = os.path.join(nfact_tmp_location, "seeds.txt")

    nfact_dr_args["seeds"] = os.path.join(
        nfact_dr_args["outdir"], "nfact_decomp", "files", "seeds.txt"
    )
    nfact_dr_args["list_of_subjects"] = os.path.join(
        nfact_dr_args["outdir"], "nfact_decomp", "files", "nfact_decomp_sub_list"
    )

    # Clean str instances of bool to actual bool type
    global_arguments = process_dictionary_arguments(global_arguments)
    nfact_pp_args = global_arguments["nfact_pp"]
    nfact_decomp_args = global_arguments["nfact_decomp"]
    nfact_dr_args = global_arguments["nfact_dr"]

    # Create tmp directory and decomposition subject list
    make_directory(nfact_tmp_location, overwrite=True)
    error_and_exit(
        does_list_of_subjects_exist(nfact_pp_args["list_of_subjects"]),
        "List of subjects doesn't exist. Used in this mode NFACT PP cannot get subjects from folder.",
    )

    write_decomp_list(
        nfact_pp_args["list_of_subjects"], nfact_pp_args["outdir"], nfact_tmp_location
    )

    # Run NFACT_PP
    if not args["input"]["skip"]:
        print(f'{col["plum"]}Running NFACT PP{col["reset"]}')
        print(nfact_pp_splash())
        nfact_pp_main(nfact_pp_args)

        print(f'{col["pink"]}\nFinished running NFACT_PP{col["reset"]}')
        print("-" * 70)
    else:
        print("Skipping NFACT_PP")
        nfact_pp_args["list_of_subjects"] = read_file_to_list(
            nfact_pp_args["list_of_subjects"]
        )

    # Run NFACT_decomp
    print(f'{col["plum"]}\nSetting up and running NFACT Decomp{col["reset"]}')
    try:
        shutil.copy(
            os.path.join(
                nfact_pp_args["outdir"],
                "nfact_pp",
                os.path.basename(nfact_pp_args["list_of_subjects"][0]),
                "seeds.txt",
            ),
            nfact_tmp_location,
        )
    except FileNotFoundError:
        error_and_exit(
            False,
            "NFACT PP has not been ran which NFACT needs. If pre-processing is seperate from decomposition please run the modules individually",
        )

    print(nfact_decomp_splash())
    nfact_decomp_main(nfact_decomp_args)
    print(f'{col["pink"]}\nFinished running NFACT_decomp{col["reset"]}')
    print("-" * 70)

    # Clean up
    try:
        shutil.move(
            nfact_tmp_location,
            os.path.join(nfact_decomp_args["outdir"], "nfact_decomp", "files"),
        )
    except shutil.Error:
        pass

    try:
        shutil.rmtree(nfact_tmp_location)
    except Exception:
        pass

    # Run NFACT_DR
    if len(nfact_pp_args["list_of_subjects"]) > 1:
        print(f'{col["plum"]}Setting up and running NFACT DR{col["reset"]}')
        print(nfact_dr_splash())
        nfact_dr_main(nfact_dr_args)
        print(f'{col["pink"]}\nFinished running NFACT_DR{col["reset"]}')
        print("-" * 70)
    else:
        print("Only one subject given. Skipping dual regression")

    # Exit
    print(f"Decomposition pipeline took {time.toc()} seconds")
    print("Finished")
    exit(0)


if __name__ == "__main__":
    nfact_pipeline_main()
