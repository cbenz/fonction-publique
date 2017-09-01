# -*- coding: utf-8 -*-


import os

from fonction_publique.config import check_template_config_files


def test_paths():
    assert check_template_config_files(), "Config file not set"
    # Test Directories paths:
    from fonction_publique.base import (
        raw_directory_path,
        tmp_directory_path,
        clean_directory_path,
        output_directory_path,
        )
    assert os.path.exists(raw_directory_path), "{} is not a valid path".format(raw_directory_path)
    assert os.path.exists(tmp_directory_path), "{} is not a valid path".format(tmp_directory_path)
    assert os.path.exists(clean_directory_path), "{} is not a valid path".format(clean_directory_path)
    assert os.path.exists(output_directory_path), "{} is not a valid path".format(output_directory_path)
