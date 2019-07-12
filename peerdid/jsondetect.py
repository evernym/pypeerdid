def str_seems_like_json(txt):
    for c in txt:
        if c not in "\r\n\t ":
            return c == '{'
    return False


def bytes_seems_like_json(binary):
    for b in binary:
        if b not in [13, 10, 9, 32]:
            return b == 123
    return False



