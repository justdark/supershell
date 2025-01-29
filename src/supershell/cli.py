import click
import os
import json
from pathlib import Path
from .agent import ReActAgent
def init_config():
    config_path = Path.home() / '.ss_config'
    if not config_path.exists():
        default_config = {
            'api_address': 'https://api.deepseek.com/v1/chat/completions',
            'model_name': 'deepseek-chat',
            'access_key': ''
        }
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        # click.echo(f"Created default config file at {config_path}")
    return config_path

@click.command()
@click.option('--config', default="empty", help='进入配置模式')
@click.argument('text', required=False, nargs=-1)
def cli(config, text):
    """SuperShell - 你的命令行工具"""    
    config_path = init_config()
    
    if config != "empty":
        click.echo("进入配置模式")
        configs = [config]+list(text)
        for c in configs:
            key,value = c.split("=")
            if key in ["api_address","model_name","access_key"]:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                config[key] = value
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                click.echo(f"Updated config file at {config_path}")
    elif text:
        full_text = ' '.join(text)
        # click.echo(f'处理文本: {full_text}')
        agent = ReActAgent(config_path)
        agent.process(full_text)
    else:
        click.echo('请提供自然语言指令或使用 --config 进行配置')

if __name__ == '__main__':
    cli()