from .nfact_config_functions import (
    nfact_config_args,
    create_combined_algo_dict,
    save_to_json,
)
from NFACT.NFACT_base.config import get_nfact_arguments, process_dictionary_arguments


def nfact_config_main() -> None:
    """
    Main nfact config function.
    Creates config file

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    args = nfact_config_args()

    if args["hyperparameters"]:
        arguments = create_combined_algo_dict()
    else:
        arguments = get_nfact_arguments()
        arguments = process_dictionary_arguments(arguments)

    print(f'Saving config file to {args["output_dir"]}\n')
    save_to_json(args["output_dir"], arguments)


if __name__ == "__main__":
    nfact_config_main()
