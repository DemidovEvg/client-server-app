import csv
from chardet import detect
import re


def get_data(files_list):
    result_list = []

    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []

    _dict = {
        'Изготовитель системы': os_prod_list,
        'Название ОС': os_name_list,
        'Код продукта': os_code_list,
        'Тип системы': os_type_list
    }

    for filename in files_list:
        with open(filename, 'rb') as f:
            data = f.read()
            encoding = detect(data)['encoding']
            data = data.decode(encoding)

        for key, value in _dict.items():
            pattern = re.compile(fr'{key}:\s*\S*')
            value.append(pattern.findall(data)[0].split()[-1])

    result_list.append(list(_dict.keys()))
    result_list.extend(list(zip(*_dict.values())))

    return result_list


def write_to_csv(filename, files_list):
    data = get_data(files_list)

    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for row in data:
            writer.writerow(row)


FILES = ['info_1.txt', 'info_2.txt', 'info_3.txt']

write_to_csv('output.csv', FILES)
