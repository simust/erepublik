# standard modules
import requests

# custom modules
from modules import handlers
from modules import erepublik
from modules import constants


if __name__ == "__main__":

    # get air unit list and rounds list from .json files
    airunit = handlers.get_file_content(constants.airunit_file)
    rounds = handlers.get_file_content(constants.rounds_file)
    countries = handlers.get_file_content(constants.countries_file)

    # start web session
    session = requests.session()

    # get airhit data
    airunit = erepublik.update_squad_airhit(session, airunit)

    # get erepublik token
    token = erepublik.get_token(session, constants.parser_username, constants.parser_password)

    # get country posts (experimental feature)
    # rounds = erepublik.get_rounds_dict(session, token, 7)
    # for value in rounds.values():
    #    value[1] = countries[value[1]]

    # collect damage data
    for value in rounds.values():
        round_stats = erepublik.get_round_stats(session, token,
                                                str(value[0]), str(value[1]), str(value[2]), str(value[3]))
        airunit = erepublik.update_squad_dmg(airunit, round_stats)

    # update hits data
    airunit = erepublik.update_squad_hits(airunit)

    # export to csv/excel
    handlers.export_to_csv('result.csv', airunit)
