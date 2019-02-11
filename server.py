import os
from threading import Thread
from flask import Flask, request, make_response
from slackclient import SlackClient
from ebird import EbirdClient
import ebird_commands
import fmr_commands

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
EBIRD_TOKEN = os.environ["EBIRD_TOKEN"]

slack_client = SlackClient(SLACK_BOT_TOKEN)
ebird_client = EbirdClient(EBIRD_TOKEN)

app = Flask(__name__)


@app.route("/slack/ebird", methods=["POST"])
def ebird_command():

    msg = request.form
    print(msg)

    user_id = msg['user_id']
    full_command = msg['text'].split()
    cmd = full_command[0]

    print(cmd)

    # Validate parameters
    params_valid, validation_message, cmd, cmd_parameters = ebird_commands.parse_parameters(full_command)

    if not params_valid:
        return make_response(validation_message, 200)

    else:
        func = getattr(ebird_commands, cmd)
        thread = Thread(target=func, args=(slack_client, ebird_client, cmd_parameters, user_id))
        thread.start()

        return make_response(validation_message, 200)


@app.route("/slack/fmr", methods=["POST"])
def fmr_command():

    msg = request.form
    print(msg)

    user_id = msg['user_id']
    full_command = msg['text'].split()
    cmd = full_command[0]

    print(cmd)

    # Validate parameters
    params_valid, validation_message, cmd, cmd_parameters = fmr_commands.parse_parameters(full_command)

    if not params_valid:
        return make_response(validation_message, 200)

    else:
        func = getattr(fmr_commands, cmd)
        thread = Thread(target=func, args=(slack_client, ebird_client, cmd_parameters, user_id))
        thread.start()

        return make_response(validation_message, 200)


# Start the Flask server
if __name__ == "__main__":
    app.run()
