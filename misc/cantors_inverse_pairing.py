from math import floor, sqrt


def cantors_pi(index):
    w = (floor(sqrt(8 * index + 1)) - 1) // 2
    t = (w * (w + 1)) // 2
    y = index - t
    x = w - y
    return x, y


def main():
    import numpy as np
    locs = np.zeros([5, 5])
    for i in range(200):
        try:
            locs[cantors_pi(i)] = i
        except IndexError:
            pass
    print(locs)


if __name__ == '__main__':
    main()
