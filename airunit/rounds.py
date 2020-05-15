# standard modules
import requests

# custom modules
from modules import erepublik, constants, handlers

if __name__ == "__main__":
    # initialization
    rounds = []

    # start web session
    session = requests.session()

    # get erepublik token
    token = erepublik.get_token(session, constants.parser_username, constants.parser_password)

    # get last 24h rounds from country posts
    rounds = erepublik.get_feed_rounds(session, token, 3, 'yesterday')

    # get current day
    day = erepublik.get_day(session)

    # prepare rounds for insert to db
    for r in rounds:
        # add erepublik day
        r.append(day)

    # add rounds to db
    query = 'INSERT INTO rounds VALUES(?, ?, ? ,?, ?)'
    handlers.db_insert_query(constants.airunit_db, query, rounds)
