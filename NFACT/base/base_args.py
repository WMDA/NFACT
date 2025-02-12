def cluster_args(base_args: object, col: dict) -> None:
    """
    Function to add in cluster arguments to
    arguments. Adds in argument group

    Parameters
    ----------
    base_args: argparse.ArgumentParser
        ArgumentParser to add group to
    col: dict
        dictionary of colour strings

    Returns
    -------
    None
    """
    cluster_args = base_args.add_argument_group(
        f"{col['amethyst']}Cluster Arguments{col['reset']}"
    )

    cluster_args.add_argument(
        "-C",
        "--cluster",
        dest="cluster",
        action="store_true",
        default=False,
        help="Use cluster enviornment",
    )
    cluster_args.add_argument(
        "-cq",
        "--queue",
        dest="cluster_queue",
        default=None,
        help="Cluster queue to submit to",
    )
    cluster_args.add_argument(
        "-cr",
        "--cluster_ram",
        dest="cluster_ram",
        default="60",
        help="Ram that job will take. Default is 60",
    )
    cluster_args.add_argument(
        "-ct",
        "--cluster_time",
        dest="cluster_time",
        default=False,
        help="Time that job will take. nfact_pp will assign a time if none given",
    )
    cluster_args.add_argument(
        "-cqos",
        "--cluster_qos",
        dest="cluster_qos",
        default=False,
        help="Set the qos for the cluster",
    )


def parallel_args(base_args: object, col: dict, help_message: str) -> None:
    """
    Function to add in parallel arguments to
    arguments. Adds in argument group

    Parameters
    ----------
    base_args: argparse.ArgumentParser
        ArgumentParser to add group to
    col: dict
        dictionary of colour strings

    Returns
    -------
    None
    """
    parallel_process = base_args.add_argument_group(
        f"{col['darker_pink']}Parallel Processing arguments{col['reset']}"
    )
    parallel_process.add_argument(
        "-n",
        "--n_cores",
        dest="n_cores",
        help=help_message,
        default=False,
    )


def set_up_args(base_args: object, col: dict) -> None:
    """
    Function to add in set up arguments to
    arguments. Adds in argument group

    Parameters
    ----------
    base_args: argparse.ArgumentParser
        ArgumentParser to add group to
    col: dict
        dictionary of colour strings

    Returns
    -------
    None
    """
    set_up_args = base_args.add_argument_group(
        f"{col['deep_pink']}Set Up Arguments{col['reset']}"
    )
    set_up_args.add_argument(
        "-l",
        "--list_of_subjects",
        dest="list_of_subjects",
        help="Filepath to a list of subjects",
    )
    set_up_args.add_argument(
        "-o",
        "--outdir",
        dest="outdir",
        help="Path to output directory",
    )


def base_arguments(base_args: object) -> None:
    base_args.add_argument(
        "-hh",
        "--verbose_help",
        dest="verbose_help",
        default=False,
        action="store_true",
        help="""
        Verbose help message.
        Prints help message and example usages
      """,
    )
    base_args.add_argument(
        "-O",
        "--overwrite",
        dest="overwrite",
        action="store_true",
        default=False,
        help="Overwrites previous file structure",
    )
