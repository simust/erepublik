# standard modules
import json
import sqlite3


# file handlers
def get_json_content(filename):
    """ Get content from file """
    with open(filename, "r") as file:
        file_content = file.read()
    content = json.loads(file_content)
    return content


def export_to_csv(filename, headers, body):
    """ Export data to .csv file """
    with open(filename, "w") as file:
        # headers
        file.write(f'{headers}\n')
        # body
        for b in body:
            line = f'{b[0]},{b[1]},{b[2]},{b[3]},{b[4]}\n'
            file.write(line)


# database handlers
def db_select_query(dbname, query):
    """ Run select query to dbname and return result as list """
    connection = sqlite3.connect(dbname)
    connection.row_factory = lambda cur, row: list(row)
    cursor = connection.cursor()
    cursor.execute(query)
    content = cursor.fetchall()
    connection.close()
    return content


def db_insert_query(dbname, query, data):
    """ Run insert query to dbname """
    connection = sqlite3.connect(dbname)
    cursor = connection.cursor()
    cursor.executemany(query, data)
    connection.commit()
    connection.close()
