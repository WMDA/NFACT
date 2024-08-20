from NFACT.NFACT_base.utils import colours
from NFACT.NFACT_DR.dual_regression import Dual_regression
from NFACT.NFACT_DR.nfact_dr_args import nfact_dr_args
from NFACT.NFACT_base.setup import check_algo, get_subjects, check_subject_exist
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
    args = nfact_dr_args()

    # Do argument checking
    args["algo"] = check_algo(args["algo"])

    # check subjects exist
    args = get_subjects(args)
    check_subject_exist(args["ptxdir"])
    print(args)
    exit(0)
    print(
        f"{col['plum']}Performing dual regression on {len(args['ptxdir'])} subjects{col['reset']}"
    )
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
