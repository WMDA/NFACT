import os


def get_version_from_pyproject(file_path: str) -> str:
    """
    Get the version number from the pyproject.toml file.

    Parameters:
    ------------
    file_path: The path to the pyproject.toml file.

    Returns:
    - str: The version number of NFACT.
    """
    try:
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()  # Remove leading/trailing whitespace
                if line.startswith("version ="):
                    # Split the line by '=' and strip the result
                    version = line.split("=", 1)[1].strip().strip('"').strip("'")
                    return version

        return "Error: Version key not found in pyproject.toml."

    except FileNotFoundError:
        return "Error: pyproject.toml file not found."
    except Exception as e:
        return f"Error: {str(e)}"


file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pyproject.toml")
__version__ = get_version_from_pyproject(file_path)
