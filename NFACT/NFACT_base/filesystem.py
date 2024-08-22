import os
import json
from datetime import datetime
from .utils import error_and_exit


def make_directory(path: str) -> None:
    """
    Function to make a directory.
    If error it will exit

    Parameters
    ----------
    path: str
        string to directory path

    Returns
    -------
    None
    """

    try:
        os.mkdir(path)
    except Exception as e:
        error_and_exit(False, f"Unable to create directory due to {e}")


def read_file_to_list(filename: str) -> list:
    """
    Function to dump output of file to
    list format.

    Parameters
    ----------
    filename: str
        path to file

    Returns
    -------
    list: list of subjects
        list of path to subjects directories
    """

    with open(filename, "r") as file:
        lines = file.readlines()
    return [sub.rstrip() for sub in lines]


def load_json(path: str) -> dict:
    """
    Function to load json

    Parameters
    ----------
    path: str
       path to json file

    Returns
    -------
    dict: dictionary file
        json file
    """
    try:
        with open(path) as config:
            return json.load(config)
    except Exception as e:
        error_and_exit(False, f"Unable to load json due to {e}")


def write_to_file(file_path: str, name: str, text: str) -> bool:
    """
    Function to write to file.

    Parameters
    ----------
    file_path: str
        abosulte file path to
        where file is created
    name: str
        name of file
    text: str
        string to add to file
    """
    try:
        with open(f"{file_path}/{name}", "w") as file:
            file.write(text)
    except Exception as e:
        print(f"Unable to write to {file_path}/{name} due to :", e)
        return False
    return True


def get_current_date() -> str:
    """
    Function to get the
    date and time in format
    useful for a file name.

    Parameters
    ----------
    None

    Returns
    -------
    str: string
        string of datetime object
    """
    now = datetime.now()
    return now.strftime("%Y_%m_%d_%H_%M_%S")
