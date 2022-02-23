def not_ascii_filter(data):
    return filter(lambda x: not x.isascii(), data)


words = ('attribute', 'класс', 'функция', 'type')

print(f'Слова, которые невозможно записать в байтовом типе: '
      f'{", ".join(not_ascii_filter(words))}')
