import csv
import logging


logger = logging.getLogger("plone.volto.scripts")
fh = logging.FileHandler("scripts.log", mode="w")
formatter = logging.Formatter(
    fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
fh.setFormatter(formatter)
logger.addHandler(fh)


def save_csv(data, filename):
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        csvfile.write("\ufeff")  # byte order mark for ease of use
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerows(sorted(data))


def print_error(error_string):  # RED
    # removed error string
    print(f"\033[31m{error_string}\033[0m")


def print_info(info_string):  # YELLOW
    print(f"\033[33m{info_string}\033[0m")
    logger.info(f"{info_string}")


def print_ok(info_string):  # GREEN
    print(f"\033[32m{info_string}\033[0m")
    logger.info(f"{info_string}")
