import os
from datetime import datetime
from threading import Thread
from flask import Flask, request, make_response
from slackclient import SlackClient
from ebird import EbirdClient
import commands

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
EBIRD_TOKEN = os.environ["EBIRD_TOKEN"]

slack_client = SlackClient(SLACK_BOT_TOKEN)
ebird_client = EbirdClient(EBIRD_TOKEN)

app = Flask(__name__)

# list of accepted commands and their required parameters
COMMAND_PARAMS = {
    'recent': ['latitude', 'longitude'],
    'recent-notable': ['latitude', 'longitude']
}


def parse_parameters(parameter_list):

    cmd = parameter_list.pop(0)

    # temporary alias until users convert to new name
    cmd = 'recent_notable' if cmd == 'recent-notable' else cmd

    if cmd not in COMMAND_PARAMS.keys():
        valid = False
        validation_message = 'Sorry, I don''t recognize the command _' + cmd + '_. ' + \
            'These are the commands I know: _' + '_, _'.join(COMMAND_PARAMS.keys()) + '_.'

    elif len(parameter_list) < len(COMMAND_PARAMS[cmd]):
        valid = False
        validation_message = 'Looks like you don''t have enough inputs.\n' \
            + 'Expected format: `/ebird ' + cmd + ' ' + ' '.join(COMMAND_PARAMS[cmd]) + '`.'

    else:
        valid = True
        validation_message = 'Command received. Working on it!'

    return valid, validation_message, cmd, parameter_list


def handle_command(cmd, cmd_params, to_channel_id):

    print('Handling command...')

    func = getattr(commands, cmd)
    func(slack_client, ebird_client, cmd_params, to_channel_id)

    return


@app.route("/slack/ebird", methods=["POST"])
def command():

    msg = request.form
    print(msg)

    user_id = msg['user_id']
    full_command = msg['text'].split()
    cmd = full_command[0]

    print(cmd)

    # Validate parameters
    params_valid, validation_message, cmd, cmd_parameters = parse_parameters(full_command)

    if not params_valid:
        return make_response(validation_message, 200)

    else:
        thread = Thread(target=handle_command, args=(cmd, cmd_parameters, user_id))
        thread.start()

        return make_response(validation_message, 200)


# Start the Flask server
if __name__ == "__main__":
    app.run()
