import math as m
from math import prod
from function.primitive_sets import p5, p6, p7, p8, p9, p10
import time


def generate_P_set(n):
    return [chr(ord('a') + i) for i in range(n)]


def lcm(x, y):
    return (x * y) // m.gcd(x, y)


def partition(N):
    result = [(x, y) for x in range(1, N) for y in range(1, x + 1) if x + y <= N]
    return result


def create_cor(P_set):
    return {p: 1 for p in P_set}


def prime_factor(N):
    factors = set()
    d = 2
    while d * d <= N:
        if N % d == 0:
            factors.add(d)
            while N % d == 0:
                N //= d
        d += 1
    if N > 1:
        factors.add(N)
    return sorted(factors)


def all_first_pairing(P_set):
    n = len(P_set)
    prime_num_pair = partition(n)
    result = []

    for i in range(len(prime_num_pair)):
        x,y = prime_num_pair[i]
        A = [P_set[j] for j in range(x)]
        B = [P_set[j] for j in range(x,x+y)]
        result.append({(1,0) : A,(0,1) : B})

    return result


def divide_check(P_set, cor, pairing, path):
    result = []
    last_path = path[-1]
    new_element = tuple(a + b for a, b in zip(last_path[0], last_path[1]))
    if len(path) % 30 == 0 and all(cor[p] > 1 for p in P_set):
        N_P = prod(cor[p] for p in P_set)
        new_element = tuple(
            x if x % N_P == 0 else x % N_P
            for x in new_element
        )
    
    divide_check = 0

    for num_tuple, keys in pairing.items():
        for key in keys:
            if cor.get(key) >= 2:
                if num_tuple[0] == 0:
                    if new_element[0] % cor.get(key) == 0:
                        divide_check += 1
                elif num_tuple[1] == 0:
                    if new_element[1] % cor.get(key) == 0:
                        divide_check += 1
                else:
                    l = lcm(num_tuple[0], new_element[0])
                    lhs = l * num_tuple[1] // num_tuple[0]
                    rhs = l * new_element[1] // new_element[0]
                    L = lhs - rhs
                    if L % cor.get(key) == 0:
                        divide_check += 1
    if divide_check >= 1:
        new_path1 = path + [(last_path[0], new_element)]
        new_path2 = path + [(new_element, last_path[1])]
        result.append((cor, pairing, new_path1, True))
        result.append((cor, pairing, new_path2, True))

    return divide_check, result


def assign_prime(P_set, cor, pairing, path):
    result = []
    last_path = path[-1]
    new_element = tuple(a + b for a, b in zip(last_path[0], last_path[1]))

    if len(path) % 30 == 0 and all(cor[p] > 1 for p in P_set):
        N_P = prod(cor[p] for p in P_set)
        new_element = tuple(x if x % N_P == 0 else x % N_P for x in new_element)

    unique_values = [v for v in set(cor.values()) if v > 1]
    used_letters = set(letter for letters in pairing.values() for letter in letters)
    P_set_rest = [letter for letter in P_set if letter not in used_letters]

    for i in range(len(P_set_rest) + 1):
        if i == 0:
            for num_tuple, keys in pairing.items():
                ordered_keys = sorted(keys)
                key_to_assign = next((k for k in ordered_keys if cor.get(k, 1) == 1), None)
                if key_to_assign is None:
                    continue

                if num_tuple[0] == 0:
                    cand_primes = prime_factor(new_element[0])
                elif num_tuple[1] == 0:
                    cand_primes = prime_factor(new_element[1])
                else:
                    l = lcm(num_tuple[0], new_element[0])
                    L = (l * num_tuple[1] // num_tuple[0]) - (l * new_element[1] // new_element[0])
                    cand_primes = prime_factor(abs(L))

                for prime in cand_primes:
                    if prime in unique_values:
                        continue
                    new_cor = cor.copy()
                    new_cor[key_to_assign] = prime

                    new_path1 = path + [(last_path[0], new_element)]
                    new_path2 = path + [(new_element, last_path[1])]
                    result.append((new_cor, pairing, new_path1, True))
                    result.append((new_cor, pairing, new_path2, True))

        else:
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


def check_unique_in_pair(unique_set, infinite_pair, remove_pair):
    for container in (infinite_pair, remove_pair):
        for sig in container:
            if isinstance(sig, (set, frozenset)):
                sig_set = sig
            else:
                sig_set = set(sig)

            if sig_set.issubset(unique_set):
                return True

    return False


def dfs_explore(P_set, cor, pairing, path,
                infinite_pair, remove_pair, need_pair, limit):

    results = []
    leaf_count = 0

    best_leaf_depth = 0
    best_leaf_cor = None
    best_leaf_pairing = None
    best_leaf_path = None

    hit_limit = False

    init_vals_set = set(cor.values())
    stack = [(cor, pairing, path, 1, init_vals_set)]

    while stack:
        cor_cur, pairing_cur, path_cur, depth, cur_vals_set = stack.pop()

        if depth > limit:
            hit_limit = True

            key = frozenset(cor_cur.values())
            if key not in infinite_pair:
                infinite_pair.append(key)

                print("=== primitive_set candidate ===")
                print("  vals      :", sorted(key))
            continue

        next_states = create_new_path(P_set, cor_cur, pairing_cur, path_cur)

        any_child = False

        for cor_new, pairing_new, path_new, valid in next_states:
            if not valid:
                continue

            new_vals_set = set(cor_new.values())

            if new_vals_set != cur_vals_set:
                if check_unique_in_pair(new_vals_set, infinite_pair, remove_pair):
                    continue

                if all(v > 1 for v in cor_new.values()):
                    if need_pair:
                        if not any(set(sub).issubset(new_vals_set) for sub in need_pair):
                            continue

            stack.append((cor_new, pairing_new, path_new, depth + 1, new_vals_set))
            any_child = True

        if not any_child:
            leaf_count += 1

            if not hit_limit:
                if depth > best_leaf_depth:
                    best_leaf_depth = depth
                    best_leaf_cor = cor_cur
                    best_leaf_pairing = pairing_cur
                    best_leaf_path = path_cur

            if leaf_count % 10_000_000 == 0:
                print(f"[leaf] reached {leaf_count:,} leaves")

    return results, leaf_count, best_leaf_cor, best_leaf_pairing, best_leaf_path, hit_limit




def tree_all_dfs(P_set, infinite_pair, remove_pair, need_pair, limit,
                 print_path=True):

    pairing_set = all_first_pairing(P_set)
    first_cor = create_cor(P_set)
    first_pair = [
        (first_cor, pairing_set[i], [((1, 0), (0, 1))])
        for i in range(len(pairing_set))
    ]

    total_leaf_count = 0

    best_global_depth = 0
    best_global_cor = None
    best_global_pairing = None
    best_global_path = None

    for m, (cor, pairing, path) in enumerate(first_pair):
        print(f"==== Exploring pair {m + 1} ====")

        (results,
         leaf_count,
         best_cor_i,
         best_pairing_i,
         best_path_i,
         hit_limit_i) = dfs_explore(
            P_set, cor, pairing, path,
            infinite_pair, remove_pair, need_pair, limit
        )

        total_leaf_count += leaf_count

        if hit_limit_i:
            continue

        if best_path_i is not None:
            depth_i = len(best_path_i)
            if depth_i > best_global_depth:
                best_global_depth = depth_i
                best_global_cor = best_cor_i
                best_global_pairing = best_pairing_i
                best_global_path = best_path_i

    if print_path and best_global_path is not None:
        print("==== deepest finite leaf over all dfs (no primitive set) ====")
        print("depth :", best_global_depth)
        print("cor   :", best_global_cor)
        print("pair  :", best_global_pairing)
        print("path  :", best_global_path)

    return infinite_pair, total_leaf_count, best_global_cor, best_global_pairing, best_global_path


def run_tree_search(
    P_num: int,
    limit: int,
    infinite_pair=None,
    remove_pair=None,
    need_pair=None,
    print_path: bool = False,
    verbose: bool = True,
):
    if infinite_pair is None:
        infinite_pair = []
    if remove_pair is None:
        remove_pair = []
    if need_pair is None:
        need_pair = []

    P_set = generate_P_set(P_num)

    known_inf = [tuple(sorted(sig)) for sig in infinite_pair]

    t0 = time.perf_counter()

    infinite_pair, total_leaf_count, best_cor, best_pairing, best_path = tree_all_dfs(
        P_set=P_set,
        infinite_pair=infinite_pair,
        remove_pair=remove_pair,
        need_pair=need_pair,
        limit=limit,
        print_path=print_path,
    )

    t1 = time.perf_counter()
    elapsed = t1 - t0

    newly_found_infinite_sigs = []

    if infinite_pair:
        all_sigs = {tuple(sorted(sig)) for sig in infinite_pair}
        for sig in sorted(all_sigs):
            if sig not in known_inf:
                newly_found_infinite_sigs.append(list(sig))

    if verbose:
        print("\n===== Summary =====")
        print(f"P_num          = {P_num}")
        print(f"P_set          = {P_set}")
        print(f"limit          = {limit}")
        print(f"total leaf cnt = {total_leaf_count}")
        print(f"elapsed        = {elapsed:.3f} sec")

        if newly_found_infinite_sigs:
            print("\n===== Newly found infinite-type signatures (hit limit) =====")
            for sig in newly_found_infinite_sigs:
                print(sig)

        if best_path is not None:
            best_cor_values = sorted(best_cor.values())
            print("\n===== Deepest finite leaf (did not hit limit) =====")
            print(f"set  = {best_cor_values}")
            print(f"depth  = {len(best_path)}")
            print(f"cor    = {best_cor}")
            print(f"pair   = {best_pairing}")
            # print(f"path   = {best_path}")

    return {
        "P_num": P_num,
        "P_set": P_set,
        "limit": limit,
        "total_leaf_count": total_leaf_count,
        "elapsed": elapsed,
        "infinite_pair": infinite_pair,
        "known_inf": known_inf,
        "newly_found_infinite_sigs": newly_found_infinite_sigs,
        "best_cor": best_cor,
        "best_cor_values": best_cor_values,   # ★ これ追加
        "best_pairing": best_pairing,
        "best_path": best_path,
    }