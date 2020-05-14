import re
from modules.constants import login_url
from modules.constants import main_url
from modules.constants import citizen_profile_url
from modules.constants import battle_console_url
from modules.constants import country_post_url
from fake_useragent import UserAgent


# raw data
def get_profile(session, citizen_id):
    url = citizen_profile_url + citizen_id
    response = session.get(url, headers={'User-Agent': UserAgent().chrome})
    citizen_profile_json = response.json()
    return citizen_profile_json


def get_token(session, username, password):
    # get server-generated token from erepublik
    response = session.get(login_url, headers={'User-Agent': UserAgent().chrome})
    token = re.search(r'id="_token" name="_token" value="(.+)" />', response.text)[1]

    # login to erepublik with credentials for parser account and confirm token
    request = {
        '_token': token,
        'citizen_email': username,
        'citizen_password': password,
        'remember': '1'
    }
    session.post(login_url, data=request, headers={'User-Agent': UserAgent().chrome})
    return token


def get_battle_page(session, token, battle_id, round, division, page):
    request = {'battleId': battle_id,
               'action': 'battleStatistics',
               'type': 'damage',
               'round': round,
               'division': division,
               'leftPage': page,
               'rightPage': page,
               '_token': token
               }
    response = session.post(battle_console_url, data=request, headers={'User-Agent': UserAgent().chrome})
    return response.json()


def get_country_post_page(session, token, page):
    request = {'page': page,
               '_token': token
               }
    response = session.post(country_post_url, data=request, headers={'User-Agent': UserAgent().chrome})
    return response.json()


def get_day(session):
    # get day from erepublik
    response = session.get(main_url, headers={'User-Agent': UserAgent().chrome})
    day = re.search(r'"eDay":(\d+),', response.text)[1]
    return day


# country feed
def get_rounds(session, token, page, stop=''):
    rounds = []

    num_round = 1
    num_page = 1
    while num_page < page:
        raw_post_page = get_country_post_page(session, token, num_page)
        wall_posts = raw_post_page['wallPosts']
        for post in wall_posts:
            # debug
            # print(post['createdAtTimeAgo'])
            if post['createdAtTimeAgo'] == stop:
                return rounds
            order = re.search(r'\[airunit\](\d{6}) (\w+) (\d+) (\d+)\[\/airunit\]', post['message'])
            if order:
                rounds.append([order[1], order[2], order[3], order[4]])
                num_round += 1
        num_page += 1
    return rounds


# airhit
def get_profile_airhit(session, citizen_id):
    citizen_profile_json = get_profile(session, citizen_id)
    level = citizen_profile_json['citizen']['level']
    rank_number = citizen_profile_json['military']['militaryData']['aircraft']['rankNumber']
    airhit = 10 * (1 + rank_number / 5) * (1.1 if level > 101 else 1.0)
    return int(airhit)


def update_squad_airhit(session, squad):
    for member in squad:
        # member - citizen_id, citizen_name, airhit, damage, hits
        member[2] = get_profile_airhit(session, str(member[0]))
    return squad


# damage
def get_round_stats(session, token, battle_id, battle_side, round, division):
    """ Get round stats using session, token, battle_id, battle_side, round and division"""
    round_stats = dict()
    # for 5 battle stats pages getting raw data and processing it
    num_page = 1
    while num_page <= 5:
        raw_stats = get_battle_page(session, token, battle_id, round, division, num_page)

        # extract fighter citizenId, citizenName and raw_value (damage/kills)
        fighter_data = raw_stats[battle_side]['fighterData']
        if fighter_data:
            for value in fighter_data.values():
                round_stats[value['citizenId']] = [value['citizenName'],
                                                   value['raw_value']]
        num_page += 1

    return round_stats


def update_squad_dmg(squad, round_stats):
    """ Update squad damage using squad and rounds stats """
    for member in squad:
        for fighter in round_stats.keys():
            if member[0] == fighter:
                # member - citizen_id, citizen_name, airhit, damage, hits
                # round_stats[fighter] - citizen_name, damage
                member[3] += round_stats[fighter][1]
    return squad


# hits
def update_squad_hits(squad):
    """ Updata squad hits using already collected squad data (dmg / hit) """
    for member in squad:
        # member - citizen_id, citizen_name, airhit, damage, hits
        member[4] = int(member[3] / member[2])
    return squad
