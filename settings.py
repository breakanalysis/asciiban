from constants import *
import os
import re

def get_dotfile():
    return os.environ.get(ENV_DOTFILE, os.path.join(os.environ.get('HOME'), '.asciiban'))

def get_board_settings_file():
    return os.path.join(get_settings()[DATADIR], BOARD_SETTINGS_FILE)

def parse_settings_file(dotfile, postprocessor):
    if not os.path.exists(dotfile):
        return {}
    with open(dotfile, 'r') as f:
        contents = f.readlines()
    line_nr = 1
    settings = {}
    for line in contents:
        try:
            line = re.sub(r'[\s]', '', line)
            if line.startswith('#') or line == '':
                continue
            key, value = line.split('=')
        except:
            raise Exception(f"Error in {dotfile}:{line_nr}. Expected syntax key=value.")
        settings[key] = value
        postprocessor(settings, line_nr)
        line_nr += 1
    return settings

def settings_postprocessor(settings, line_nr):
    for key in settings:
        if key==MAX_BOARD_ROWS:
            try:
                settings[key] = int(settings[key])
            except:
                raise Exception(f"Error on line {line_nr}. Expected integer value for {key}.")

def board_settings_postprocessor(settings, line_nr):
    for key in settings:
        if key==CUSTOM_FIELDS:
            try:
                pairs_as_str = re.sub(r'[\s]', '', settings[key]).split(',')
                fields_with_defaults = {}
                for pair in pairs_as_str:
                    k, v = pair.split(':')
                    fields_with_defaults[k] = int(v)
                settings[key] = fields_with_defaults
            except:
                raise Exception(f"Error on line {line_nr}. Setting {key} expects value in format field1:default1,field2:default2,... where defaults are integers.")
        if key==STATUS_COLUMNS:
            settings[key] = settings[key].split(',')

def default_settings():
    # MAYBE TODO: customizable dateformatting
    return {MAX_BOARD_ROWS: 20,
            BOX_WIDTH: 15,
            BOX_ROWS: 4,
            DATADIR: os.environ.get(ENV_DATADIR, os.path.join(os.environ.get('HOME'), '.asciiban.d')),
            EDITOR: 'vi'}

def get_settings():
    settings = default_settings()
    settings.update(parse_settings_file(get_dotfile(), settings_postprocessor))
    return settings

def default_board_settings():
    return {BACKLOG_SORTING: '100*urgency - created + value/estimate',
            CUSTOM_FIELDS: {'urgency': 2, 'value': 2, 'estimate': 2},
            STATUS_COLUMNS: [BACKLOG, UPCOMING, WIP, BLOCKED, DONE]}

def get_board_settings():
    settings = default_board_settings()
    settings.update(parse_settings_file(get_board_settings_file(), board_settings_postprocessor))
    return settings
