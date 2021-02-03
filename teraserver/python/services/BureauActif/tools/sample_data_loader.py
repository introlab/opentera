import os
import csv


def parse_timers_file(fullpath):
    date = 'invalid'
    values = {'minutes_up': 0, 'minutes_down': 0}

    if 'Timers_' in fullpath and '.txt' in fullpath:
        date = fullpath.split('_')[1].split('.txt')[0]

        try:
            with open(fullpath) as file:
                values['minutes_up'] = float(file.readline().strip())
                values['minutes_down'] = float(file.readline().strip())
        except:
            print('Error reading: ', fullpath)

    # Return timers
    return {date: values}


def parse_config_file(fullpath):

    max_height = 0
    min_height = 0
    try:
        with open(fullpath) as file:
            max_height = float(file.readline().strip())
            min_height = float(file.readline().strip())
    except:
        print('Error reading: ', fullpath)
        return {'invalid': {}}

    return {'config': {'max_height': max_height, 'min_height': min_height}}


def parse_data_file(fullpath):
    # print('parse_data_file: ', fullpath)
    lines = []

    date = 'invalid'
    filename = os.path.split(fullpath)[1]

    if '_' in filename and '.dat' in filename:
        date = filename.split('_')[1].split('.dat')[0]
        try:
            with open(fullpath) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter='\t')
                for row in csv_reader:
                    # REMOVE EMPTY ELEMENTS CREATED BY TOW TABS
                    lines.append([row[0], row[1], row[2], row[3], row[5], row[7], row[9], row[11]])
        except csv.Error:
            print('Error reading: ', fullpath)

    # Return list of lines
    return {date: lines}


def load_data_from_path(path):

    file_data = {'config': {'max_height': 0, 'min_height': 0}}

    for root, subFolders, files in os.walk(path, topdown=True):
        # print(root, subFolders, files)

        # First pass, read data, create data structure
        for filename in files:
            # Data file
            if '.dat' in filename:
                result = parse_data_file(os.path.join(root, filename))

                # Fill data
                for res in result:
                    if res != 'invalid':
                        file_data[res] = {'data': result[res],
                                          'timers': {'minutes_up': 0, 'minutes_down': 0}}

            # Config file
            if '.txt' in filename:
                if 'Config' in filename:
                    result = parse_config_file(os.path.join(root, filename))

                    # Fill data
                    for res in result:
                        if res != 'invalid':
                            # Replace configuration
                            file_data['config'] = result[res]

                elif 'Timers_' in filename:
                    result = parse_timers_file(os.path.join(root, filename))
                    # Fill data
                    for res in result:
                        if res != 'invalid':
                            if file_data.__contains__(res):
                                file_data[res]['timers'] = result[res]
                            else:
                                print('missing data file for: ', res, ' skipping...')
            else:
                print('Unknown file:', filename, ' skipping...')

    return file_data


# if __name__ == '__main__':
#     result = load_data_from_path('/Users/dominic/Downloads/Rasp8')
#     print(result)
