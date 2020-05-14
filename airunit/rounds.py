# standard modules
import sqlite3
import requests

# custom modules
from modules import erepublik, constants

if __name__ == "__main__":
    # initialization
    rounds = []

    # start web session
    session = requests.session()

    # get erepublik token
    token = erepublik.get_token(session, constants.parser_username, constants.parser_password)

    # get last 24h rounds from country posts
    rounds = erepublik.get_rounds(session, token, 3, 'yesterday')

    # get current day
    day = erepublik.get_day(session)

    # prepare rounds for insert to db
    for r in rounds:
        # add erepublik day
        r.append(day)

    # add rounds to db
    connection = sqlite3.connect(constants.airunit_db)
    cursor = connection.cursor()
    cursor.executemany('INSERT INTO rounds VALUES(?, ?, ? ,?, ?)', rounds)
    connection.commit()
    connection.close()
