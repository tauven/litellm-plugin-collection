"""
Combine System Messages Plugin for LiteLLM

This plugin is designed to combine multiple 'system' messages into the first 'system' message
before they are forwarded to LLM models. This addresses compatibility issues
with various LLM providers that may not support or expect multiple 'system' messages
in the OpenAI chat format.

The plugin works by intercepting requests before they are sent to the LLM
and combining all 'system' messages into the first 'system' message, ensuring consistent
message formatting across different LLM providers.

Compatibility Issues Addressed:
- OpenAI's handling of multiple 'system' messages
- LLM providers that don't support multiple 'system' messages
- API error prevention when multiple 'system' messages are unexpected
- Consistency in message formatting

Usage:
To use this plugin, you need to add it to your LiteLLM configuration file (e.g., `litellm_config.yaml`).
- Add this plugin to your LiteLLM configuration
  litellm_config.yaml
  '''
    ...
    litellm_settings:
      callbacks: ["litellm.combine_system_messages_plugin.combine_system_messages_handler_instance"]
    ...
  '''
- The plugin will automatically process all user messages
- No manual intervention required

"""
from typing import Literal
from litellm.integrations.custom_logger import CustomLogger # pyright: ignore[reportMissingImports]
from litellm.proxy.proxy_server import UserAPIKeyAuth, DualCache  # pyright: ignore[reportMissingImports]
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# pylint: disable=unused-argument
class CombineSystemMessagesPlugin(CustomLogger):
    """
    A LiteLLM plugin to combine multiple 'system' messages into the first 'system' message
    in the request body.
    """

    def __init__(self):
        """
        Initialize the CombineSystemMessagesPlugin.

        Sets the plugin name for identification.
        """
        super().__init__()
        self.name = "combine_system_messages_plugin"

    async def async_pre_call_hook(
            self,
            user_api_key_dict: UserAPIKeyAuth,
            cache: DualCache,
            data: dict,
            call_type: Literal[
                "completion",
                "text_completion",
                "embeddings",
                "image_generation",
                "moderation",
                "audio_transcription",
            ]
    ) -> dict:
        """
        Combine multiple 'system' messages into the first 'system' message before sending to LLM.

        This hook processes the request payload and combines all 'system' messages into the first 'system' message.
        It's called before the request is forwarded to the LLM provider.

        Args:
            user_api_key_dict (UserAPIKeyAuth): User API key authentication info
            cache (DualCache): Cache instance
            data (dict): The request payload data containing messages
            call_type (Literal): Type of API call being made

        Returns:
            dict: The modified data with combined 'system' messages
        """
        try:
            messages = data.get("messages")

            if not isinstance(messages, list):
                return data

            system_messages = [msg for msg in messages if msg.get("role") == "system"]

            if len(system_messages) > 1:
                # Combine all system messages into the first system message
                combined_content = "\n".join(msg.get("content", "") for msg in system_messages)
                system_messages[0]["content"] = combined_content

                # Remove the additional system messages
                data["messages"] = [msg for msg in messages if msg not in system_messages[1:]]

            return data

        except Exception as e:
            logger.error(f"Error processing messages: {e}")
            return data

proxy_handler_instance = CombineSystemMessagesPlugin()