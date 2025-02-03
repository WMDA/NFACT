from ..nfact_dr_functions import get_subject_id
from NFACT.base.utils import nprint, colours
from NFACT.base.cluster_support import cluster_submission, Queue_Monitoring
from pathlib import Path
import os
import sys


def get_python_path() -> str:
    """
    Function to return python path.
    If running in virtualenv then
    will use that else will use the
    fsl python path

    Parameteres
    -----------
    None

    Returns
    -------
    str: string object
        path for python
    """
    if sys.prefix != sys.base_prefix:
        return sys.executable
    return os.path.join(os.environ["FSLDIR"], "bin", "python3")


def get_cluster_script_path() -> str:
    """
    Function to return path of
    cluster script.

    Parameters
    ----------
    None

    Returns
    -------
    str: str object
        Path to cluster
        script
    """
    return os.path.join(Path(__file__).parent, "cluster_script.py")


def build_cluster_command(
    fdt_path: str,
    output_dir: str,
    component_path: str,
    group_average_path: str,
    algo: str,
    seeds: str,
    sub_id: str,
    medial_wall: str,
    parallel: str,
) -> list:
    """
    Function to build out cluster
    command.

    Parameters
    ----------
    fdt_path: str
        path to subjects fdt_path

    output_dir: str,
    component_path: str,
    group_average_path: str,
    algo: str,
    seeds: str,
    sub_id: str,
    medial_wall: str,
    parallel: str

    Returns
    -------
    list: list object
        list of command
    """
    python_path = get_python_path()
    cluster_script = get_cluster_script_path()
    command = [
        python_path,
        cluster_script,
        "--fdt_path",
        str(fdt_path),
        "--output_dir",
        str(output_dir),
        "--component_path",
        str(component_path),
        "--group_average_path",
        str(group_average_path),
        "--algo",
        str(algo),
        "--seeds",
        str(seeds),
        "--id",
        str(sub_id),
        "--medial_wall",
        str(medial_wall),
    ]
    if parallel:
        command.extned(["--parallel", str(parallel)])
    return command


def submit_to_cluster(args: dict, paths: dict) -> list:
    """
    Function to submit jobs to cluster
    using fsl_sub
    Function to run jobs on cluster

    Parameters
    ----------
    args: dict
        cmd arguments
    paths: dict
        dictionary of paths

    Returns
    -------
    job_ids: list
        list of job ids
    """
    job_ids = []
    for idx, sub in enumerate(args["ptxdir"]):
        sub_id = get_subject_id(sub, idx)
        nprint(f"Submittng {sub_id}")
        cluster_command = build_cluster_command(
            sub,
            os.path.join(args["outdir"], "nfact_dr"),
            paths["component_path"],
            paths["group_average_path"],
            args["algo"],
            args["seeds"],
            sub_id,
            args["medial_wall"],
            args["n_cores"],
        )
        id = cluster_submission(
            cluster_command,
            args["cluster_time"],
            args["cluster_ram"],
            args["cluster_queue"],
            f"{sub_id}_nfact_dr",
            os.path.join(args["outdir"], "nfact_dr", "logs"),
            args["cluster_qos"],
            False,
        )
        job_ids.append(id)
    return job_ids


def run_on_cluster(args: dict, paths: dict) -> None:
    """
    Function to run jobs on cluster

    Parameters
    ----------
    args: dict
        cmd arguments
    paths: dict
        dictionary of paths

    Returns
    -------
    None
    """

    col = colours()
    nprint(f"{col['pink']}Running{col['reset']}: Cluster")
    nprint(f"{col['pink']}Submtting to{col['reset']}: {args['cluster_queue']}")
    ids = submit_to_cluster(args, paths)
    queue = Queue_Monitoring()
    queue.monitor(ids)
