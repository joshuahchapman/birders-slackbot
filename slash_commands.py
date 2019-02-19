import os
from datetime import datetime
from sqlalchemy import create_engine, MetaData, Table, select, func, and_
import slack_utilities as su


def parse_parameters(handler):

    parameter_list = handler.subcommand_text.split()
    subcommand = parameter_list.pop(0)

    if subcommand not in handler.COMMAND_PARAMS.keys():
        valid = False
        validation_message = 'Sorry, I don''t recognize the command _' + subcommand + '_. ' + \
                             'These are the commands I know: _' + '_, _'.join(handler.COMMAND_PARAMS.keys()) + '_.'

    elif len(parameter_list) < len(handler.COMMAND_PARAMS[subcommand]):
        valid = False
        validation_message = "Looks like you don't have enough inputs.\n" \
                             + 'Expected format: `' + handler.command + ' ' + subcommand + ' ' + \
                             ' '.join(handler.COMMAND_PARAMS[subcommand]) + '`.'

    else:
        valid = True
        validation_message = 'Command received. Working on it!'

    return valid, validation_message, subcommand, parameter_list


class FmrHandler:

    # list of accepted commands and their required parameters
    COMMAND_PARAMS = {
        'add_circle': ['latitude', 'longitude'],
        'list_circles': [],
        'set_default': ['circle_name'],
        'recent': [],
        'recent_notable': []
    }

    def __init__(self, message):
        self.command = message['command']
        self.user_id = message['user_id']
        self.subcommand_text = message['text']
        # TO DO: move db stuff to be called only at the time when the subcommand requires it.
        self.db_uri = os.environ["DATABASE_URL"]
        self.engine = create_engine(self.db_uri)
        self.meta = MetaData(self.engine)
        self.user_circle = Table('user_circle', self.meta, autoload=True)
        return

    def __str__(self):
        return self.command + ' ' + self.subcommand_text

    def add_circle(self, slack_client, ebird_client, cmd_params):
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
            'user_id': self.user_id,
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
        conn = self.engine.connect()
        print('Connected successfully. Checking for existing circle for this user and name.')
        s = select([func.count()]).where(and_(self.user_circle.c.user_id == self.user_id,
                                              self.user_circle.c.user_circle_name == options['user_circle_name']))
        result = conn.execute(s)
        row = result.fetchone()
        result.close()
        print(row)

        circle_exists = row[0]
        if circle_exists != 0:
            return_message = 'You already have a circle called ' + options['user_circle_name'] + '. ' + \
                'Please try again with a different name.'
            su.post_message(slack_client, self.user_id, return_message)
            return

        # check if the user already has a default circle.
        conn = self.engine.connect()
        print('Connected successfully. Checking for existing default circle for this user.')
        s = select([func.count()]).where(and_(self.user_circle.c.user_id == self.user_id,
                                              self.user_circle.c.user_default_circle == 1))
        result = conn.execute(s)
        row = result.fetchone()
        result.close()
        print(row)

        has_default = row[0]
        options['user_default_circle'] = 1 if has_default == 0 else 0

        try:
            conn = self.engine.connect()
            print('Connected successfully. Trying insert with the following options:')
            print(options)
            conn.execute(self.user_circle.insert(), options)
            return_message = 'Created a circle called ' + options['user_circle_name'] + ' with a radius of ' + \
                             str(options['radius_km']) + 'km, centered at ' + str(options['latitude']) + ', ' + \
                             str(options['longitude']) + '.'

        except:
            print('Database connection or insert failed.')
            return_message = 'Sorry, there was an error creating your circle. Please report the issue to an admin.'

        su.post_message(slack_client, self.user_id, return_message)

        return

    def list_circles(self, slack_client, ebird_client, cmd_params):

        conn = self.engine.connect()
        print('Connected successfully. Pulling circles for this user.')
        s = select([self.user_circle]).where(and_(self.user_circle.c.user_id == self.user_id, self.user_circle.c.deleted == 0))
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

        su.post_message(slack_client, self.user_id, msg)

        return

    def set_default(self, slack_client, ebird_client, cmd_params):

        print(cmd_params)

        new_default_name = cmd_params[0]

        conn = self.engine.connect()
        print('Connected successfully. Verifying existence of circle ' + new_default_name + ' for user ' + self.user_id + '.')
        s = select([self.user_circle]).where(and_(self.user_circle.c.user_id == self.user_id,
                                                  self.user_circle.c.user_circle_name == new_default_name))
        result = conn.execute(s)
        row = result.fetchone()
        result.close()
        print(row)

        if row is None:
            return_message = 'You don''t have a circle named ' + new_default_name + '. Please try again. ' + \
                'You can use `' + self.command + ' list_circles` to see the names of your circles.'
            su.post_message(slack_client, self.user_id, return_message)
            return

        # get current default circle, which will have to be un-set
        s = select([self.user_circle]).where(and_(self.user_circle.c.user_id == self.user_id,
                                             self.user_circle.c.user_default_circle == 1))
        result = conn.execute(s)
        # assumes only 1 default is set at any given time.
        row = result.fetchone()
        result.close()

        u = self.user_circle.update().values(user_default_circle=0, updated_at=datetime.now()).\
            where(self.user_circle.c.user_circle_id == row['user_circle_id'])
        conn.execute(u)

        # set new default
        u = self.user_circle.update().values(user_default_circle=1, updated_at=datetime.now()).\
            where(and_(self.user_circle.c.user_id == self.user_id, self.user_circle.c.user_circle_name == new_default_name))
        conn.execute(u)

        return_message = 'Successfully set circle ' + new_default_name + ' to be your new default.'
        su.post_message(slack_client, self.user_id, return_message)

        return

    def recent(self, slack_client, ebird_client, cmd_params):

        options = {}
        for param in cmd_params:
            print('parsing parameter: ' + param)
            parsed = param.split('=')
            options[parsed[0]] = parsed[1]

        # optional parameters for eBird: back, cat, maxResults, includeProvisional, hotspot, sort, sppLocale
        # lat, lng, and dist would not make sense here, since they're looked up from the database
        # other optional parameters: circle_name

        conn = self.engine.connect()
        print('Connected successfully. Trying select for user_id: ' + self.user_id)

        if 'circle_name' in options:
            s = select([self.user_circle]).where(and_(self.user_circle.c.user_id == self.user_id,
                                                      self.user_circle.c.user_circle_name == options['circle_name']))
        else:
            s = select([self.user_circle]).where(and_(self.user_circle.c.user_id == self.user_id,
                                                      self.user_circle.c.user_default_circle == 1))
        result = conn.execute(s)
        row = result.fetchone()
        result.close()
        print(row)

        circle_name = row['user_circle_name']
        lat = row['latitude']
        long = row['longitude']
        options['dist'] = row['radius_km']

        df = ebird_client.get_recent_observations_by_lat_long(lat, long, **options)

        print('Rows returned: {rowcount}'.format(rowcount=len(df.index)))

        if df.empty or 'errors' in df.columns:
            return_message = 'eBird returned no observations in circle ' + circle_name + '.'
        else:
            return_message = 'Recent observations from circle *' + circle_name + '*:\n'
            return_message = return_message + su.format_observation_list(df)

        su.post_message(slack_client, self.user_id, return_message)

        return

    def recent_notable(self, slack_client, ebird_client, cmd_params):

        options = {}
        for param in cmd_params:
            print('parsing parameter: ' + param)
            parsed = param.split('=')
            options[parsed[0]] = parsed[1]

        # optional parameters for eBird: back, maxResults, detail, hotspot
        # lat, lng, and dist would not make sense here, since they're looked up from the database
        # other optional parameters: circle_name

        conn = self.engine.connect()
        print('Connected successfully. Trying select for user_id: ' + self.user_id)

        if 'circle_name' in options:
            s = select([self.user_circle]).where(and_(self.user_circle.c.user_id == self.user_id,
                                                      self.user_circle.c.user_circle_name == options['circle_name']))
        else:
            s = select([self.user_circle]).where(and_(self.user_circle.c.user_id == self.user_id,
                                                      self.user_circle.c.user_default_circle == 1))
        result = conn.execute(s)
        row = result.fetchone()
        result.close()
        print(row)

        circle_name = row['user_circle_name']
        lat = row['latitude']
        long = row['longitude']
        options['dist'] = row['radius_km']

        df = ebird_client.get_recent_notable_observations_by_lat_long(lat, long, **options)

        print('Rows returned: {rowcount}'.format(rowcount=len(df.index)))

        if df.empty or 'errors' in df.columns:
            return_message = 'eBird returned no notable observations in circle ' + circle_name + '.'
        else:
            return_message = 'Recent notable observations from circle *' + circle_name + '*:\n'
            return_message = return_message + su.format_observation_list(df)

        su.post_message(slack_client, self.user_id, return_message)

        return


class EbirdHandler:

    # list of accepted commands and their required parameters
    COMMAND_PARAMS = {
        'recent': ['latitude', 'longitude'],
        'recent_notable': ['latitude', 'longitude']
    }

    def __init__(self, message):
        self.command = message['command']
        self.user_id = message['user_id']
        self.subcommand_text = message['text']
        return

    def __str__(self):
        return self.command + ' ' + self.subcommand_text

    def recent(self, slack_client, ebird_client, cmd_params, to_channel_id):

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
        su.post_message(slack_client, self.user_id, return_message)
        return

    def recent_notable(self, slack_client, ebird_client, cmd_params, to_channel_id):

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
        su.post_message(slack_client, self.user_id, return_message)
        return
