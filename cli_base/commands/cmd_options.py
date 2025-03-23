import click


SCOPE_PARAMS = [
    {"name": "global", "func_param":"scope",  "flag_value": "global", "help": "Use global configuration"},
    {"name": "local", "func_param":"scope", "flag_value": "local", "default": True, "help": "Use local configuration"},
    {"name": "file", "func_param":"file_path", "type": str, "help": "Model name"},
]

# @click.option("--global", "scope", flag_value="global", help="Use global configuration.")
# @click.option("--local", "scope", flag_value="local", default=True, help="Use local configuration.")
# @click.option("--file", "file_path", type=str, help="Use named configuration file.")

def scope_options(command):
    """Decorator to add profile options to a command."""
    for param in SCOPE_PARAMS:
        command = click.option(
            f"--{param['name']}", 
            param['func_param'],
            flag_value=param.get('flag_value', None) if 'flag_value' in param else None,
            type=param['type'] if 'type' in param else None, 
            default=param.get('default', None) if 'default' in param else None,
            help=param['help']
        )(command)
    return command