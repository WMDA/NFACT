from NFACT.NFACT_base.utils import colours, nprint
from NFACT.NFACT_base.logging import NFACT_logs
from NFACT.NFACT_base.signithandler import Signit_handler
from .dual_regression import Dual_regression
from .nfact_dr_args import nfactdr_args, nfact_dr_splash
from .nfact_dr_set_up import (
    check_nfact_directory,
    check_compulsory_arguments,
    create_nfact_dr_folder_set_up,
)
from .nfact_dr_functions import get_group_level_components

from NFACT.NFACT_base.setup import (
    check_algo,
    get_subjects,
    check_subject_exist,
    process_seeds,
    seed_type,
)

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

    handler = Signit_handler()
    col = colours()
    if not args:
        args = nfactdr_args()

    # Do argument checking

    args["algo"] = check_algo(args["algo"])
    check_compulsory_arguments(args)
    # check subjects exist
    args = get_subjects(args)
    check_subject_exist(args["ptxdir"])
    check_nfact_directory(args["nfact_dir"], args["algo"])
    create_nfact_dr_folder_set_up(args["nfact_dir"])
    seeds = process_seeds(args["seeds"])
    img_type = seed_type(seeds)

    log = NFACT_logs(args["algo"], "DR", len(args["ptxdir"]))
    log.set_up_logging(os.path.join(args["nfact_dir"], "nfact_dr", "logs"))
    log.inital_log(nfact_dr_splash())
    log.log_break("input")
    log.log_arguments(args)
    log.log_break("nfact decomp workflow")
    nprint(
        f"{col['plum']}Performing dual regression on {len(args['ptxdir'])} subjects{col['reset']}\n"
    )

    nprint("Obtaining components\n")

    components = get_group_level_components(args["nfact_dir"], args["algo"], seeds)

    dual_reg = Dual_regression(
        algo=args["algo"],
        normalise=args["normalise"],
        parallel=False,
        list_of_files=args["ptxdir"],
        component=components,
        save_type=img_type,
        seeds=seeds,
        nfact_directory=os.path.join(args["nfact_dir"], "nfact_dr"),
    )
    dual_reg.run()

    nprint(f"{col['darker_pink']}NFACT_DR has finished{col['reset']}")


if __name__ == "__main__":
    nfact_dr_main()
    exit(0)
