import os
from threading import Thread
from flask import Flask, request, make_response
from slackclient import SlackClient
from ebird import EbirdClient
import slash_commands

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
EBIRD_TOKEN = os.environ["EBIRD_TOKEN"]

slack_client = SlackClient(SLACK_BOT_TOKEN)
ebird_client = EbirdClient(EBIRD_TOKEN)

app = Flask(__name__)


def handler_factory(message):
    slash_command = message['command']
    if slash_command in ['/5mr', '/fmr', '/test-5mr', '/test-fmr']:
        handler = slash_commands.FmrHandler(message)
    elif slash_command in ['/ebird', '/test-ebird']:
        handler = slash_commands.EbirdHandler(message)
    else:
        raise ValueError('Unrecognized slash command {}'.format(slash_command))
    return handler


@app.route("/slack/slashcmd", methods=["POST"])
def command():

    print(request.form)
    handler = handler_factory(request.form)
    params_valid, validation_message, subcommand, subcommand_parameters = slash_commands.parse_parameters(handler)

    if not params_valid:
        return make_response(validation_message, 200)

    func = getattr(handler, subcommand)
    thread = Thread(target=func, args=(slack_client, ebird_client, subcommand_parameters))
    thread.start()
    return make_response(validation_message + '\n`' + str(handler) + '`', 200)


# Start the Flask server
if __name__ == "__main__":
    app.run()
