from collections import deque


def deepmatch(needle, haystack):
    """With a needle dictionary, recursively match all its keys to
    the haystack dictionary."""
    stream = deque([(needle, haystack)])

    while True:
        atom_left, atom_right = stream.pop()
        for k,v in atom_left.items():
            if isinstance(v, dict):
                if k not in atom_right:
                    return False
                stream.append((v, atom_right[k]))
            else:
                if atom_right.get(k) != v:
                    return False
        if not stream:
            break
    return True
