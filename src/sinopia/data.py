__author__ = "Jeremy Nelson"
__license__ = "Apache 2"

import pandas as pd


def issues_data_frame(**kwargs):
    """Takes a JSON Github v4 issues payload and returns a Panda's
    data frame.

    Keyword arguments:
    issues: list of issues
    """
