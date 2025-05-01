import logging
from typing import Optional, Tuple


# You can rename the class for clarity if you like, e.g., NoGetNoiseFilter
# Just remember to update log_config.yaml if you rename the class.
class NoSuccessfulOrRedirectGetFilter(logging.Filter):
    """
    A logging filter that prevents successful GET requests (2xx)
    and temporary redirect GET requests (307) from being logged
    by uvicorn.access.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        # Check if the logger name is specifically 'uvicorn.access'
        if record.name == "uvicorn.access":
            args: Optional[Tuple] = getattr(record, "args", None)

            if isinstance(args, tuple) and len(args) >= 5:
                method = args[1]  # Second argument is the method
                status_code = args[4]  # Fifth argument is the status code

                # Check if it's a GET request AND if the status code is 2xx OR 307
                if method == "GET" and isinstance(status_code, int):
                    is_successful = 200 <= status_code < 300
                    is_temp_redirect = status_code == 307

                    if is_successful or is_temp_redirect:
                        # Return False to prevent this log record from being processed
                        return False

        # For all other log records (or non-matching access logs), allow them
        return True
