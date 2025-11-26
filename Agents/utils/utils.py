from google.genai import types

import os
import json
from ..config import (
    RETRY_CONFIG_ATTEMPTS,
    RETRY_CONFIG_DELAY,
    RETRY_CONFIG_EXP_BASE,
    RETRY_CONFIG_HTTP_STATUS_CODE
                     )


retry_config = types.HttpRetryOptions(
    attempts=RETRY_CONFIG_ATTEMPTS,
    initial_delay=RETRY_CONFIG_DELAY,
    exp_base=RETRY_CONFIG_EXP_BASE,
    http_status_codes=RETRY_CONFIG_HTTP_STATUS_CODE
)
