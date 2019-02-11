import os
from sqlalchemy import create_engine, MetaData, Table

db_uri = os.environ["DATABASE_URL"]
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
            + 'Expected format: `/' + ROOT_CMD + ' ' + cmd + ' ' + ' '.join(COMMAND_PARAMS[cmd]) + '`.'

    else:
        valid = True
        validation_message = 'Command received. Working on it!'

    return valid, validation_message, cmd, parameter_list


def add_circle(slack_client, ebird_client, cmd_params, user_id):

    lat = cmd_params.pop(0)
    long = cmd_params.pop(0)

    options = {
        'user_id': user_id,
        'latitude': lat,
        'longitude': long
    }

    for param in cmd_params:
        print('parsing parameter: ' + param)
        parsed = param.split('=')
        options[parsed[0]] = parsed[1]

    # set default distance to 8km (~5mi)
    if 'radius_km' not in options:
        options['radius_km'] = 8

    # note for later: if you're going to issue an *update* on the table, you'll have to set updated_at explicitly;
    # the database won't handle it.

    # options = {
    #     'user_id': 'dummyuser2',
    #     'latitude': 34.1075142,
    #     'longitude': -118.2890215,
    #     'radius_km': 8
    # }

    try:
        conn = engine.connect()
        print('Connected successfully. Trying insert with the following options:')
        print(options)
        conn.execute(user_circle.insert(), options)
        return_message = 'Created a circle with radius ' + str(options['radius_km']) + ' centered at ' + \
            str(options['latitude']) + ', ' + str(options['longitude']) + '.'

    except:
        print('Database connection or insert failed.')
        return_message = 'Sorry, there was an error creating your circle. Please report the issue to an admin.'

    print('Sending message to Slack (channel: {channel}): {msg}'.format(channel=user_id, msg=return_message))

    # send channel a message
    channel_msg = slack_client.api_call(
        "chat.postMessage",
        channel=user_id,
        text=return_message
    )

    if channel_msg['ok']:
        print('Message sent to Slack successfully')
    else:
        print('Error message from Slack: ' + channel_msg['error'])

    return
