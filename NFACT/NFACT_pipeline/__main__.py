from .nfact_pipeline_args import nfact_args
from .nfact_pipeline_set_up import pipeline_args_check
from NFACT.NFACT_base.config import get_nfact_arguments


def nfact_pipeline_main() -> None:
    args = nfact_args()
    pipeline_args_check(args)
    print(get_nfact_arguments())

    exit(0)


if __name__ == "__main__":
    nfact_pipeline_main()
