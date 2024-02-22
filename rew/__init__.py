import os
import yaml
import google.generativeai as genai
import click


def chat_prompt(text: str):
    message = f"""
rephrase as professional and polite short chat message:

""{text}""  

only write the message
""".strip()

    return message


def clean_response(text: str):
    text = text.strip()
    if text[0] == '"' and text[-1] == '"':
        text = text[1:-1]

    return text


def defaut_config():
    return {
        "api_key": None,
        "model_name": "gemini-1.0-pro-latest",
    }


def get_config_dir():
    config_file_dir = os.path.join(
        os.path.expanduser('~'),
        '.rew', 
    )
    os.makedirs(config_file_dir, exist_ok=True)
    return config_file_dir


def set_config(config: dict | None = None, config_filename: str = 'config.yaml'):
    """To save given configuration to config.yaml"""

    if not config:
        config = defaut_config()

    config_file_dir = get_config_dir()
    config_file_path = os.path.join(config_file_dir, config_filename)

    with open(config_file_path, 'w', encoding='utf-8') as outfile:
        yaml.dump(config, outfile, default_flow_style=False)


def set_api_key(api_key: str):
    config = get_config()
    config['api_key'] = api_key
    set_config(config)


def validate_config(config):
    if 'api_key' not in config.keys() or config['api_key'] is None:
        raise Exception("API Key is required. Run 'rew --api-key=\"API-KEY\"' to set it.")


def get_config(config_filename: str = 'config.yaml'):
    """To get configuration from config.yaml"""

    config_file_dir = get_config_dir()
    config_file_path = os.path.join(config_file_dir, config_filename)

    if not os.path.exists(config_file_path):
        set_config()

    with open(config_file_path, 'r', encoding='utf-8') as stream:
        config = yaml.safe_load(stream)

    validate_config(config)

    return config


@click.command()
@click.option('--chat', is_flag=True, help="To rephrase chat messages")
@click.option('--api-key', type=click.STRING)
def gateway(chat, api_key: str):
    
    if api_key:
        set_api_key(api_key)

    if chat:
        config = get_config()

        genai.configure(api_key=config['api_key'])
        model = genai.GenerativeModel(config['model_name'])

        ask_message = "\nMessage: "

        text = input(ask_message)
        while text != "exit()":
            response = model.generate_content(chat_prompt(text))

            response_text = clean_response(response.text)
            click.echo(f"{response_text}")

            text = input(ask_message)

if __name__ == "__main__":
    gateway()
