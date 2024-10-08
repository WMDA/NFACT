# NFACT functions
from .nfactpp_setup import (
    check_seeds_surfaces,
    nfact_pp_folder_setup,
    check_roi_seed_len,
    load_file_tree,
)
from .nfactpp_functions import (
    update_seeds_file,
    get_file,
    filetree_get_files,
    process_filetree_args,
)
from .probtrackx_functions import (
    build_probtrackx2_arguments,
    write_options_to_file,
    Probtrackx,
    get_target2,
    seeds_to_ascii,
)
from NFACT.base.utils import colours, error_and_exit

import os
import re
import shutil


def pre_processing(arg: dict, handler) -> None:
    """
    Main function for nfact PP

    Parameters
    ----------
    arg: dict
       dictionary of command line
       arguments

    Returns
    -------
    None
    """
    col = colours()

    if arg["file_tree"]:
        print(f'{col["plum"]}Filetree {arg["file_tree"].lower()} given {col["reset"]}')
        arg["file_tree"] = load_file_tree(f"{arg['file_tree'].lower()}.tree")

        # load a random subjects seed and ROI to check its type
        arg["seed"] = [filetree_get_files(arg["file_tree"], "sub1", "L", "seed")]

        # Needed for checking if seed is surface
        arg["rois"] = ["filestree"]

    arg["surface"] = check_seeds_surfaces(arg["seed"])

    if arg["surface"]:
        print(f'{col["darker_pink"]}Surface seeds mode{col["reset"]}')
        check_roi_seed_len(arg["seed"], arg["rois"])
    else:
        print(f'{col["darker_pink"]}Volume seed mode{col["reset"]}')

    print("Number of subjects: ", len(arg["list_of_subjects"]))
    subjects_commands = []
    for sub in arg["list_of_subjects"]:
        sub_id = os.path.basename(sub)
        print(f"\n{col['pink']}Setting up:{col['reset']} {sub_id}")
        if arg["file_tree"]:
            arg = process_filetree_args(arg, sub_id)
        seed = get_file(arg["seed"], sub)
        seed_text = "\n".join(seed)
        # using this function not to return a file but check it is an imaging file
        get_file(arg["warps"], sub)
        nfactpp_diretory = os.path.join(arg["outdir"], "nfact_pp", sub_id)
        nfact_pp_folder_setup(nfactpp_diretory)
        [
            shutil.copyfile(
                seed_location,
                os.path.join(
                    nfactpp_diretory, "files", os.path.basename(seed_location)
                ),
            )
            for seed_location in seed
        ]
        if arg["surface"]:
            roi = get_file(arg["rois"], sub)
            seed_names = [
                re.sub(r"..ii", "", os.path.basename(seeds)) for seeds in seed
            ]
            for img in range(0, len(roi)):
                seeds_to_ascii(
                    seed[img],
                    roi[img],
                    os.path.join(nfactpp_diretory, "files", f"{seed_names[img]}.asc"),
                )
            asc_seeds = [
                os.path.join(nfactpp_diretory, "files", f"{seed}.asc")
                for seed in seed_names
            ]
            seed_text = "\n".join(asc_seeds)
        error_and_exit(write_options_to_file(nfactpp_diretory, seed_text))
        if not arg["target2"]:
            print(
                f'{col["purple"]}No target given. Creating a whole brain target.{col["reset"]}'
            )
            get_target2(
                arg["ref"],
                os.path.join(nfactpp_diretory, "files", "target2"),
                arg["mm_res"],
                arg["ref"],
                "nearestneighbour",
            )
        subjects_commands.append(
            build_probtrackx2_arguments(
                arg,
                sub,
                ptx_options=arg["ptx_options"],
            )
        )

    # This supresses the signit kill message or else it prints it off multiple times for each core
    if arg["n_cores"]:
        handler.set_suppress_messages = True
    # Running probtrackx2
    Probtrackx(subjects_commands, arg["cluster"], arg["n_cores"])
    print(arg)
    if arg["surface"]:
        [
            update_seeds_file(
                os.path.join(
                    arg["outdir"], "nfact_pp", os.path.basename(sub), "seeds.txt"
                )
            )
            for sub in arg["list_of_subjects"]
        ]
