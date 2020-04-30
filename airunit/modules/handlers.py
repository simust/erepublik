# standard modules
import json


# file handlers
def get_file_content(filename):
    """ Simply function that get content from file """
    with open(filename, "r") as file:
        file_content = file.read()
    content = json.loads(file_content)
    return content


def export_to_csv(filename, squad):
    with open(filename, "w") as file:
        # headers
        file.write('citizen_id,citizen_name,airhit,damage,hits\n')
        # body
        for key, value in squad.items():
            line = f'{key},{value[0]},{value[1]},{value[2]},{value[3]}\n'
            file.write(line)
