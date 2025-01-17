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


def parallel_args(base_args: object, col: dict) -> None:
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
        help="If should parallel process and with how many cores",
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
