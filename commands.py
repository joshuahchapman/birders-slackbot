from datetime import datetime


def recent(slack_client, ebird_client, cmd_params, to_channel_id):

    OPTIONAL_PARAMS = ['dist', 'back', 'cat', 'maxResults', 'includeProvisional', 'hotspot', 'sort', 'sppLocale']

    lat = cmd_params.pop(0)
    long = cmd_params.pop(0)

    print('lat={lat}, long={long}'.format(lat=lat, long=long))

    options = {}
    for param in cmd_params:
        print('parsing parameter: ' + param)
        parsed = param.split('=')
        if parsed[0] in OPTIONAL_PARAMS:
            options[parsed[0]] = parsed[1]
        else:
            print('Ignoring unrecognized parameter ' + parsed[0])

#    df = ebird_client.get_recent_observations_by_lat_long(lat, long, distance=8, days_back=3)
    df = ebird_client.get_recent_observations_by_lat_long(lat, long, distance=8, days_back=3)

    print('Rows returned: {rowcount}'.format(rowcount=len(df.index)))

    if df.empty or 'errors' in df.columns:
        return_message = 'eBird returned no observations near latitude ' + lat + ', longitude ' + long

    else:
        return_message = ''
        for index, row in df.iterrows():
            # Format the datetime nicely for display.
            pretty_dtm = datetime.strptime(row['obsDt'], '%Y-%m-%d %H:%M').strftime(
                '%-m/%-d at %-I:%M %p')
            return_message = return_message + '*' + row['comName'] + '*, ' + \
                row['locName'] + ', on ' + pretty_dtm + '\n'

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

    lat = cmd_params[0]
    long = cmd_params[1]

    print('lat={lat}, long={long}'.format(lat=lat, long=long))

    df = ebird_client.get_recent_notable_observations_by_lat_long(lat, long, distance=8, days_back=3)

    if df.empty or 'errors' in df.columns:
        return_message = 'eBird returned no notable observations near latitude ' + lat + ', longitude ' + long

    else:
        return_message = ''
        for index, row in df.iterrows():
            # Format the datetime nicely for display.
            pretty_dtm = datetime.strptime(row['obsDt'], '%Y-%m-%d %H:%M').strftime(
                '%-m/%-d at %-I:%M %p')
            return_message = return_message + '*' + row['comName'] + '*, ' + \
                row['locName'] + ', on ' + pretty_dtm + '\n'

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
