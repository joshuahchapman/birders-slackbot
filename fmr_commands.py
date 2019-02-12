import os
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, select, func, and_
import slack_utilities as su

db_uri = os.environ["DATABASE_URL"]
print(db_uri)
engine = create_engine(db_uri)
meta = MetaData(engine)
user_circle = Table('user_circle', meta, autoload=True)

ROOT_CMD = '5mr'

# list of accepted commands and their required parameters
COMMAND_PARAMS = {
    'add_circle': ['latitude', 'longitude'],
    'list_circles': [],
    'recent': []
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
    """
    To create a circle, you need the following fields:
    - user_id
    - latitude
    - longitude
    - user_circle_name (alias: name. This function will default it.)
    - radius_km (alias: dist. This function will default it.)
    - user_default_circle (For now, set by this function, not by the user.)
    :param slack_client:
    :param ebird_client:
    :param cmd_params:
    :param user_id:
    :return:
    """

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
        if 'dist' in options:
            options['radius_km'] = options['dist']
        else:
            options['radius_km'] = 8

    # set default circle name
    if 'user_circle_name' not in options:
        if 'name' in options:
            options['user_circle_name'] = options['name']
        else:
            options['user_circle_name'] = 'circle1'

    # note for later: if you're going to issue an *update* on the table, you'll have to set updated_at explicitly;
    # the database won't handle it.

    # check if the user already has a circle by this name.
    conn = engine.connect()
    print('Connected successfully. Checking for existing circle for this user and name.')
    s = select([func.count()]).where(and_(user_circle.c.user_id == user_id,
                                          user_circle.c.user_circle_name == options['user_circle_name']))
    result = conn.execute(s)
    row = result.fetchone()
    result.close()
    print(row)

    circle_exists = row[0]
    if circle_exists != 0:
        return_message = 'You already have a circle called ' + options['user_circle_name'] + '. ' + \
            'Please try again with a different name.'
        su.post_message(slack_client, user_id, return_message)
        return

    # check if the user already has a default circle.
    conn = engine.connect()
    print('Connected successfully. Checking for existing default circle for this user.')
    s = select([func.count()]).where(and_(user_circle.c.user_id == user_id,
                                          user_circle.c.user_default_circle == 1))
    result = conn.execute(s)
    row = result.fetchone()
    result.close()
    print(row)

    has_default = row[0]
    options['user_default_circle'] = 1 if has_default == 0 else 0

    try:
        conn = engine.connect()
        print('Connected successfully. Trying insert with the following options:')
        print(options)
        conn.execute(user_circle.insert(), options)
        return_message = 'Created a circle called ' + options['user_circle_name'] + ' with a radius of ' + \
                         str(options['radius_km']) + 'km, centered at ' + str(options['latitude']) + ', ' + \
                         str(options['longitude']) + '.'

    except:
        print('Database connection or insert failed.')
        return_message = 'Sorry, there was an error creating your circle. Please report the issue to an admin.'

    su.post_message(slack_client, user_id, return_message)

    return


def list_circles(slack_client, ebird_client, cmd_params, user_id):

    conn = engine.connect()
    print('Connected successfully. Pulling circles for this user.')
    s = select([user_circle]).where(and_(user_circle.c.user_id == user_id), user_circle.c.deleted == 0)
    result = conn.execute(s)
    rows = result.fetchall()
    result.close()

    print(rows)
    msg = ''
    for row in rows:
        msg = msg + '*' + row['user_circle_name'] + '*, radius ' + str(row['radius_km']) + 'km, lat ' + \
            str(float(row['latitude'])) + ', lon ' + str(float(row['longitude'])) + ', default: ' + \
            ('YES' if row['user_default_circle'] == 1 else 'NO') + '\n'
    print(msg)

    su.post_message(slack_client, user_id, msg)

    return


def set_default_circle(slack_client, ebird_client, cmd_params, user_id):

    print(cmd_params)

    new_default_name = cmd_params[0]

    conn = engine.connect()
    print('Connected successfully. Verifying existence of circle ' + new_default_name + ' for user ' + user_id + '.')
    s = select([user_circle]).where(and_(user_circle.c.user_id == user_id,
                                         user_circle.c.user_circle_name == new_default_name))
    result = conn.execute(s)
    row = result.fetchone()
    result.close()
    print(row)

    if row is None:
        return_message = 'You don''t have a circle named ' + new_default_name + '. Please try again. ' + \
            'You can use `' + ROOT_CMD + ' list_circles` to see the names of your circles.'
        su.post_message(slack_client, user_id, return_message)
        return

    # get current default circle, which will have to be un-set
    s = select([user_circle]).where(and_(user_circle.c.user_id == user_id,
                                         user_circle.c.user_default_circle == 1))
    result = conn.execute(s)
    # assumes only 1 default is set at any given time.
    row = result.fetchone()
    result.close()

    u = user_circle.update().values(user_default_circle=0, updated_at=datetime.now()).\
        where(user_circle.c.user_circle_id == row['user_circle_id'])
    conn.execute(u)

    # set new default
    u = user_circle.update().values(user_default_circle=1, updated_at=datetime.now()).\
        where(and_(user_circle.c.user_id == user_id, user_circle.c.user_circle_name == new_default_name))
    conn.execute(u)

    return_message = 'Successfully set circle ' + new_default_name + ' to be your new default.'
    su.post_message(slack_client, user_id, return_message)
    
    return


def recent(slack_client, ebird_client, cmd_params, user_id):

    options = {}
    for param in cmd_params:
        print('parsing parameter: ' + param)
        parsed = param.split('=')
        options[parsed[0]] = parsed[1]

    # optional parameters: back, cat, maxResults, includeProvisional, hotspot, sort, sppLocale
    # lat, lng, and dist would not make sense here, since they're looked up from the database

    conn = engine.connect()
    print('Connected successfully. Trying select for user_id: ' + user_id)

    if 'user_circle_name' in options:
        s = select([user_circle]).where(and_(user_circle.c.user_id == user_id,
                                        user_circle.c.user_circle_name == options['user_circle_name']))

    else:
        s = select([user_circle]).where(and_(user_circle.c.user_id == user_id,
                                        user_circle.c.user_default_circle == 1))
    result = conn.execute(s)
    row = result.fetchone()
    result.close()
    print(row)

    lat = row['latitude']
    long = row['longitude']
    options['dist'] = row['radius_km']

    df = ebird_client.get_recent_observations_by_lat_long(lat, long, **options)

    print('Rows returned: {rowcount}'.format(rowcount=len(df.index)))

    if df.empty or 'errors' in df.columns:
        return_message = 'eBird returned no observations near latitude ' + lat + ', longitude ' + long
    else:
        return_message = su.format_observation_list(df)

    su.post_message(slack_client, user_id, return_message)

    return
