from collections import deque


def deepmatch(needle, haystack):
    """With a needle dictionary, recursively match all its keys to
    the haystack dictionary."""
    stream = deque([(needle, haystack)])

    while True:
        atom_left, atom_right = stream.pop()
        for key, value in atom_left.items():
            if isinstance(value, dict):
                if key not in atom_right:
                    return False
                stream.append((value, atom_right[key]))
            else:
                if atom_right.get(key) != value:
                    return False
        if not stream:
            break
    return True
