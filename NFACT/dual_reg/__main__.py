from .nfact_dr_args import nfactdr_args, nfact_dr_splash
from .nfact_dr_set_up import (
    check_nfact_decomp_directory,
    create_nfact_dr_folder_set_up,
)
from .nfact_dr_functions import get_paths
from NFACT.base.setup import (
    check_algo,
    get_subjects,
    check_subject_exist,
    check_arguments,
    process_input_imgs,
    check_seeds_surfaces,
    check_medial_wall,
)
from NFACT.base.utils import colours, nprint
from NFACT.base.logging import NFACT_logs
from NFACT.base.signithandler import Signit_handler
from NFACT.base.cluster_support import processing_cluster
from .local.local_run import run_locally
from .cluster.cluster_run import run_on_cluster
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

    if args["cluster"]:
        args["gpu"] = False
        args = processing_cluster(args)

    # Set up directory
    create_nfact_dr_folder_set_up(args["outdir"])

    # Process seeds
    args["seeds"] = process_input_imgs(args["seeds"])
    args["surface"] = check_seeds_surfaces(args["seeds"])
    args = check_medial_wall(args)

    # logging
    log = NFACT_logs(args["algo"], "DR", len(args["ptxdir"]))
    log.set_up_logging(os.path.join(args["outdir"], "nfact_dr", "logs"))
    log.inital_log(nfact_dr_splash())
    log.log(
        f"{col['plum']}Regresion Type{col['reset']}: {'Non-Negative' if args['algo'] == 'nmf' else 'Linear'}"
    )
    log.log_break("input")
    log.log_arguments(args)
    log.log_break("NFACT Decomp Workflow")
    nprint(f"{col['plum']}Number of subject:{col['reset']} {len(args['ptxdir'])} \n")

    nprint("\nDual Regression\n")
    nprint("-" * 100)

    if args["cluster"]:
        run_on_cluster(args, paths)
    else:
        run_locally(args, paths)

    nprint(f"{col['darker_pink']}NFACT_DR has finished{col['reset']}")
    log.clear_logging()

    if to_exit:
        exit(0)


if __name__ == "__main__":
    nfact_dr_main()
