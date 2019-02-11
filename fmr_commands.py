import os
from sqlalchemy import create_engine, MetaData, Table, Column

db_uri = os.environ["DATABASE"]
engine = create_engine(db_uri)
meta = MetaData(engine)
user_circle = Table('user_circle', meta, autoload=True)

ROOT_CMD = '5mr'

# list of accepted commands and their required parameters
COMMAND_PARAMS = {
    'add_circle': ['latitude', 'longitude'],
    'list_circles': []
}


def parse_parameters(parameter_list):

    cmd = parameter_list.pop(0)

    if cmd not in COMMAND_PARAMS.keys():
        valid = False
        validation_message = 'Sorry, I don''t recognize the command _' + cmd + '_. ' + \
            'These are the commands I know: _' + '_, _'.join(COMMAND_PARAMS.keys()) + '_.'

    elif len(parameter_list) < len(COMMAND_PARAMS[cmd]):
        valid = False
        validation_message = 'Looks like you don''t have enough inputs.\n' \
            + 'Expected format: `/ ' + ROOT_CMD + ' ' + cmd + ' ' + ' '.join(COMMAND_PARAMS[cmd]) + '`.'

    else:
        valid = True
        validation_message = 'Command received. Working on it!'

    return valid, validation_message, cmd, parameter_list


def add_circle(user_id, lat, lon, radius_km=8, name=''):
    ins = user_circle.insert().values(user_id='dummyuser', latitude=47.2491706, longitude=-122.5969097,
                                      user_circle_name='mycir', radius_km=10)
    conn = engine.connect()

    print('Sending message to Slack (channel: {channel}): {msg}'.format(channel=to_channel_id, msg=return_message))

    # send channel a message
    channel_msg = slack_client.api_call(
        "chat.postMessage",
        channel=to_channel_id,
        text=return_message
    )

    if channel_msg['ok']:
        print('Message sent to Slack successfully')
    else:
        print('Error message from Slack: ' + channel_msg['error'])

    return
