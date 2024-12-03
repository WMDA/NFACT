from .dual_regression import Dual_regression
from .nfact_dr_args import nfactdr_args, nfact_dr_splash
from .nfact_dr_set_up import (
    check_nfact_decomp_directory,
    create_nfact_dr_folder_set_up,
)
from .nfact_dr_functions import get_group_level_components, get_paths

from NFACT.base.setup import (
    check_algo,
    get_subjects,
    check_subject_exist,
    check_arguments,
    process_input_imgs,
    check_seeds_surfaces,
)
from NFACT.base.utils import colours, nprint
from NFACT.base.logging import NFACT_logs
from NFACT.base.signithandler import Signit_handler
import os


def nfact_dr_main(args: dict = None) -> None:
    """
    Main function for NFACT DR.

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

    Signit_handler()
    col = colours()
    to_exit = False

    if not args:
        args = nfactdr_args()
        to_exit = True

    # Do argument checking
    check_arguments(args, ["seeds", "list_of_subjects", "algo"])
    args["algo"] = check_algo(args["algo"])

    # Get component paths
    paths = get_paths(args)

    # check subjects exist
    args = get_subjects(args)
    check_subject_exist(args["ptxdir"])
    check_nfact_decomp_directory(paths["component_path"], paths["group_average_path"])

    # Set up directory
    create_nfact_dr_folder_set_up(args["outdir"])

    # Process seeds
    args["seeds"] = process_input_imgs(args["seeds"])
    args["surface"] = check_seeds_surfaces(args["seeds"])
    if args["surface"] and args["medial_wall"]:
        args["medial_wall"] = process_input_imgs(args["medial_wall"])
    else:
        args["medial_wall"] = False
    # logging
    log = NFACT_logs(args["algo"], "DR", len(args["ptxdir"]))
    log.set_up_logging(os.path.join(args["outdir"], "nfact_dr", "logs"))
    log.inital_log(nfact_dr_splash())
    log.log(
        f"{col['plum']}Regresion Type{col['reset']}: {'Non-Negative' if args['algo'] == 'nmf' else 'Linear'}"
    )
    log.log_break("input")
    log.log_arguments(args)
    log.log_break("nfact decomp workflow")
    nprint(
        f"{col['plum']}Performing dual regression on {len(args['ptxdir'])} subjects{col['reset']}\n"
    )

    nprint("Obtaining components\n")
    components = get_group_level_components(
        paths["component_path"], paths["group_average_path"], args["seeds"]
    )

    dual_reg = Dual_regression(
        algo=args["algo"],
        normalise=args["normalise"],
        parallel=False,
        list_of_files=args["ptxdir"],
        component=components,
        seeds=args["seeds"],
        nfact_directory=os.path.join(args["outdir"], "nfact_dr"),
        medial_wall=args["medial_wall"],
    )
    dual_reg.run()

    nprint(f"{col['darker_pink']}NFACT_DR has finished{col['reset']}")
    log.clear_logging()

    if to_exit:
        exit(0)


if __name__ == "__main__":
    nfact_dr_main()
