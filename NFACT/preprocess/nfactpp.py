# NFACT functions
from .nfactpp_setup import (
    check_seeds_surfaces,
    nfact_pp_folder_setup,
    check_roi_seed_len,
    load_file_tree,
)
from .nfactpp_functions import (
    get_file,
    filetree_get_files,
    process_filetree_args,
    rename_seed,
    stoppage,
    get_stop_files_filestree,
)
from .probtrackx_functions import (
    build_probtrackx2_arguments,
    write_options_to_file,
    Probtrackx,
    get_target2,
    seeds_to_gifti,
)
from NFACT.base.utils import colours, error_and_exit
from NFACT.base.filesystem import load_json
import os
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

    print(
        f'{col["plum"]}Number of subjects:{col["reset"]} ', len(arg["list_of_subjects"])
    )
    subjects_commands = []
    print("\n")
    print("SUBJECT SETUP\n")
    print("-" * 80)
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
            seed_names = rename_seed(seed)
            for img in range(0, len(roi)):
                seeds_to_gifti(
                    seed[img],
                    roi[img],
                    os.path.join(
                        nfactpp_diretory, "files", f"{seed_names[img]}.surf.gii"
                    ),
                )
            asc_seeds = [
                os.path.join(nfactpp_diretory, "files", f"{seed}.surf.gii")
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

        if arg["stop"]:
            print(f"{col['pink']}Processing:{col['reset']} stop and wtstop files")
            if arg["file_tree"]:
                stop_files = get_stop_files_filestree(arg["file_tree"], sub_id)
            else:
                stop_files = load_json(arg["stop"])
            stop_ptx = stoppage(
                sub, os.path.join(nfactpp_diretory, "files"), stop_files
            )
            if arg["ptx_options"]:
                [arg["ptx_options"].append(command) for command in stop_ptx]
            else:
                arg["ptx_options"] = stop_ptx

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
    print("\n")
    print("TRACTOGRAPHY\n")
    print("-" * 80)
    # Running probtrackx2
    Probtrackx(subjects_commands, arg["n_cores"])
