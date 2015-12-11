from datetime import datetime as _datetime
import autocheckin
import configloader
import logutil
import sched
import time
import randutil
import sys


log = logutil.get_logger()

# global variables are captialized
Job_q         = sched.scheduler(time.time, time.sleep)
Checkin_flag  = {}
Checkout_flag = {}


'''
    CONFIG_MAP are loaded from configloader module, which contains info like:
        
        checkin_begin_hour  = 8
        checkin_begin_min   = 55
        checkin_window_secs = 240

        checkout_begin_hour  = 18
        checkout_begin_min   = 20
        checkout_window_secs = 240

        # to which day this program runs.
        stop_date = 2013-12-21

        # at weekday checkin runs, comma separated, 0-6(mon-sun)
        op_weekday = 0, 1, 2, 3, 4

'''
CONFIG_MAP = configloader.get_sched_config_map()

def schedule_checkin(key):
    log.info('===  %s  ========================================================\n' % key)
    log.info('start scheduling checkins, key:%s' % key)

    Checkin_flag[key] = True
    users             = configloader.get_checkin_users()
    checkin_timeline  = randutil.pick(CONFIG_MAP['checkin_window_secs'], 15, 2 * len(users))

    log.info('generated checkin timeline: %s' % checkin_timeline.__repr__())

    for i in range(0, len(users)):
        Job_q.enter(checkin_timeline[i], 1, autocheckin.checkin, argument=(users[i],))

    # second round, do it for guarantee
    for i in range(0, len(users)):
        Job_q.enter(CONFIG_MAP['checkin_window_secs'] + 30, 1, autocheckin.checkin, argument=(users[i],))

    Job_q.run()

def schedule_checkout(key):
    log.info('start scheduling checkouts, key:%s' % key)

    Checkout_flag[key] = True
    users              = configloader.get_checkout_users()
    checkout_timeline  = randutil.pick(CONFIG_MAP['checkout_window_secs'], 15, 2 * len(users))

    log.info('generated checkout timeline: %s ' % checkout_timeline.__repr__())

    for i in range(0, len(users)):
        Job_q.enter(checkout_timeline[i], 1, autocheckin.checkout, argument=(users[i],))

    # second round, after 60secs, do it for guarantee
    for i in range(0, len(users)):
        Job_q.enter(CONFIG_MAP['checkout_window_secs'] + 30, 1, autocheckin.checkout, argument=(users[i],))

    Job_q.run()


def run():
    log.info('---------------------- System have started successfully ------------------------')
    
    global Checkin_flag, Checkout_flag
    while True:
        global CONFIG_MAP
        CONFIG_MAP   = configloader.get_sched_config_map()
        today        = _datetime.now()
        cur_weekday  = today.weekday()
        now          = today.timetuple()

        curyear, curmon, curday, curhour, curmin = now[0], now[1], now[2], now[3], now[4]
        key = '%d%d%d' %  (curyear, curmon, curday)
        
        # exit when today exceed configured stop date
        if today >= CONFIG_MAP['stop_date']:
            log.info('system exit');
            sys.exit(0)

        # sleep 5 hour if not in checkin weekday, and skip any excution after this if block
        if cur_weekday not in CONFIG_MAP['op_weekday']:
            log.info('we skip %s day' % key)
            time.sleep(3600 * 5)
            continue

        # if today we haven't do any checkin yet
        if key not in Checkin_flag:
            Checkin_flag = {}  # reset map
            Checkin_flag[key] = False

        # if today we haven't do any checkout yet
        if key not in Checkout_flag:
            Checkout_flag = {}
            Checkout_flag[key] = False

        # if we are in checkin time zone
        if curhour==CONFIG_MAP['checkin_begin_hour'] \
            and curmin >=CONFIG_MAP['checkin_begin_min'] \
            and curmin < CONFIG_MAP['checkin_begin_min'] + CONFIG_MAP['checkin_window_secs']//60 \
            and not Checkin_flag[key]:

            # start checkins
            schedule_checkin(key)
            
        elif curhour>=CONFIG_MAP['checkout_begin_hour'] \
            and curmin >=CONFIG_MAP['checkout_begin_min'] \
            and curmin < CONFIG_MAP['checkout_begin_min'] + CONFIG_MAP['checkout_window_secs']//60 \
            and not Checkout_flag[key]:
            
            # start checkouts
            schedule_checkout(key)
        else:
            time.sleep(60)


if __name__ == '__main__':
    run()
