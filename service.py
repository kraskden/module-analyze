import os
from typing import Tuple

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

def get_supplies_stat():
    logins = get_played_logins()
    res = {}
    for login in logins:
        user = load_user(login)
        supplies = user['currMonth']['supplies'] if 'currMonth' in user else []
        for supply in supplies:
            name = supply['name']
            res[name] = res.get(name, 0) + supply['count']
    return {k: v for k, v in sorted(res.items(), key=lambda kv: kv[1])}

def get_usage_stat(role, month = 'currMonth'):
    logins = get_played_logins()
    times = {}
    scores = {}
    rel_times = {}
    rel_scores = {}
    used_logins = []
    for login in logins:
        user = load_user(login)
        activities = user[month]['activities'] if month in user else []
        target_group = list(filter(lambda act: act['role'] == role, activities))
        if role == 'Module' and len(list(filter(lambda mod: mod['name'].find('Spectrum') != -1, target_group))) != 0:
            continue
        if (len(activities) > 0):
            used_logins.append(login)
        time_sum = sum(map(lambda t: t['time'], target_group))
        score_sum = sum(map(lambda t: t['score'], target_group))

        for entity in target_group:
            name = entity['name']
            times[name] = times.get(name, 0) + entity['time']
            scores[name] = scores.get(name, 0) + entity['score']
            rel_times[name] = rel_times.get(name, 0) + entity['time'] / time_sum
            rel_scores[name] = rel_scores.get(name, 0) + entity['score'] / score_sum

    
    print(used_logins, len(used_logins))
    key_mapper = lambda k: MODULES_MAP[k] if role == 'Module' else k

    res_mapper = lambda items : dict((key_mapper(k), v) for k, v in sorted(items.items(), key=lambda kv: kv[1]))
    return res_mapper(times), res_mapper(scores), res_mapper(rel_times), res_mapper(rel_scores)

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
    for name in usage.keys():    
        # plt.figure(name)
        # plt.title(name + ' usage', fontdict={'fontsize': 'large', 'fontweight': 'bold'})
        times, scores, rel_times, rel_scores = usage[name]
        colours = {}
        for idx, cat in enumerate(times.keys()):
            colours[cat] = f'C{idx}'

        plot_on_axe(name, plt, times, scores, colours)
        plot_on_axe(f'Relative {name}', plt, rel_times, rel_scores, colours)

    plt.show()


def plot_on_axe(cat: str, plt, times: dict, scores: dict, colours: dict):

    fig, (ax1, ax2) = plt.subplots(1, 2)

    fig.canvas.set_window_title(cat)

    def get_labels(items):
        total = sum(items.values())
        return [f'{name} [{round(param/total * 100)}%]' for name, param in items.items()]

    ax1.pie(list(times.values()), labels=get_labels(times), colors=[colours[label] for label in times.keys()])
    ax1.set_title(f"{cat}s by time")

    ax2.pie(list(scores.values()), labels=get_labels(scores), colors=[colours[label] for label in scores.keys()])
    ax2.set_title(f"{cat}s by score")


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