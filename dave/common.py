import csv, json

class DataverseError(Exception):
    pass

def json_to_dict(data):
    try:
        return json.loads(data)
    except Exception as e:
        raise TypeError('Error while converting JSON data to dict {} ({})'.format(data, str(e)))

def dict_to_json(data):
    try:
        return json.dumps(data, ensure_ascii=True, indent=2)
    except Exception as e:
        raise TypeError('Error while converting dict to JSON {} ({})'.format(data, str(e)))

def read_file(filename, mode='r'):
    try:
        with open(filename, mode) as f:
            data = f.read()
        return data
    except Exception as e:
        raise IOError('Error while reading file {} ({})'.format(filename, str(e)))

def write_file(filename, data, mode='w'):
    try:
        with open(filename, mode) as f:
            f.write(data)
    except Exception as e:
        raise IOError('Error while writing file {} ({})'.format(filename, str(e)))

def read_file_json(filename):
    return json_to_dict(read_file(filename, 'r'))

def write_file_json(filename, data, mode='w'):
    write_file(filename, dict_to_json(data), mode)

def read_file_csv(filename):
    try:
        with open(filename, newline='') as csv_file:
            return csv.reader(csv_file, delimiter=',', quotechar='"')
    except Exception as e:
        raise IOError('Error while reading CSV file {} ({})'.format(filename, str(e)))
    finally:
        csv_file.close()

def read_csv_to_dict(filename):
    reader = csv.DictReader(open(filename), 'r')
    data = []
    for row in reader:
        data.append(dict(row))
    return data
