import logging
import json
import os
from NFACT.NFACT_base.filesystem import get_current_date
from NFACT.NFACT_base.utils import colours


class NFACT_logs:
    """
    Class to log progress in a log file

    Usage
    -----
    log = NFACT_logs(args["algo"], "decomp", len(args["ptxdir"]))\n
    log.set_up_logging(os.path.join(args["outdir"], "nfact", "logs"))\n
    log.inital_log(nfact_splash())\n
    log.log_break("input")\n
    log.log_arguments(args)\n
    log.log_parameters(parameters)\n
    log.log_break("nfact decomp workflow")
    """

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

    def process_datetime(self):
        date_time = self.time.split("_")
        date = "/".join(date_time[:2])
        time = ":".join(date_time[3:])
        return {"date": date, "time": time}

    def inital_log(self, splash):
        date_time = self.process_datetime()
        logging.info(splash)
        self.log_break("meta data")
        logging.info(
            f"{self.cols['plum']}Date Started{self.cols['reset']}: {date_time['date']}"
        )
        logging.info(
            f"{self.cols['plum']}Time Started{self.cols['reset']}: {date_time['time']}"
        )
        logging.info(
            f"{self.cols['plum']}Number of Subjects{self.cols['reset']}: {self.no_subject}"
        )
        logging.info(
            f"{self.cols['plum']}Decomposition algo{self.cols['reset']}: {self.algo}"
        )

    def log_break(self, message):
        logging.info(f"\n{message.upper()}")
        logging.info("-" * 80)

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
