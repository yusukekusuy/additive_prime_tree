import math as m
from math import prod
from function.primitive_sets import p5, p6, p7, p8, p9, p10

def generate_P_set(n):
    return [chr(ord('a') + i) for i in range(n)]

def lcm(x, y):
    return (x * y) // m.gcd(x, y)

def partition(N):
    """
    input: Natural number
    output: the list of all pairs (x,y) with 1 <= y <= x <= N-1 and x+y <= N
    ------------------------------------
    Ex: partition(4)
    output: [(1,1), (2,1), (2,2), (3,1)]
    """
    result = [(x, y) for x in range(1, N) for y in range(1, x + 1) if x + y <= N]
    return result

def create_cor(P_set):
    return {p: 1 for p in P_set}

def prime_factor(N):
    """
    input: Natural number
    output: the list of prime factor of input
    """
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
    """
    input: A list of symbols of prime
    output: A list of all distinct divisibility patterns of the initial pair (a,b)), classified only by counts of primes dividing a and b
    ------------------------------------
    Ex: first_pairing(['a', 'b', 'c', 'd'])
    output: 
    [{(1, 0): ['a'], (0, 1): ['b']},
    {(1, 0): ['a', 'b'], (0, 1): ['c']},
    {(1, 0): ['a', 'b'], (0, 1): ['c', 'd']},
    {(1, 0): ['a', 'b', 'c'], (0, 1): ['d']}]
    ------------------------------------
    Explanation:
    (A,B) represents Aa+Bb where a,b are symbols.
    """
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
    """
    Explanation: Determine if the new element is divisible by its assigned prime.
    """
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
    """
    Explanation: Assign new prime.
    """
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
    """
    input: P_set: a list of symbols of prime, cor: correspondence between primes and the element of P_set, pairing: correspondence between Aa+Bb((A,B)) and elements of P_set, path: read the explanation below 
    output: [cor_new, pairing_new, paths_new, finish_check]
    ------------------------------------
    Ex of input: 
    P_set = ['a', 'b', 'c', 'd']
    cor = {'a': 1, 'b': 1, 'c': 1, 'd': 1}
    pairing = {(1, 0): ['a', 'b'], (0, 1): ['c']}
    path = [((1, 0), (0, 1))]
    ------------------------------------
    Explanation:
    ((A, B), (C, D)) represents (Aa+Bb, Ca+Db).
    path = [((1, 0), (0, 1)), ((1, 0), (1, 1)), ((2, 1), (1, 1))] represents (a,b) → (a,a+b) → (2a+b,a+b) where a,b are symbols.
    """
    div, res1 = divide_check(P_set, cor, pairing, path)
    if div >= 1:
        return res1
    else:
        res2 = assign_prime(P_set, cor, pairing, path)
        return res2

def check_unique_in_pair(unique_set, infinite_pair, remove_pair):
    """
    unique_set      : set[int]
    infinite_pair   : list or set of (list/tuple/set/frozenset[int])
    remove_pair     : 同上
    """
    for container in (infinite_pair, remove_pair):
        for sig in container:
            # sig が list/tuple なら set に変換、set/frozenset ならそのまま
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
    leaf_count = 0  # ★ 葉のカウント

    # stack 要素: (cor, pairing, path, depth, cor_vals_set)
    init_vals_set = set(cor.values())
    stack = [(cor, pairing, path, 1, init_vals_set)]

    while stack:
        cor_cur, pairing_cur, path_cur, depth, cur_vals_set = stack.pop()

        # --- 深さ制限チェック ---
        if depth > limit:
            key = frozenset(cor_cur.values())
            if key not in infinite_pair:
                infinite_pair.append(key)

                print("=== hit limit / infinite_pair candidate ===")
                print("  vals      :", sorted(key))
            continue

        # 次の状態を生成
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
                        if not any(sub.issubset(new_vals_set) for sub in need_pair):
                            continue

            stack.append((cor_new, pairing_new, path_new, depth + 1, new_vals_set))
            any_child = True

        # --- 葉（valid な子がない） ---
        if not any_child:
            leaf_count += 1

            # ★ 100万枚ごとに print
            if leaf_count % 10000000 == 0:
                print(f"[leaf] reached {leaf_count:,} leaves")

    return results, leaf_count

def tree_all_dfs(P_set, infinite_pair, remove_pair, need_pair, limit,
                 print_path=True):

    pairing_set = all_first_pairing(P_set)
    first_cor = create_cor(P_set)
    first_pair = [(first_cor, pairing_set[i], [((1, 0), (0, 1))]) for i in range(len(pairing_set))]

    for m, (cor, pairing, path) in enumerate(first_pair):
        print(f"==== Exploring pair {m + 1} ====")
        # dfs_explore は infinite_pair を更新するためだけに呼ぶ
        results = dfs_explore(P_set, cor, pairing, path,
                              infinite_pair, remove_pair, need_pair, limit)

    B = []
    count_B = 0
    rep_list = []

    return B, count_B, rep_list, infinite_pair