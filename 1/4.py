def encode(data, encoding):
    return list(map(lambda x: bytes(x.encode(encoding)), data))


def decode(data, encoding):
    return list(map(lambda x: x.decode(encoding), data))


words = ['разработка', 'администрирование', 'protocol', 'standard']
encoding = 'utf-8'

enc_words = encode(words, encoding)
print(enc_words)

dec_words = decode(enc_words, encoding)
print(dec_words)
