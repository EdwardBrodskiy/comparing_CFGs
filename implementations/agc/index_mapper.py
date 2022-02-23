from math import floor, ceil, sqrt
from typing import Tuple


def map_to_space(index: int, x_bound, y_bound):  # wrap the original algorithm to make both bounds exclusive
    return cantors_extended_pi(index, x_bound - 1, y_bound)


def cantors_extended_pi(index: int, x_bound: int, y_bound: int) -> Tuple[int, int]:
    """
    index to bounded 2D space mapper from Automating Grammar Comparison paper
    """
    # for compatibility with original definition in the paper
    z = index

    # number of indices until x space is filled i.e (x, 0) is not available
    zx = (x_bound + 1) * (x_bound + 2) // 2

    # number of indices until y space is filled i.e (0, y) is not available
    zy = y_bound * (y_bound + 1) // 2

    # when to begin closing the bottom right corner i.e when both x and y bounds run out of space
    zb = get_zb(y_bound, x_bound, zx, zy)

    # select behavior given the prior defined bounds
    if z >= zb:
        t, w = b_skip(z, x_bound, y_bound)
    elif zx <= z < zb:
        t, w = x_skip(z, x_bound)
    elif zy <= z < zb:
        t, w = y_skip(z, y_bound)
    else:
        t, w = simple(z)

    y = z - t
    x = w - y
    return x, y


def get_zb(yb, xb, zx, zy):
    if xb > yb - 1:
        return yb * (xb - yb + 1) + zy
    elif yb - 1 > xb:
        return (xb + 1) * (yb - xb - 1) + zx
    else:
        return zy


def b_skip(z, xb, yb):  # handle the mirror of simple i.e the closing corner
    sb = xb ** 2 + yb ** 2
    wb = xb + yb
    r = 2 * wb + 1

    in_w_sqrt = r ** 2 - 8 * z - 4 * sb + 4 * yb - 4 * xb
    w = (r - ceil(sqrt(in_w_sqrt))) // 2

    t = ((2 * wb - 1) * w - w ** 2 - sb + wb) // 2
    return t, w


def x_skip(z, xb):  # handle preventing x direction overflow
    w = (2 * z + xb ** 2 + xb) // (2 * (xb + 1))
    t = (2 * w * xb - xb ** 2 + xb) // 2
    return t, w


def y_skip(z, yb):  # handle preventing y direction overflow
    w = (2 * z + yb ** 2 - yb) // (2 * yb)
    t = (2 * w * yb - yb ** 2 + yb) // 2
    return t, w


def simple(z):  # Cantor's expansion for before bounds are reached
    w = (floor(sqrt(8 * z + 1)) - 1) // 2
    t = w * (w + 1) // 2
    return t, w


def main():
    import numpy as np
    dim = (6, 4)
    locs = np.ones(dim) * -1
    missed = set()
    for i in range(dim[0] * dim[1]):
        coords = map_to_space(i, *dim)
        try:
            locs[coords] = i
        except IndexError:
            missed.add((coords, i))
    print(locs)
    print(missed)
    return


if __name__ == '__main__':
    main()
