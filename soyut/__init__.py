# -*- coding: utf-8 -*-
"""

.. include:: ../README.md

[comment]: # (The class diagram is as follows:)

[comment]: # (![classes](./classes.png "Class diagram")

# Tests and coverage

## Baseline images generation

If needed (for example, a new test with its associated baseline image), we might have to
regenerate the baseline images. In this case, run:

    pdm baseline

## Running tests

To run tests and code coverage, run:

    pdm test

## Reports

Once the tests ran, the reports are generated. See the links below:

[See test report](../tests/report.html)

[See test results](../tests/results/fig_comparison.html)

[See coverage](../coverage/index.html)

# Building distribution

The following command builds a wheel file in the dist folder:

    pdm build

The following command builds the doc in htmldoc:

    pdm doc

.. include:: ../CHANGELOG.md

"""
import os
import logging

from rich.logging import RichHandler


logger = logging.getLogger("soyut_logger")
logger.setLevel(os.environ.get("LOGLEVEL", "info").upper())

stream_handler = RichHandler()
logger.addHandler(stream_handler)


def get_soyut_version() -> str:
    import importlib.metadata as im

    try:
        # Production mode
        version = im.version("soyut")
    except BaseException:
        # Development mode
        version = "dev"
    return version


__version__ = get_soyut_version()
