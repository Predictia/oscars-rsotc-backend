"""
Timing utilities module.

This module provides decorators for measuring and logging function execution
times.
"""
import functools
import logging
import time
from typing import Any, Callable


def log_execution_time(func: Callable) -> Callable:
    """
    Calculate and log the computation time of a function.

    It uses the logger of the module where the function is defined to log
    the duration in seconds.

    Parameters
    ----------
    func : Callable
        The function to be decorated.

    Returns
    -------
    Callable
        The wrapped function.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        # Try to get the logger from the module where the function is defined
        module_name = func.__module__
        logger = logging.getLogger(module_name)

        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()

        duration = end_time - start_time
        logger.info(f"Execution time for {func.__name__}: {duration:.4f}s")

        return result

    return wrapper
