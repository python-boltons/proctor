"""The proctor package's catch-all module.

You should only add code to this module when you are unable to find ANY other
module to add it to.
"""

from __future__ import annotations

import logging
from subprocess import PIPE, Popen, TimeoutExpired
from typing import Any, Iterable, Iterator

from eris import ErisError, Err, Ok, Result


logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT = 15


class Process:
    """A wrapper around a subprocess.Popen(...) object.

    Examples:
        >>> from subprocess import PIPE, Popen

        >>> echo_factory = lambda x: Popen(["echo", x], stdout=PIPE)

        >>> echo_popen = echo_factory("foo")
        >>> echo_proc = Process(echo_popen)
        >>> echo_proc.out
        'foo'

        >>> echo_popen = echo_factory("bar")
        >>> out, _err = Process(echo_popen)
        >>> out
        'bar'
    """

    def __init__(
        self,
        popen: Popen,
        *,
        timeout: float | None = _DEFAULT_TIMEOUT,
    ) -> None:
        self.popen = popen

        try:
            stdout, stderr = popen.communicate(timeout=timeout)
        except TimeoutExpired:
            logger.warning(
                "Timed out after %.1f seconds of waiting: %r",
                timeout,
                popen.args,
            )
            popen.kill()
            stdout, stderr = popen.communicate()

        self.out = "" if stdout is None else str(stdout.decode().strip())
        self.err = "" if stderr is None else str(stderr.decode().strip())

    def __iter__(self) -> Iterator[str]:
        """Resturns a 2-tuple of the processes' STDOUT and STDERR."""
        yield from [self.out, self.err]

    def to_error(self, *, up: int = 0) -> Err[Process, ErisError]:
        """Converts a Process object into an Err(...) object.."""
        maybe_out = ""
        if self.out:
            maybe_out = "\n\n----- STDOUT\n{}".format(self.out)

        maybe_err = ""
        if self.err:
            maybe_err = "\n\n----- STDERR\n{}".format(self.err)

        return Err(
            ErisError(
                "Command Failed (ec={}): {!r}{}{}".format(
                    self.popen.returncode,
                    self.popen.args,
                    maybe_out,
                    maybe_err,
                ),
                up=up + 1,
            )
        )


def safe_popen(
    cmd_parts: Iterable[str],
    *,
    up: int = 0,
    timeout: float | None = _DEFAULT_TIMEOUT,
    **kwargs: Any,
) -> Result[Process, ErisError]:
    """Wrapper for subprocess.Popen(...).

    Returns:
        Ok(Process) if the command is successful.
            OR
        Err(ErisError) otherwise.
    """
    process = unsafe_popen(cmd_parts, timeout=timeout, **kwargs)
    if process.popen.returncode != 0:
        return process.to_error(up=up + 1)

    return Ok(process)


def unsafe_popen(
    cmd_parts: Iterable[str],
    *,
    timeout: float | None = _DEFAULT_TIMEOUT,
    **kwargs: Any,
) -> Process:
    """Wrapper for subprocess.Popen(...)

    You can use unsafe_popen() instead of safe_popen() when you don't care
    whether or not the command succeeds.

    Returns:
        A Process(...) object.
    """
    cmd_list = list(cmd_parts)
    logger.debug(
        "Running system command. | command=%r  timeout=%r", cmd_list, timeout
    )

    kwargs.setdefault("stdout", PIPE)
    kwargs.setdefault("stderr", PIPE)

    popen = Popen(cmd_list, **kwargs)
    process = Process(popen, timeout=timeout)

    return process


def command_exists(cmd: str) -> bool:
    """Returns True iff the shell command ``cmd`` exists."""
    popen = Popen("hash {}".format(cmd), shell=True, stdout=PIPE, stderr=PIPE)
    return popen.wait() == 0
