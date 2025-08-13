# LiteLLM Plugin Collection

This collection includes three plugins designed to enhance the functionality of LiteLLM:

1. **Remove Name Plugin**: This plugin removes the 'name' attribute from all messages before they are forwarded to LLM models. This addresses compatibility issues with various LLM providers that may not support or expect the 'name' field in the OpenAI chat format.

2. **Combine System Messages Plugin**: This plugin combines system messages into a single message, ensuring consistent and coherent interactions with LLM models.

3. **Custom Logger Plugin**: This plugin provides a simple logging mechanism for verifying the behavior of LiteLLM plugins. It can be used to log messages and interactions for debugging and verification purposes.

## Compatibility Issues Addressed

- **Remove Name Plugin**:
  - OpenAI's optional 'name' field for messages
  - LLM providers that don't support the 'name' field
  - API error prevention when 'name' field is unexpected
  - Privacy considerations for sensitive user information
  - Workaround for [vllm/pull/20973](https://github.com/vllm-project/vllm/pull/20973) to handle unsupported 'name' field in tool calling.

- **Combine System Messages Plugin**:
  - Ensures consistent and coherent interactions with LLM models by combining system messages.

- **Custom Logger Plugin**:
  - Provides a simple logging mechanism for verifying plugin behavior.

## Installation

1. Place the `remove_name_plugin.py`, `combine_system_messages_plugin.py`, and `custom_logger.py` files in the `litellm` directory of your project.
2. Ensure you have `litellm` installed.

## Usage

To use these plugins, you need to add them to your LiteLLM configuration file (e.g., `litellm/litellm_config.yaml`).

Here is an example of how to configure the plugins in your `litellm_config.yaml`:

```yaml
model_list:
  - model_name: chat
    litellm_params:
      # prefix with openai, hosted_vllm ...
      model: hosted_vllm/chat
      # Base URL of the LLM provider (e.g. OpenAI)
      base_url: http://host.docker.internal:8033/v1/
      api_key: "sk-none"
      cache: true

litellm_settings:
  # Filename of the plugins without .py and name of method.
  callbacks: ["remove_name_plugin.remove_name_handler_instance", "combine_system_messages_plugin.combine_system_messages_handler_instance", "custom_logger.custom_logger_handler_instance"]
```

The plugins will automatically process all messages and remove the `name` field (for the Remove Name Plugin), combine system messages (for the Combine System Messages Plugin), and log interactions (for the Custom Logger Plugin) before forwarding them to the LLM.

## Docker Compose Usage

To use these plugins with Docker, you can leverage the provided `docker-compose.yml` configuration. This setup mounts both the plugin files and configuration file into the container.

Here's how to set it up:

1. Make sure your `docker-compose.yml` looks like this:

```yaml
services:
  litellm:
    image: ghcr.io/berriai/litellm:main-stable
    ports:
      - "4000:4000"
    volumes:
      - ./litellm/litellm_config.yaml:/app/litellm_config.yaml
      - ./litellm/remove_name_plugin.py:/app/remove_name_plugin.py
      - ./litellm/combine_system_messages_plugin.py:/app/combine_system_messages_plugin.py
      - ./litellm/custom_logger.py:/app/custom_logger.py
    command: |
      --config /app/litellm_config.yaml --detailed_debug
    restart: unless-stopped
  vllm-chat:
    image: vllm/vllm-openai:latest
    runtime: nvidia
    ipc: host
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    volumes:
      - .cache/huggingface:/root/.cache/huggingface
    environment:
      # ADD HF_TOKEN to your .env file.
      HUGGING_FACE_HUB_TOKEN: ${HF_TOKEN}
      VLLM_LOGGING_LEVEL: DEBUG

    command: --served-model-name chat --port 8033 --model Qwen/Qwen2-0.5B --max-num-seqs 1 --max-model-len 2048
    ports:
      - "8033:8033"
```

2. The plugins will be automatically loaded and registered when LiteLLM starts up.

3. When running requests, the plugins will intercept all messages and remove any 'name' field (for the Remove Name Plugin), combine system messages (for the Combine System Messages Plugin), and log interactions (for the Custom Logger Plugin) before forwarding to LLM providers.

## Environment Variables

This project uses a `.env` file to manage environment variables. This file is not checked into version control, as specified in the `.gitignore` file.

To set up your local environment, create a `.env` file in the root of the project and add the necessary environment variables. For example:

```
HF_TOKEN="your-huggingface-token"