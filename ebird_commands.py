import slack_utilities as su

ROOT_CMD = '5mr'

# list of accepted commands and their required parameters
COMMAND_PARAMS = {
    'recent': ['latitude', 'longitude'],
    'recent_notable': ['latitude', 'longitude']
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


def recent(slack_client, ebird_client, cmd_params, to_channel_id):

    lat = cmd_params.pop(0)
    long = cmd_params.pop(0)

    print('lat={lat}, long={long}'.format(lat=lat, long=long))

    options = {}
    for param in cmd_params:
        print('parsing parameter: ' + param)
        parsed = param.split('=')
        options[parsed[0]] = parsed[1]

    # set default distance to 8km (~5mi), since most users are interested in Five Mile Radius birding
    if 'dist' not in options:
        options['dist'] = 8

    df = ebird_client.get_recent_observations_by_lat_long(lat, long, **options)

    print('Rows returned: {rowcount}'.format(rowcount=len(df.index)))

    if df.empty or 'errors' in df.columns:
        return_message = 'eBird returned no observations near latitude ' + lat + ', longitude ' + long

    else:
        return_message = su.format_observation_list(df)

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


def recent_notable(slack_client, ebird_client, cmd_params, to_channel_id):

    lat = cmd_params.pop(0)
    long = cmd_params.pop(0)

    print('lat={lat}, long={long}'.format(lat=lat, long=long))

    options = {}
    for param in cmd_params:
        print('parsing parameter: ' + param)
        parsed = param.split('=')
        options[parsed[0]] = parsed[1]

    # set default distance to 8km (~5mi), since most users are interested in Five Mile Radius birding
    if 'dist' not in options:
        options['dist'] = 8

    df = ebird_client.get_recent_notable_observations_by_lat_long(lat, long, **options)

    if df.empty or 'errors' in df.columns:
        return_message = 'eBird returned no notable observations near latitude ' + lat + ', longitude ' + long

    else:
        return_message = su.format_observation_list(df)

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
