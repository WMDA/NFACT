from .nfact_pipeline_args import nfact_args
from .nfact_pipeline_set_up import pipeline_args_check, get_function_output
from NFACT.NFACT_PP.nfactpp_args import nfact_pp_args


def nfact_pipeline_main() -> None:
    args = nfact_args()
    pipeline_args_check(args)

    exit(0)


if __name__ == "__main__":
    nfact_pipeline_main()
