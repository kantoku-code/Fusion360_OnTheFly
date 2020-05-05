#FusionAPI_python addin
#Author-kantoku
#Description-

import traceback
from .OnTheFlyCore import OnTheFlyCore
import sys

try:
    commands = []
    command_definitions = []
        # 'toolbar_panel_id': 'InspectPanel',

    cmd = {
        'cmd_name': 'On The Fly',
        'cmd_description': 'On The Fly',
        'cmd_id': 'onthefly',
        'cmd_resources': '',
        'workspace': 'FusionSolidEnvironment',
        'toolbar_panel_id': 'SolidScriptsAddinsPanel',
        'class': OnTheFlyCore
    }
    command_definitions.append(cmd)

    cmd = {
        'cmd_name': 'On The Fly',
        'cmd_description': 'On The Fly',
        'cmd_id': 'onthefly',
        'cmd_resources': '',
        'workspace': 'CAMEnvironment',
        'toolbar_panel_id': 'CAMInspectPanel',
        'class': OnTheFlyCore
    }
    command_definitions.append(cmd)

    debug = False

    # Don't change anything below here:
    for cmd_def in command_definitions:
        command = cmd_def['class'](cmd_def, debug)
        commands.append(command)

except:
    print('Failed:\n{}'.format(traceback.format_exc()))

def run(context):
    for run_command in commands:
        run_command.on_run()


def stop(context):
    for stop_command in commands:
        stop_command.on_stop()