from chardet import detect

file = 'file.txt'

with open(file, 'rb') as f:
    encoding = detect(f.read())['encoding']

with open(file, 'r', encoding=encoding) as f:
    print(f.read())
