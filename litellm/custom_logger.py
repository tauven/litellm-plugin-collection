from litellm.integrations.custom_logger import CustomLogger
import litellm
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PreAPICallLogger(CustomLogger):
    """
    Custom logger to log the pre-api-call messages.
    """
    def __init__(self):
        super().__init__()

    def log_pre_api_call(self, model, messages, kwargs):
        logger.info(f"Pre-API Call for model: {model}")
        try:
            pretty_messages = json.dumps(messages, indent=2)
            logger.info(f"Messages: {pretty_messages}")
        except TypeError:
            logger.info(f"Messages (could not serialize to JSON): {messages}")


# Instantiate the custom logger
pre_api_call_logger = PreAPICallLogger()