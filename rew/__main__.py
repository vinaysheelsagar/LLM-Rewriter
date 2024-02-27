import os
import sys
import yaml
import google.generativeai as genai
import click


def chat_prompt(text: str):
# rephrase as professional and polite short chat message:
    message = f"""
Rewrite the following sentence in professional and simpler terms
only write the message:

message: ""{text}""

rewritten message:

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


def set_config(
    config: dict,
    config_filename: str = 'config.yaml', 
):
    """To save given configuration to config.yaml"""

    config_file_dir = get_config_dir()
    config_file_path = os.path.join(config_file_dir, config_filename)

    with open(config_file_path, 'w', encoding='utf-8') as outfile:
        yaml.dump(config, outfile, default_flow_style=False)


def set_api_key(api_key: str):
    config = get_config(validate=False)
    config['api_key'] = api_key
    set_config(config)


def validate_config(config):
    if (
        'api_key' not in config.keys() \
        or config['api_key'] is None
    ):
        click.echo(
            "API Key is not set. Run 'rew --api-key=\"API-KEY\"' to set it.", 
            err=True, 
            color=True,
        )
        sys.exit()


def get_config(
    config_filename: str = 'config.yaml', 
    validate: bool = True,
):
    """To get configuration from config.yaml"""

    config_file_dir = get_config_dir()
    config_file_path = os.path.join(config_file_dir, config_filename)

    if not os.path.exists(config_file_path):
        config = defaut_config()
        set_config(config=None)

    with open(
        config_file_path, 
        'r', 
        encoding='utf-8'
    ) as stream:
        config = yaml.safe_load(stream)

    if validate:
        validate_config(config)

    return config


@click.command(context_settings = dict( help_option_names = ['-h', '--help'] ))
@click.option('-c', '--chat', is_flag=True, help='To rephrase chat messages')
@click.option('--api-key', type=click.STRING)
@click.version_option()
def gateway(
    chat: bool,
    api_key: str,
):

    if api_key:
        set_api_key(api_key)

    if chat:
        config = get_config()

        genai.configure(api_key=config['api_key'])
        model = genai.GenerativeModel(config['model_name'])

        message_history = []

        ask_message = "\nMessage: "

        while True:
            text_input = input(ask_message)

            if text_input == "exit()":
                break

            message_history.append(text_input)

            if text_input == "p":
                message_history.pop()

            response = model.generate_content(chat_prompt(message_history[-1]))

            response_text = clean_response(response.text)
            click.echo(f"> {response_text}")
