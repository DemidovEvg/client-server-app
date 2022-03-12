import json


def write_order_to_json(item, quantity, price, buyer, date):
    try:
        with open('orders.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {'orders': []}

    orders_list = data['orders']

    new_order = {
        'item': item,
        'quantity': quantity,
        'price': price,
        'buyer': buyer,
        'date': date,
    }

    orders_list.append(new_order)

    with open('orders.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


for i in range(10):
    write_order_to_json(f'item{i}', i, i, f'name{i}', f'date{i}')
