import yaml

DATA = {
    'key_list': ['value1', 'value2'],
    'integer': 4,
    'key_dict': {'key1': '20€', 'key2': '50€'},
}

with open('yaml.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(DATA, f, default_flow_style=False, allow_unicode=True)

with open("yaml.yaml", 'r', encoding='utf-8') as f:
    assert DATA == yaml.load(f, Loader=yaml.SafeLoader)
