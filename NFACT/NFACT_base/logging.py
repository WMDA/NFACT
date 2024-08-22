import logging
import json


class NFACT_logs:
    def __init__(self) -> None:
        pass

    def set_up_logging(self, path):
        logging.basicConfig(
            filename=path,
            level=logging.INFO,
            format="%(message)s",
        )

    def log_subjects(self, no_subject):
        logging.info(f"Number of Subjects: {no_subject}")

    def log_arguments(self, args):
        input_args = self.dictionary_to_json(args)
        logging.info("Input arguments to NFACT")
        logging.info(input_args)

    def log_parameters(self, parameters):
        parms = self.dictionary_to_json(parameters)
        logging.info("Decomposition hyperparameters")
        logging.info(parms)

    def dictionary_to_json(self, dictionary):
        json_string = json.dumps(dictionary, indent=4)

    def log(self, message):
        logging.info(message)
