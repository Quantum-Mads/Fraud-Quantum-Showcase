import os
from configparser import ConfigParser
import platform


def get_config_file_data():
    os_platform = platform.platform()
    separator = "/"
    if "Windows" in os_platform:
        separator = "\\"

    abs_path = os.path.abspath(__file__).split(separator)
    src_position = abs_path.index("src")

    config_file_path: str = separator.join(abs_path[:src_position])
    config_file = config_file_path + separator + "config.cfg"
    config = ConfigParser()

    return config, config_file
