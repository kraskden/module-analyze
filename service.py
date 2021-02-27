import os
import db
import api

import matplotlib.pyplot as plt
import numpy as np

TURRET_COUNT = 15

MODULES_MAP = db.json.loads("{\"Fox\":\"Firebird\",\"Badger\":\"Freeze\",\"Ocelot\":\"Isida\",\"Wolf\":\"Hammer\",\"Panther\":\"Twins\",\"Lion\":\"Ricochet\",\"Dolphin\":\"Smoky\",\"Orka\":\"Striker\",\"Shark\":\"Vulcan\",\"Grizzly\":\"Thunder\",\"Falcon\":\"Railgun\",\"Griffin\":\"Magnum\",\"Owl\":\"Gauss\",\"Eagle\":\"Shaft\",\"Spider\":\"Mines\"}")

def calculate_module_stat():
    users = load_users()
    logins = []
    for user in users:
        if ('state' in user) and (user['state']['rank'] > 30):
            logins.append(user['login'])
    
    stat = list([0.0 for _ in range(0, TURRET_COUNT)])
    ideal_stat = list([0.0 for _ in range(0, TURRET_COUNT)])
    stat_count = 0

    modules_stat = {}

    for login in logins:
        user = load_user(login)
        activities = user['currMonth']['activities'] if 'currMonth' in user else []
        modules = list(filter(lambda act: act['role'] == 'Module', activities))
        if len(list(filter(lambda mod: mod['name'].find('Spectrum') != -1, modules))) != 0:
            continue
        # Update modules_stat
        for module in modules:
            name = module['name']
            modules_stat[name] = modules_stat.get(name, 0) + module['time']

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

    modules_stat = dict((MODULES_MAP[name], val) for name, val in sorted(modules_stat.items(), key=lambda kv: kv[1]))
    

    print("Total players")
    print(stat_count)
    print("Percent stat")
    print(stat)
    print("Modules stat")
    print(modules_stat)

    # Uncomment to plot graph

    # plot_module_stat(modules_stat)
    # plot_module_pie(modules_stat)
    plot_stat(stat)
    # plot_both_stat(stat, ideal_stat)

def plot_module_stat(module_stat: dict):
    plt.rcdefaults()
    plt.barh(list(module_stat.keys()), list(map(lambda h: h/3600, module_stat.values())))
    plt.show()

def plot_module_pie(module_stat: dict):
    plt.rcdefaults()
    plt.pie(list(module_stat.values()), labels=list(module_stat.keys()))
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