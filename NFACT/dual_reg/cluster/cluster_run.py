from ..nfact_dr_functions import get_subject_id
from NFACT.base.utils import nprint, colours
from NFACT.base.cluster_support import cluster_submission
from NFACT.base.setup import check_fsl_is_installed
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
    return [
        python_path,
        cluster_script,
        "--fdt_path",
        fdt_path,
        "--output_dir",
        output_dir,
        "--component_path",
        component_path,
        "--group_average_path",
        group_average_path,
        "--algo",
        algo,
        "--seeds",
        seeds,
        "--id",
        sub_id,
        "--medial_wall",
        medial_wall,
        "--parallel",
        parallel,
    ]


def submit_to_cluster(fdt_matricies):
    """
    Function to submit jobs to cluster
    using fsl_sub

    Parameters
    ----------
    """
    job_ids = []
    for sub, idx in enumerate(fdt_matricies):
        sub_id = get_subject_id(sub, idx)
        cluster_command = build_cluster_command(sub)
        id = cluster_submission(cluster_command)
        job_ids.append(id)
    return job_ids


def run_on_cluster(args: dict, paths: dict) -> None:
    check_fsl_is_installed()
    col = colours()
    nprint(f"{col['pink']}Running{col['reset']}: Cluster")
    nprint(f"{col['pink']}Submtting to{col['reset']}: {args['queue']}")
    ids = submit_to_cluster()
    return None
