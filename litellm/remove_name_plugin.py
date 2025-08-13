"""
Remove Name Plugin for LiteLLM

This plugin is designed to remove the 'name' attribute from all messages
before they are forwarded to LLM models. This addresses compatibility issues
with various LLM providers that may not support or expect the 'name' field
in the OpenAI chat format.

The plugin works by intercepting requests before they are sent to the LLM
and removing the 'name' field from user messages, ensuring consistent
message formatting across different LLM providers.

Compatibility Issues Addressed:
- OpenAI's optional 'name' field for user messages
- LLM providers that don't support the 'name' field
- API error prevention when 'name' field is unexpected
- Privacy considerations for sensitive user information

Usage:
To use this plugin, you need to add it to your LiteLLM configuration file (e.g., `litellm_config.yaml`).
- Add this plugin to your LiteLLM configuration
  litellm_config.yaml
  '''
    ...
    litellm_settings:
      callbacks: ["litellm.remove_name_plugin.remove_name_handler_instance"]
    ...
  '''
- The plugin will automatically process all user messages
- No manual intervention required

"""
from typing import Literal
from litellm.integrations.custom_logger import CustomLogger # pyright: ignore[reportMissingImports]
from litellm.proxy.proxy_server import UserAPIKeyAuth, DualCache  # pyright: ignore[reportMissingImports]

# pylint: disable=unused-argument
class RemoveNamePlugin(CustomLogger):
    """
    A LiteLLM plugin to remove the 'name' parameter from the 'user' object
    in the request body.
    """
    
    def __init__(self):
        """
        Initialize the RemoveNamePlugin.
        
        Sets the plugin name for identification.
        """
        super().__init__()
        self.name = "remove_name_plugin"
    
    async def async_pre_call_hook(self, 
            user_api_key_dict: UserAPIKeyAuth, 
            cache: DualCache, data: dict,
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
        Remove 'name' attribute from user messages before sending to LLM.
        
        This hook processes the request payload and removes the 'name' field
        from all messages. It's called before the request is forwarded
        to the LLM provider.
        
        Args:
            user_api_key_dict (UserAPIKeyAuth): User API key authentication info
            cache (DualCache): Cache instance
            data (dict): The request payload data containing messages
            call_type (Literal): Type of API call being made
            
        Returns:
            dict: The modified data with 'name' field removed from user messages
        """
        try:
            messages = data.get("messages")
            
            if not isinstance(messages, list):
                return data
            
            modified_count = 0
            for message in messages:
                if isinstance(message, dict) and "name" in message:
                    message.pop("name", None)
                    modified_count += 1
            
            return data
            
        except Exception as e:
            return data   

proxy_handler_instance = RemoveNamePlugin()
