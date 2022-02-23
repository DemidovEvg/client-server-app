def show_info(data):
    for obj in data:
        print(f'The type of "{obj}" is {type(obj)}.')


words_a = ('разработка', 'сокет', 'декоратор')

words_b = (
    '\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430',
    '\u0441\u043e\u043a\u0435\u0442',
    '\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440'
)

show_info(words_a)
show_info(words_b)
