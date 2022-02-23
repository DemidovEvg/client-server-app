def evaluate(data):
    for obj in data:
        result = eval(f'b"{obj}"')
        print(f'Object: "{result}"; type: {type(result)}; length: {len(result)}')


words = ('class', 'function', 'method')

evaluate(words)
