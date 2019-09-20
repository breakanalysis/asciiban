from constants import ENV_DATADIR, ENV_DOTFILE, DATADIR, MAX_BOARD_ROWS, EDITOR
import os
import re

def get_dotfile():
    return os.environ.get(ENV_DOTFILE, os.path.join(os.environ.get('HOME'), '.asciiban'))

def parse_dotfile():
    dotfile = get_dotfile()
    if not os.path.exists(dotfile):
        return {}
    settings = {}
    with open(dotfile, 'r') as f:
        contents = f.readlines()
    line_nr = 1
    for line in contents:
        try:
            line = re.sub(r'[\s]', '', line)
            if line.startswith('#') or line == '':
                continue
            key, value = line.split('=')
        except:
            raise Exception(f"Error in {dotfile}:{line_nr}. Expected syntax key=value.")
        if key=='max_board_rows':
            try:
                settings['max_board_rows'] = int(value)
            except:
                raise Exception(f"Error in {dotfile}:{line_nr}. Value {value} is not an integer.")
        elif key==DATADIR:
            settings[DATADIR] = value
        line_nr += 1
    return settings

def default_settings():
    # MAYBE TODO: customizable dateformatting
    return {MAX_BOARD_ROWS: 20,
            DATADIR: os.environ.get(ENV_DATADIR, os.path.join(os.environ.get('HOME'), '.asciiban.d')),
            EDITOR: 'vi'}

def get_settings():
    settings = default_settings()
    settings.update(parse_dotfile())
    return settings
