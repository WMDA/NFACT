from NFACT.base.filesystem import get_current_date
from NFACT.base.utils import colours, error_and_exit
from NFACT.base.cluster_support import run_fsl_sub
import os
import subprocess
import multiprocessing
import signal
import time


def to_use_gpu():
    """
    Function to check if to use GPU
    or CPU
    Parameters
    ----------
    None
    Returns
    -------
    bool: boolen
        True if probtrack
    """
    return True if get_probtrack2_arguments(bin=True) else False


def fail_safe_for_nfact_pp(warp: str, bpx: str):
    """
    Fail safe function to check that
    warps and bedpostx directory given.

    Parameters
    ----------
    warp: str
        str og warp files
    bpx: str
        str of bedpostX directory

    Returns
    -------
    None
    """
    arg_names = ["warps", "bedpostX directory"]
    for idx, arg in enumerate([warp, bpx]):
        error_and_exit(
            arg,
            f"{arg_names[idx]} not given. If using nfact pipeline check the json file",
        )


def check_bpx_dir(bpx_path: str, nodiff_mask: str) -> None:
    """
    Function to check bedpostX dir

    Parameters
    ----------
    bpx_path: str
        path to bedpost directory
    nodiff_mask: str
        path to nodiff mask

    Returns
    -------
    None
    """
    error_and_exit(
        os.path.exists(os.path.dirname(bpx_path)), "BedpostX directory does not exist."
    )
    error_and_exit(
        os.path.isfile(nodiff_mask + ".nii.gz"),
        "No diff mask in Bedpost X directory does not exist.",
    )


def process_command_arguments(arg: dict, sub: str) -> dict:
    """
    Function to process command line
    arguments

    Parameters
    -----------
    arg: dict
        dictionary of arguments from
        command line
    sub: str
        subjects full path

    Returns
    -------
    dict: dictonary oject
        dict of processed
        command line arguments
    """
    fail_safe_for_nfact_pp(
        arg["warps"],
        arg["bpx_path"],
    )
    return {
        "warps": [os.path.join(sub, warp) for warp in arg["warps"]],
        "seed": os.path.join(
            arg["outdir"], "nfact_pp", os.path.basename(sub), "seeds.txt"
        ),
        "bpx_path": os.path.join(sub, arg["bpx_path"]),
    }


def build_probtrackx2_arguments(arg: dict, sub: str, ptx_options=False) -> list:
    """
    Function to build out probtrackx2 arguments

    Parameters
    ----------
    arg: dict
        dictionary of arguments from
        command line
    sub: str
        subjects full path
    output_dir: str
        path to output directory

    Returns
    -------
    list: list object
        list of probtrackx2 arguements
    """

    command_arguments = process_command_arguments(arg, sub)
    binary = "probtrackx2_gpu" if arg["gpu"] else "probtrackx2"
    warps = command_arguments["warps"]
    seeds = command_arguments["seed"]
    mask = os.path.join(command_arguments["bpx_path"], "nodif_brain_mask")
    target_mask = (
        os.path.join(sub, arg["target2"])
        if arg["target2"]
        else os.path.join(
            arg["outdir"], "nfact_pp", os.path.basename(sub), "files", "target2.nii.gz"
        )
    )

    bpx = os.path.join(command_arguments["bpx_path"], "merged")
    check_bpx_dir(bpx, mask)
    output_dir = os.path.join(
        arg["outdir"], "nfact_pp", os.path.basename(sub), "omatrix2"
    )

    command = [
        binary,
        "-x",
        seeds,
        "-s",
        bpx,
        f"--mask={mask}",
        f"--xfm={warps[0]}",
        f"--invxfm={warps[1]}",
        f"--seedref={arg['ref']}",
        "--omatrix2",
        f"--target2={target_mask}",
        "--loopcheck",
        "--forcedir",
        "--opd",
        "--pd",
        f"--nsamples={arg['nsamples']}",
        f"--dir={output_dir}",
    ]

    if ptx_options:
        command = command + ptx_options
    return command


def get_target2(
    target_img: str,
    output_dir: str,
    resolution: str,
    reference_img: str,
    interpolation_strategy: str,
) -> None:
    """
    Function to create target2 image

    Parameters
    ----------
    target_img: str
        string to target image
    output: str
        string to output directory
    resolution: str
        resolution of target2
    reference_img: str
        reference input
    interpolation_strategy: str
        interpolation, either
        trilinear,
        nearestneighbour,
        sinc,
        spline

    Returns
    -------
    None
    """

    try:
        run = subprocess.run(
            [
                "flirt",
                "-in",
                target_img,
                "-out",
                output_dir,
                "-applyisoxfm",
                str(resolution),
                "-ref",
                reference_img,
                "-interp",
                interpolation_strategy,
            ],
            capture_output=True,
        )
    except FileNotFoundError:
        error_and_exit(False, "Unable to find reference image. Please check it exists")
    except subprocess.CalledProcessError as error:
        error_and_exit(False, f"Error in calling FSL flirt: {error}")
    except KeyboardInterrupt:
        run.kill()

    if run.returncode != 0:
        error_and_exit(
            False, f"FSL FLIRT failure due to {run.stderr}. Unable to build target2"
        )


def seeds_to_ascii(surfin: str, medial_wall: str, surfout: str) -> None:
    """
    Function to create seeds from
    surfaces.

    Parameters
    ----------
    surfin: str
        input surface
    medial_wall: str,
        medial wall surface
    surfout: str
        name of output surface.
        Needs to be full path

    Returns
    -------
    None
    """
    col = colours()
    print(
        f"{col['pink']}Working on seed surface:{col['reset']} {os.path.basename(surfin)}"
    )

    try:
        run = subprocess.run(
            [
                "surf2surf",
                "-i",
                surfin,
                "-o",
                surfout,
                f"--values={medial_wall}",
                "--outputtype=ASCII",
            ],
            capture_output=True,
        )

    except subprocess.CalledProcessError as error:
        error_and_exit(False, f"Error in calling surf2surf: {error}")
    except KeyboardInterrupt:
        run.kill()

    if run.returncode != 0:
        error_and_exit(
            False,
            f"FSL surf2surf failure due to {run.stderr}. Unable to create asc surface",
        )


def get_probtrack2_arguments(bin: bool = False) -> None:
    """
    Function to get probtrack2
    arguments to check that user input
    is valid

    Parameters
    ----------
    bin: bool
        get the arguments for the
        gpu binary. Needed for NFACT
        pipeline

    Returns
    -------
    help_arguments: str
        string of help arguments
    """

    binary = "probtrackx2" if not bin else "probtrackx2_gpu"

    try:
        help_arguments = subprocess.run([binary, "--help"], capture_output=True)
    except subprocess.CalledProcessError as error:
        error_and_exit(False, f"Error in calling probtrackx2: {error}")

    return help_arguments.stderr.decode("utf-8")

class Probtrackx:
    """
    Class to run probtrackx

    Usage
    -----
    probtrackx = Probtrackx(command: list,
        cluster_time: int,
        cluster_queue: str,
        cluster_ram: int,
        parallel: bool = False,
        dont_cluster: bool = False)
    probtrackx.run()
    """

    def __init__(
        self,
        command: list,
        cluster: bool,
        cluster_time: int,
        cluster_queue: str,
        cluster_ram: int,
        parallel: bool = False,
    ) -> None:
        self.command = command
        self.parallel = parallel
        self.col = colours()
        self.cluster = cluster
        self.gpu = True if "probtrackx2_gpu" in command[0] else False
        self.cluster_time = cluster_time
        self.cluster_queue = cluster_queue
        self.cluster_ram = cluster_ram

    def run(self):
        """
        Method to run probtrackx
        """
        if self.parallel:
            self.__parallel_mode()
        if not self.parallel:
            self.__single_subject_run()

    def __single_subject_command(self):
        """
        Method to get single subjects
        """
        return {
            "command": (self.__cluster if self.cluster else self.__run_probtrackx),
            "print_str": "on cluster" if self.cluster else "locally",
        }

    def __single_subject_run(self) -> None:
        """
        Method to do single subject mode
        Loops over all the subject
        """
        run_probtractkx = self.__single_subject_command()
        print(
            f"{self.col['pink']}\nRunning subjects {run_probtractkx['print_str']}{self.col['reset']}"
        )

        submitted_jobs = []
        for sub_command in self.command:
            if self.__cluster:
                job = run_probtractkx["command"](sub_command)
                submitted_jobs.append(job["stdout"])
            if not self.__cluster:
                run_probtractkx["command"](sub_command)
        self.__wait_for_complete(submitted_jobs)

    def __cluster(self, command):
        """
        Method to submit jobs to cluster
        """
        cluster_command = [
            os.path.join(os.environ["FSLDIR"], "bin", "fsl_sub"),
            command,
            "-T",
            self.cluster_time,
            "-R",
            self.cluster_ram,
            "-q",
            self.cluster_queue,
            "-c",
            "cuda" if self.gpu else False,
            "-N",
            f"nfact_pp_{os.path.basename(os.path.dirname(command[2]))}",
        ]

        return run_fsl_sub(cluster_command)

    def __wait_for_complete(self, job_id):
        while True:
            running = True
            for job in job_id:
                running = self.__check_job(job)

            if not running:
                print("All NFACT_PP jobs have finihsed")
                break

            time.sleep(300)

    def __check_job(self, job_id):
        output = run_fsl_sub(
            [os.path.join(os.environ["FSLDIR"], "bin", "fsl_sub_report"), job_id]
        )
        if "finished" in output["stdout"]:
            return False
        return True

    def __parallel_mode(self) -> None:
        """
        Method to parallell process
        multiple subjects
        """
        print(
            f"{self.col['pink']}\nParrellel processing with {self.parallel} cores{self.col['reset']}"
        )
        pool = multiprocessing.Pool(processes=int(self.parallel))

        def kill_pool(sig, frame):
            """
            Method to kill pool safely.
            Also prints kill message so that
            the singit doesn't print it 100x
            times
            """

            pool.terminate()
            print(
                f"\n{self.col['darker_pink']}Recieved kill signal (Ctrl+C). Terminating..."
            )
            print(f"Exiting...{self.col['reset']}\n")
            exit(0)

        signal.signal(signal.SIGINT, kill_pool)
        pool.map(self.__run_probtrackx, self.command)

    def __log_name(self):
        return "PP_log_" + get_current_date()

    def __log_path(self, nfactpp_diretory):
        return os.path.join(nfactpp_diretory, "logs", self.__log_name())

    def __nfact_dir(self, command):
        return os.path.dirname(command[2])

    def __run_probtrackx(self, command: list) -> None:
        """
        Method to run probtrackx

        Parameters
        ----------
        command: list
            command in list form to run

        Returns
        -------
        None
        """
        nfactpp_diretory = self.__nfact_dir(command)
        print(
            "Running",
            command[0],
            f"on subject {os.path.basename(nfactpp_diretory)}",
        )
        try:
            with open(self.__log_path(nfactpp_diretory), "w") as log_file:
                run = subprocess.run(
                    command,
                    stdout=log_file,
                    stderr=log_file,
                    universal_newlines=True,
                )
        except subprocess.CalledProcessError as error:
            error_and_exit(False, f"Error in calling probtrackx2: {error}")
        except KeyboardInterrupt:
            run.kill()
        except Exception as e:
            error_and_exit(False, f"The following error occured: {e}")
            return None
        # Error handling subprocess
        if run.returncode != 0:
            error_and_exit(False, f"Error in {command[0]} please check log files")
