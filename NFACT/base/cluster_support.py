from .utils import colours, error_and_exit
import os
import subprocess


class Cluster_parameters:
    """
    Class to process cluster parameters.

    Usage
    -----
    arg = Cluster_parameters().process_parameters(arg)

    Parameters
    ----------
    arg: dict
        command line arguments
    """

    def __init__(self, arg: dict):
        self.args = arg
        self.colours = colours()
        self.queues = self.has_queues()

    def process_parameters(self):
        """
        Method to process parameters

        Parameters
        ----------
        None

        Returns
        ------
        args: dict

        dictionary of processed
        command line arguments
        """

        queues_avail = self.queues["stdout"] != "No"
        if not queues_avail:
            raise NoClusterQueuesException
        self.cluster_ram()
        self.cluster_queue_assignment()
        if self.arg["cluster_qos"]:
            self.cluster_qos()
        self.print_cluster_queues()
        return self.arg

    def has_queues(self) -> dict:
        """
        Method to check if queues
        available.
        """
        return run_fsl_sub(
            [os.path.join(os.environ["FSLDIR"], "bin", "fsl_sub"), "--has_queues"]
        )

    def cluster_ram(self):
        """Method to assign ram amount"""
        self.arg["cluster_ram"] = (
            self.arg["cluster_ram"] if self.arg["cluster_ram"] else 30
        )

    def cluster_time(self):
        """Method to assign cluster time"""
        self.arg["cluster_time"] = (
            self.arg["cluster_time"]
            if self.arg["cluster_time"]
            else 160
            if self.arg["gpu"]
            else 600
        )

    def cluster_queue_assignment(self):
        """Method to assign cluster queue"""
        self.arg["cluster_queue"] = (
            self.arg["cluster_queue"]
            if self.arg["cluster_queue"] in self.queues["std_out"]
            else None
        )

    def cluster_qos(self):
        """Method to assign cluster qos"""
        self.args["cluster_qos"] = f'--extra "--qos={self.args['cluster_qos']}'

    def print_cluster_queues(self):
        """Method to print cluster queues"""
        print_string = (
            "No queue given will assign"
            if not self.arg["cluster_queue"]
            else self.arg["cluster_queue"]
        )
        print(f"{self.col['plum']}Cluster:{self.col['reset']} {print_string}")


class NoClusterQueuesException(Exception):
    """Custom exception for when no cluster queues are available."""

    def __init__(self):
        super().__init__()


def no_cluster_queues():
    """
    Function to print
    and return None if no
    cluster support.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    col = colours()
    print(
        f"{col['plum']}Cluster:{col['reset']} No queues detected. Not running on cluster"
    )
    return None


def run_fsl_sub(command: list) -> dict:
    """
    Function wrapper around fsl_sub calls.

    Parameters
    ----------
    command: list
        list of command to run
    report: bool
        to use fsl_sub_report

    Returns
    -------
    output: dict
        output of fsl_sub call
    """
    try:
        run = subprocess.run(
            command,
            capture_output=True,
        )

    except subprocess.CalledProcessError as error:
        error_and_exit(False, f"Error in calling fsl_sub due to: {error}")
    except KeyboardInterrupt:
        run.kill()
    output = {
        key: value.decode("utf-8").strip() if isinstance(value, bytes) else value
        for key, value in vars(run).items()
    }
    if output["stderr"]:
        error_and_exit(False, f"FSL sub failed due to {output['stderr']}")
    return output
