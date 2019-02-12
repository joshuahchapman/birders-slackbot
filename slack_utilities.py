from datetime import datetime


def format_observation_list(observation_df):

    """
    There are baked-in assumptions here about the structure of the dataframe passed in.
    These should be spec'd out somewhere in the project besides in these comments....
    :param observation_df: includes obsDt, comName, locName.
    :return: string containing the observation list formatted for Slack
    """

    return_message = ''
    for index, row in observation_df.iterrows():
        # Format the datetime nicely for display.
        pretty_dtm = datetime.strptime(row['obsDt'], '%Y-%m-%d %H:%M').strftime(
            '%-m/%-d at %-I:%M %p')
        return_message = return_message + '*' + row['comName'] + '*, ' + \
                         row['locName'] + ', on ' + pretty_dtm + '\n'

    return return_message


# def parse_slash_request():

#    return
