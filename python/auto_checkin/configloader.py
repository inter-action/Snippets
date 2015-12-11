import configparser
import os
from datetime import datetime
import re

CONFIG_FILENAME = 'init.ini'


def _get_configure():
    if not os.path.exists(CONFIG_FILENAME):
        raise Exception(" %s config file can not be found" % CONFIG_FILENAME)
    config = configparser.ConfigParser()
    config.read(CONFIG_FILENAME)
    return config


def get_checkin_users():
    users = []
    users_section = _get_configure()['users']
    for entry in users_section:
        if '.' not in entry:
            u = {}
            u['username'] = entry
            u['password'] = users_section[entry]
            users.append(u)
    return users

def get_checkout_users():
    users = []
    users_section = _get_configure()['users']
    for entry in users_section:
        if '.' not in entry \
            and entry+'.checkout' in users_section \
            and users_section[entry+'.checkout'] == 'true' : # username entry

            u = {}
            u['username'] = entry
            u['password'] = users_section[entry]
            users.append(u)
    return users

def _get_op_weekdays(weekday_str):
    ''' load running weekdays configration 

        Returns:
            weekdays tuple
    '''
    result = None
    try:
        result = tuple(int(i) for i in weekday_str.split(','))
    except Exception as e:
        raise Exception('invalid weekday configration format')
    return result


def get_sched_config_map():
    sys_section = _get_configure()['sched_config']
    int_matcher = re.compile(r'^\d*$')
    m = {}
    for entry in sys_section:
        value = sys_section[entry]
        if int_matcher.match(value) is not None:
            m[entry] = int(value)
        else:
            m[entry] = value

    m['stop_date'] = datetime.strptime(m['stop_date'], '%Y-%m-%d')
    m['op_weekday'] = _get_op_weekdays(m['op_weekday'])
    return m


if __name__ == '__main__':
    # print('%s' % weekday_tuple().__repr__())
    print('%s' % get_sched_config_map().__repr__())
    # raise LoginFailureException('blah, blah, blah')
