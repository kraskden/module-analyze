import os

import db
import api

import matplotlib.pyplot as plt
import numpy as np

TURRET_COUNT = 15

MODULES_MAP = db.json.loads("{\"Fox\":\"Firebird\",\"Badger\":\"Freeze\",\"Ocelot\":\"Isida\",\"Wolf\":\"Hammer\",\"Panther\":\"Twins\",\"Lion\":\"Ricochet\",\"Dolphin\":\"Smoky\",\"Orka\":\"Striker\",\"Shark\":\"Vulcan\",\"Grizzly\":\"Thunder\",\"Falcon\":\"Railgun\",\"Griffin\":\"Magnum\",\"Owl\":\"Gauss\",\"Eagle\":\"Shaft\",\"Spider\":\"Mines\"}")

def get_played_logins():
    users = load_users()
    logins = []
    for user in users:
        if ('state' in user) and (user['state']['rank'] > 30):
            logins.append(user['login'])
    return logins

def get_usage_stat(role, month = 'currMonth'):
    logins = get_played_logins()
    res = {}
    total = len(logins)
    for login in logins:
        user = load_user(login)
        activities = user[month]['activities'] if month in user else []
        target_group = list(filter(lambda act: act['role'] == role, activities))
        if role == 'Module' and len(list(filter(lambda mod: mod['name'].find('Spectrum') != -1, target_group))) != 0:
            continue
        if (len(target_group) == 0):
            total = total - 1
        for entity in target_group:
            name = entity['name']
            res[name] = res.get(name, 0) + entity['time']
    
    print(total)
    key_mapper = lambda k: MODULES_MAP[k] if role == 'Module' else k
    return dict((key_mapper(k), v) for k, v in sorted(res.items(), key=lambda kv: kv[1]))

def calculate_module_stat():
    logins = get_played_logins()
    stat = list([0.0 for _ in range(0, TURRET_COUNT)])
    ideal_stat = list([0.0 for _ in range(0, TURRET_COUNT)])
    stat_count = 0

    for login in logins:
        user = load_user(login)
        activities = user['currMonth']['activities'] if 'currMonth' in user else []
        modules = list(filter(lambda act: act['role'] == 'Module', activities))
        if len(list(filter(lambda mod: mod['name'].find('Spectrum') != -1, modules))) != 0:
            continue
        times = sorted(map(lambda x: x['time'], modules), reverse=True)
        ideal_times = [1.0/TURRET_COUNT for _ in range(0, TURRET_COUNT)]
        full_time = sum(times)
        full_ideal_time = sum(ideal_times)
        if full_time != 0:
            for i in range(2, TURRET_COUNT):
                stat[i] = stat[i] + (sum(times[0:i+1]) / full_time) 
                ideal_stat[i] = ideal_stat[i] + (sum(ideal_times[0:i+1]) / full_ideal_time) 
            stat_count = stat_count + 1

    stat = list(map(lambda x: x / stat_count, stat))
    ideal_stat = list(map(lambda x: x / stat_count, ideal_stat))
    
    return (stat, ideal_stat)

def plot_all_usages_pie(usage: dict):
    plt.rcdefaults()
    for name in ['Module', 'Hull', 'Turret', 'Mode']:    
        plt.figure(name)
        plt.title(name + ' usage', fontdict={'fontsize': 'large', 'fontweight': 'bold'})
        plot_on_axe(plt, usage[name])

    plt.show()


def plot_on_axe(plt, usage_stat: dict):

    def get_labels():
        total = sum(usage_stat.values())
        return [f'{name} [{round(time/total * 100)}%]' for name, time in usage_stat.items()]

    plt.pie(list(usage_stat.values()), labels=get_labels())


def plot_usage_pie(usage_stat: dict):
    plt.rcdefaults()
    plt.pie(list(usage_stat.values()), labels=list(usage_stat.keys()))
    plt.show()

def plot_stat(stat: list):
    plt.rcdefaults()
    data = stat[2:]
    x = list(range(3, len(stat) + 1))
    plt.plot(x, data, linestyle='--', marker='o', color='b')
    plt.yticks(np.arange(0.5, 1.05, 0.05))
    plt.xticks(np.arange(3, len(stat) + 1, 1))
    plt.grid(True)
    plt.show()

def plot_both_stat(stat: list, ideal_stat: list):
    plt.rcdefaults()
    data = stat[2:]
    ideal_data = ideal_stat[2:]
    x = list(range(3, len(stat) + 1))
    plt.plot(x, data, linestyle='--', marker='o', color='b', label='Real')
    plt.yticks(np.arange(0.1, 1.05, 0.05))
    plt.xticks(np.arange(3, len(stat) + 1, 1))
    plt.grid(True)
    plt.plot(x, ideal_data, linestyle='--', marker='o', color='red', label='Ideal')
    plt.show()


def load_user(login):
    return _load_resource(f'/user/{login}/track', f'{db.USER_PREFIX}/{login}.json')

def load_users():
    return _load_resource('/users', db.USER_PATH)


def _load_resource(uri, db_path):
    if os.path.isfile(db_path):
        return db.load_json(db_path)
    else:
        return api.load_api_resource(uri, db_path)