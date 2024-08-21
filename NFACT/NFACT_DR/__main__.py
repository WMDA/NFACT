from NFACT.NFACT_base.utils import colours
from .dual_regression import Dual_regression
from .nfact_dr_args import nfactdr_args
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
)
from NFACT.NFACT_base.signithandler import Signit_handler


def nfact_dr_main() -> None:
    """
    Main function for NFACT DR.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """

    handler = Signit_handler()
    col = colours()
    args = nfactdr_args()

    # Do argument checking

    args["algo"] = check_algo(args["algo"])
    check_compulsory_arguments(args)
    # check subjects exist
    args = get_subjects(args)
    check_subject_exist(args["ptxdir"])
    check_nfact_directory(args["nfact_dir"], args["algo"])
    create_nfact_dr_folder_set_up(args["nfact_dir"])

    print(
        f"{col['plum']}Performing dual regression on {len(args['ptxdir'])} subjects{col['reset']}"
    )

    get_group_level_components(args["nfact_dir"], args["algo"])
    exit(0)
    dual_reg = Dual_regression(
        algo=args["algo"],
        normalise=args["normalise"],
        parallel=False,
        list_of_files=args["ptxdir"],
        component=components,
        save_type=img_type,
        seeds=seeds,
        nfact_directory=args["nfact_dir"],
    )
    dual_reg.run()
    return None


if __name__ == "__main__":
    nfact_dr_main()
