from NFACT.NFACT_config.nfact_config_functions import (
    nfact_config_args,
    create_combined_algo_dict,
    save_to_json,
)


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
    arguments = create_combined_algo_dict()
    print(f'Saving config file to {args["output_dir"]}\n')
    save_to_json(args["output_dir"], arguments)


if __name__ == "__main__":
    nfact_config_main()
