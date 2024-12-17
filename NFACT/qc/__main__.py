from .nfactQc_args import nfact_qc_args
from .nfactQc_functions import nfactQc_dir, check_Qc_dir
from NFACT.base.setup import check_arguments, check_algo, process_dim
from NFACT.base.utils import error_and_exit, colours
import os


def nfactQc_main():
    args = nfact_qc_args()
    col = colours()
    check_arguments(args, ["nfact_folder", "dim", "algo"])
    error_and_exit(
        os.path.exists(args["nfact_folder"]), "NFACT decomp directory does not exist."
    )

    args["algo"] = check_algo(args["algo"]).upper()
    args["dim"] = process_dim(args["dim"])
    nfactQc_directory = os.path.join(args["nfact_folder"], "nfactQc")
    print(f"{col['plum']}nfactQC directory:{col['reset']} {nfactQc_directory}")
    nfactQc_dir(nfactQc_directory, args["overwrite"])
    check_Qc_dir(
        nfactQc_directory,
        args["dim"],
        args["algo"],
    )
    # check args
    # make folder
    #
    # coverage_maps()


if __name__ == "__main__":
    nfact_qc_args()
