"""proctor package

process doctor (PROCTOR)... Utilities related to process / thread management.
"""

import logging as _logging

from ._core import Process, command_exists, safe_popen, unsafe_popen


__all__ = ["Process", "command_exists", "safe_popen", "unsafe_popen"]

__author__ = "Bryan M Bugyi"
__email__ = "bryanbugyi34@gmail.com"
__version__ = "0.2.2"

_logging.getLogger(__name__).addHandler(_logging.NullHandler())
