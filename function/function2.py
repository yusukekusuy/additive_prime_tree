from math import prod, lcm
from itertools import permutations
from function.primitive_sets import p5, p6, p7, p8, p9, p10
from function.function1 import divide_check, all_first_pairing

def create_cor(P_set, need_pair):
    result = []
    for perm in permutations(need_pair):
        cor = {p: v for p, v in zip(P_set, perm)}
        result.append(cor)
    return result

from math import prod


def assign_prime(P_set, cor, pairing, path):

    result = []

    last_path = path[-1]
    new_element = tuple(a + b for a, b in zip(last_path[0], last_path[1]))

    if len(path) % 30 == 0 and all(cor[p] > 1 for p in P_set):
        N_P = prod(cor[p] for p in P_set)
        new_element = tuple(
            x if x % N_P == 0 else x % N_P
            for x in new_element
        )

    used_letters = {letter for letters in pairing.values() for letter in letters}
    P_set_rest = [letter for letter in P_set if letter not in used_letters]

    if not P_set_rest:
        return []

    for i in range(1, len(P_set_rest) + 1):
        new_pairing = pairing.copy()
        new_pairing[new_element] = P_set_rest[:i]

        new_path1 = path + [(last_path[0], new_element)]
        new_path2 = path + [(new_element, last_path[1])]

        result.append((cor, new_pairing, new_path1, True))
        result.append((cor, new_pairing, new_path2, True))

    return result



def create_new_path(P_set, cor, pairing, path):
    div, res1 = divide_check(P_set, cor, pairing, path)
    if div >= 1:
        return res1
    else:
        res2 = assign_prime(P_set, cor, pairing, path)
        return res2

    

def dfs_explore(P_set, cor, pairing, path, limit):
    
    results = []
    leaf_count = 0

    best_depth = 0
    best_cor = None
    best_pairing = None
    best_path = None
    hit_limit = False

    init_vals_set = set(cor.values())
    stack = [(cor, pairing, path, 1, init_vals_set)]

    while stack:
        cor_cur, pairing_cur, path_cur, depth, cur_vals_set = stack.pop()

        if depth > limit:
            if not hit_limit:
                hit_limit = True
                best_cor = cor_cur
                best_pairing = pairing_cur
                best_path = path_cur
            continue

        next_states = create_new_path(P_set, cor_cur, pairing_cur, path_cur)

        any_child = False

        for cor_new, pairing_new, path_new, valid in next_states:
            if not valid:
                continue

            new_vals_set = set(cor_new.values())

            stack.append((cor_new, pairing_new, path_new, depth + 1, new_vals_set))
            any_child = True

        if not any_child:
            leaf_count += 1

            if not hit_limit:
                if depth > best_depth:
                    best_depth = depth
                    best_cor = cor_cur
                    best_pairing = pairing_cur
                    best_path = path_cur

    flag = 1 if hit_limit else 0

    return results, leaf_count, best_cor, best_pairing, best_path, flag


def tree_all_dfs(P_set, need_pair, limit, print_path=True):

    pairing_set = all_first_pairing(P_set)

    first_cor_sets = create_cor(P_set, need_pair)

    best_global_cor = None
    best_global_pairing = None
    best_global_path = None
    best_global_len = 0

    init_idx = 0

    for pairing0 in pairing_set:
        for cor0 in first_cor_sets:
            init_idx += 1
            path0 = [((1, 0), (0, 1))]

            _, leaf_count, best_cor_i, best_pairing_i, best_path_i, flag_i = dfs_explore(
                P_set,
                cor0,
                pairing0,
                path0,
                limit,
            )

            if flag_i == 1:
                if print_path and best_path_i is not None:
                    print(f"==== hit limit at initial pattern {init_idx} ====")
                    print("cor   :", best_cor_i)
                    print("pair  :", best_pairing_i)
                    print("path  :", best_path_i)

                return best_cor_i, best_pairing_i, best_path_i, 1

            if best_path_i is not None:
                cur_len = len(best_path_i)
                if cur_len > best_global_len:
                    best_global_len = cur_len
                    best_global_cor = best_cor_i
                    best_global_pairing = best_pairing_i
                    best_global_path = best_path_i

    if print_path and best_global_path is not None:
        print("==== longest path without hitting limit ====")
        print("length:", best_global_len)
        print("cor   :", best_global_cor)
        print("pair  :", best_global_pairing)
        print("path  :", best_global_path)

    return best_global_cor, best_global_pairing, best_global_path, 0
