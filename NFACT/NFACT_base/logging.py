import logging
import json
import os
from NFACT.NFACT_base.filesystem import get_current_date
from NFACT.NFACT_base.utils import colours


class NFACT_logs:
    def __init__(self, algo, log_prefix, no_subject) -> None:
        self.algo = algo.upper()
        self.log_prefix = log_prefix
        self.time = get_current_date()
        self.no_subject = no_subject
        self.cols = colours()

    def set_up_logging(self, path):
        logging.basicConfig(
            filename=os.path.join(path, self.get_log_name()),
            level=logging.INFO,
            format="%(message)s",
        )

    def get_log_name(self):
        return f"{self.log_prefix}_{self.algo}_{self.time}.log"

    def inital_log(self, splash):
        logging.info(self.time)
        logging.info(splash)
        logging.info(
            f"{self.cols['plum']}Number of Subjects{self.cols['reset']}: {self.no_subject}"
        )
        logging.info(
            f"{self.cols['plum']}Decomposition algo{self.cols['reset']}: {self.algo}"
        )

    def log_arguments(self, args):
        input_args = self.dictionary_to_json(args)
        logging.info(
            f"{self.cols['plum']}Input arguments: {self.cols['reset']}{input_args}\n"
        )

    def log_parameters(self, parameters):
        parms = self.dictionary_to_json(parameters)
        logging.info(
            f"{self.cols['plum']}Decomposition hyperparameters: {self.cols['reset']}{parms}\n"
        )

    def dictionary_to_json(self, dictionary):
        return json.dumps(dictionary, indent=4)

    def log(self, message):
        logging.info(message)
