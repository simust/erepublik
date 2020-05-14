# standard modules
import requests

# custom modules
from modules import handlers, erepublik, constants

if __name__ == "__main__":
    # initialization
    airunit = []
    rounds = []

    # start web session
    session = requests.session()

    # get airunit list from db
    query = """ SELECT * FROM airunit """
    airunit = handlers.db_select_query(constants.airunit_db, query)

    # get airhit data
    airunit = erepublik.update_squad_airhit(session, airunit)

    # get erepublik token
    token = erepublik.get_token(session, constants.parser_username, constants.parser_password)

    # get last 7d rounds list from db
    day = erepublik.get_day(session)
    query = """ SELECT battle_id, country_id, round, division FROM rounds
                JOIN countries ON rounds.battle_side = countries.country_name 
                WHERE day > {}""".format(int(day)-7)
    rounds = handlers.db_select_query(constants.airunit_db, query)

    # collect rounds damage data
    for r in rounds:
        round_stats = erepublik.get_round_stats(session, token,
                                                str(r[0]), str(r[1]), str(r[2]), str(r[3]))
        airunit = erepublik.update_squad_dmg(airunit, round_stats)

    # update hits data
    airunit = erepublik.update_squad_hits(airunit)

    # export to csv/excel
    handlers.export_to_csv('export/airunit.csv', 'citizen_id,citizen_name,airhit,damage,hits', airunit)
