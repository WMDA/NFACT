from .nfact_config_functions import (
    nfact_config_args,
    create_combined_algo_dict,
    save_to_json,
    create_subject_list,
    check_arguments,
)
from NFACT.base.config import get_nfact_arguments, process_dictionary_arguments


def nfact_config_main() -> None:
    """
    Main nfact config function.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    args = nfact_config_args()
    check_arguments(args)
    if args["subject_list"]:
        print(f'Saving subject list to {args["output_dir"]}\n')
        create_subject_list(args["subject_list"], args["output_dir"])
        exit(0)

    if args["decomp_only"]:
        arguments = create_combined_algo_dict()
        file_name = "nfact_config_decomp"
    if args["config"]:
        arguments = get_nfact_arguments()
        arguments = process_dictionary_arguments(arguments)
        file_name = "nfact_config_pipeline"

    print(f'Saving {file_name}.config to {args["output_dir"]}\n')
    save_to_json(args["output_dir"], arguments, file_name)
    exit(0)


if __name__ == "__main__":
    nfact_config_main()
