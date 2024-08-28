from .nfact_pipeline_args import nfact_args
from .nfact_pipeline_functions import pipeline_args_check, build_module_arguments
from NFACT.NFACT_base.config import get_nfact_arguments


def nfact_pipeline_main() -> None:
    args = nfact_args()
    # print(args)

    if not args["input"]["config"]:
        pipeline_args_check(args)

    global_arguments = get_nfact_arguments()
    nfact_pp_args = build_module_arguments(
        global_arguments["nfact_pp"], args, "pre_process"
    )
    nfact_decomp_args = build_module_arguments(
        global_arguments["nfact_decomp"], args, "decomp"
    )
    nfact_dr_args = build_module_arguments(global_arguments["nfact_dr"], args, "decomp")
    print(nfact_pp_args)

    exit(0)


if __name__ == "__main__":
    nfact_pipeline_main()
