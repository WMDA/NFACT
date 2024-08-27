from .nfact_pipeline_args import nfact_args


def nfact_pipeline_main() -> None:
    args = nfact_args()
    print(args)

    exit(0)


if __name__ == "__main__":
    nfact_pipeline_main()
