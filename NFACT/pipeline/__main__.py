from .nfact_pipeline_args import nfact_args
from .nfact_pipeline_functions import (
    pipeline_args_check,
    build_module_arguments,
    write_decomp_list,
    compulsory_args_for_config,
    update_nfact_args_in_place,
)
from NFACT.base.config import get_nfact_arguments, process_dictionary_arguments
from NFACT.base.utils import error_and_exit, colours, Timer
from NFACT.base.filesystem import make_directory, load_json, read_file_to_list
from NFACT.base.setup import does_list_of_subjects_exist
from NFACT.preprocess.__main__ import nfact_pp_main
from NFACT.preprocess.nfactpp_args import nfact_pp_splash
from NFACT.decomp.__main__ import nfact_decomp_main
from NFACT.decomp.setup.args import nfact_decomp_splash
from NFACT.dual_reg.nfact_dr_args import nfact_dr_splash
from NFACT.dual_reg.__main__ import nfact_dr_main

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

    # Build out arguments from config file
    if args["input"]["config"]:
        print("Arguments taken from config file rather than command line")
        global_arguments = load_json(args["input"]["config"])
        nfact_pp_args = global_arguments["nfact_pp"]
        nfact_decomp_args = global_arguments["nfact_decomp"]
        nfact_dr_args = global_arguments["nfact_dr"]
        compulsory_args_for_config(global_arguments)

    update_nfact_args_in_place(global_arguments)
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
    if not global_arguments["global_input"]["skip"]:
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
