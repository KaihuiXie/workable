import time
from enum import Enum


class TimerLogLevel(Enum):
    # Print the execution time of the decorated func, with the func name.
    BASIC = "basic"
    # Print the execution time of the decorated func, with the func name and args.
    STANDARD = "standard"
    # Print the start, finish timestamp and the execution time of the decorated func, with the func name and args.
    VERBOSE = "verbose"


def timer(log_level=TimerLogLevel.STANDARD):
    """Decorator that reports the execution time."""

    def wrapper(func):
        def wrapper_func(*args, **kwargs):
            if log_level == TimerLogLevel.BASIC:
                func_prompt = f"'{func.__name__}'"
            else:
                func_prompt = (
                    f"'{func.__name__}' with args {[str(arg) for arg in args]}"
                )

            start = time.time()
            if log_level == TimerLogLevel.VERBOSE:
                print(
                    f"Start executing {func_prompt} at ",
                    time.asctime(time.localtime(start)),
                )

            result = func(*args, **kwargs)

            end = time.time()
            if log_level == TimerLogLevel.VERBOSE:
                print(
                    f"Finish executing {func_prompt} at ",
                    time.asctime(time.localtime(end)),
                )

            print(f"Executing {func_prompt} took: ", end - start)
            return result

        return wrapper_func

    return wrapper
