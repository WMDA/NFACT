from .nfactQc_args import nfact_qc_args
from NFACT.base.setup import check_arguments
from NFACT.base.utils import error_and_exit
import os


def nfactQc_main():
    args = nfact_qc_args()
    check_arguments(args, ["nfact_folder", "dim", "algo"])
    error_and_exit(
        os.path.exists(args["nfact_folder"]), "NFACT decomp directory does not exist."
    )
    args["algo"] = args["algo"].upper()
    print(args)
    # check args
    # make folder
    #
    # coverage_maps()


if __name__ == "__main__":
    nfact_qc_args()
