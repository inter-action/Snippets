import random

"""
random utils module
"""

def pick(range, interval, size):
    ''' note that if (interval + 1) * size >= range 
        you could get a result size that's less than you intended 
    '''
    result = []
    def _pick(l, r):
        if len(result) >= size:
            return 
        else:
            t = random.randrange(r - l) + l
            result.append(t)
            left = t - interval
            right = t + interval + 1
            if left > l:
                _pick(l, left)
            if right < r:
                _pick(right, r)

    _pick(0, range)
    return result


if __name__ == '__main__':
    data = pick(240, 15, 8)
    print(data.__repr__())
