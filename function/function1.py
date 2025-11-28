import math as m
from math import prod
from function.primitive_sets import p5, p6, p7, p8, p9, p10
import signal
from function.primes import primes_list

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


# def dfs_explore(P_set, cor, pairing, path,
#                 infinite_pair, remove_pair, need_pair, limit):

#     results = []

#     # stack 要素: (cor, pairing, path, depth, cor_vals_set)
#     init_vals_set = set(cor.values())
#     stack = [(cor, pairing, path, 1, init_vals_set)]

#     while stack:
#         cor_cur, pairing_cur, path_cur, depth, cur_vals_set = stack.pop()

#         # --- 深さ制限チェック ---
#         if depth > limit:
#             # この signature を infinite_pair に登録
#             key = frozenset(cor_cur.values())
#             if key not in infinite_pair:
#                 infinite_pair.append(key)

#                 # ★ ここで逐次 print する
#                 print("=== hit limit / infinite_pair candidate ===")
#                 print("  vals      :", sorted(key))
#                 # print("  depth     :", depth)
#                 # print("  path_len  :", len(path_cur))
#                 # 必要なら cor や pairing も出せる:
#                 # print("  cor       :", cor_cur)
#                 # print("  pairing  :", pairing_cur)
#             continue


#         # 次の状態を生成
#         next_states = create_new_path(P_set, cor_cur, pairing_cur, path_cur)

#         any_child = False  # 有効な子が一つでもあったかどうか

#         for cor_new, pairing_new, path_new, valid in next_states:
#             if not valid:
#                 continue

#             # cor の値集合（重複なし）
#             new_vals_set = set(cor_new.values())

#             # ここがポイント：
#             # cor の値集合が親と同じなら、signature は変わっていないので
#             # infinite_pair / remove_pair / need_pair のチェックはスキップしてよい。
#             if new_vals_set != cur_vals_set:
#                 # ---- infinite_pair / remove_pair による除外判定 ----
#                 if check_unique_in_pair(new_vals_set, infinite_pair, remove_pair):
#                     continue

#                 # ---- need_pair チェック ----
#                 # 「cor の全要素が 1 より大きくなったとき」にのみ行う
#                 if all(v > 1 for v in cor_new.values()):
#                     if need_pair:
#                         # need_pair のうちいずれかの subset が含まれていなければ除外
#                         if not any(sub.issubset(new_vals_set) for sub in need_pair):
#                             continue

#             # ここまで来たらこの子ノードは有効 → 次の深さへ積む
#             stack.append((cor_new, pairing_new, path_new, depth + 1, new_vals_set))
#             any_child = True

#         # # 有効な子が一つもなかった場合（葉）
#         # if not any_child:
#         #     results.append((cor_cur, pairing_cur, path_cur))

#     return results

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


# def tree_all_dfs(P_set, infinite_pair, remove_pair, need_pair, limit,
#                  print_path=True):
#     result_list = []
#     representatives = {}

#     pairing_set = all_first_pairing(P_set)
#     first_cor = create_cor(P_set)
#     first_pair = [(first_cor, pairing_set[i], [((1, 0), (0, 1))]) for i in range(len(pairing_set))]

#     for m, (cor, pairing, path) in enumerate(first_pair):
#         print(f"==== Exploring pair {m + 1} ====")
#         results = dfs_explore(P_set, cor, pairing, path,
#                               infinite_pair, remove_pair, need_pair, limit)

#         for cor_final, pairing_final, _ in results:
#             vals = sorted(set(cor_final.values()))
#             result_list.append(vals)
#             key = tuple(vals)
#             if key not in representatives:
#                 representatives[key] = (cor_final, pairing_final, path)

#     # deduplicate results
#     B = list(map(list, {tuple(x) for x in result_list}))
#     count_B = len(B)
#     rep_list = [(representatives[tuple(vals)][0], representatives[tuple(vals)][1])
#                 for vals in B if tuple(vals) in representatives]

#     if print_path:
#         print("\n=== Representative results ===")
#         for vals in B:
#             key = tuple(vals)
#             if key in representatives:
#                 cor_rep, pairing_rep, path_rep = representatives[key]
#                 print(f"- cor values: {vals}")
#                 print(f"  cor: {cor_rep}")
#                 print(f"  pairing: {pairing_rep}")
#                 print(f"  depth: {len(path_rep)}")

#     return B, count_B, rep_list, infinite_pair

def tree_all_dfs(P_set, infinite_pair, remove_pair, need_pair, limit,
                 print_path=True):
    # B や代表結果を使わないのでコメントアウト
    # result_list = []
    # representatives = {}

    pairing_set = all_first_pairing(P_set)
    first_cor = create_cor(P_set)
    first_pair = [(first_cor, pairing_set[i], [((1, 0), (0, 1))]) for i in range(len(pairing_set))]

    for m, (cor, pairing, path) in enumerate(first_pair):
        print(f"==== Exploring pair {m + 1} ====")
        # dfs_explore は infinite_pair を更新するためだけに呼ぶ
        results = dfs_explore(P_set, cor, pairing, path,
                              infinite_pair, remove_pair, need_pair, limit)

        # B を使わないなら、results から何かを集計する処理も不要
        # for cor_final, pairing_final, _ in results:
        #     vals = sorted(set(cor_final.values()))
        #     result_list.append(vals)
        #     key = tuple(vals)
        #     if key not in representatives:
        #         representatives[key] = (cor_final, pairing_final, path)

    # # deduplicate results
    # B = list(map(list, {tuple(x) for x in result_list}))
    # count_B = len(B)
    # rep_list = [(representatives[tuple(vals)][0], representatives[tuple(vals)][1])
    #             for vals in B if tuple(vals) in representatives]

    # if print_path:
    #     print("\n=== Representative results ===")
    #     for vals in B:
    #         key = tuple(vals)
    #         if key in representatives:
    #             cor_rep, pairing_rep, path_rep = representatives[key]
    #             print(f"- cor values: {vals}")
    #             print(f"  cor: {cor_rep}")
    #             print(f"  pairing: {pairing_rep}")
    #             print(f"  depth: {len(path_rep)}")

    # 互換性を保ちたいなら、空のダミーを返しておく
    B = []
    count_B = 0
    rep_list = []

    return B, count_B, rep_list, infinite_pair


class TimeoutException(Exception):
    pass

def _timeout_handler(signum, frame):
    raise TimeoutException

# def tree_special(need_pair, limit, print_steps=None, print_path=True):
#     """
#     input:
#         need_pair: list of primes (single set), e.g., [2, 3, 5]
#         limit: int, maximum depth (layers) to explore
#         print_steps: int or None. If int k, print progress every k layers.
#         print_path: If true, print a representative when limit is exceeded.

#     output:
#         If limit is exceeded:
#             (True, (cor_rep, pairing_rep), None)
#         Else (limit not exceeded):
#             (False, None, max_depth)

#     Notes:
#         - P_set is auto-generated with the same size as need_pair (labels 'a','b',...).
#         - During exploration, any cor value not in {1} ∪ set(need_pair) will be pruned.
#     """
#     # --- timeout（600 sec） ---
#     signal.signal(signal.SIGALRM, _timeout_handler)
#     signal.alarm(600)

#     try:
#         # --- helpers / assumptions ---
#         # Uses: all_first_pairing(P_set), create_cor(P_set), create_new_path(P_set, cor, pairing, path)

#         # Generate P_set with the same cardinality as need_pair
#         r = len(need_pair)
#         P_set = [chr(97 + i) for i in range(r)]  # ['a','b','c',...]
#         allowed = set(need_pair)

#         # Initial frontier
#         pairing_set = all_first_pairing(P_set)
#         first_cor = create_cor(P_set)
#         first_pair = [(first_cor, pairing_set[i], [((1, 0), (0, 1))]) for i in range(len(pairing_set))]
#         # print(first_pair)

#         exceeded = False
#         representative = None  # (cor_rep, pairing_rep)
#         max_depth_reached = 1  # path starts with one edge in our seed

#         for m in range(len(first_pair)):
#             # print(f"==== Exploring pair {m + 1} ====")
#             steps = 2
#             set_rest = [first_pair[m]]

#             while len(set_rest) >= 1 and steps <= limit:
#                 # if isinstance(print_steps, int) and print_steps > 0 and (steps % print_steps == 0):
#                     # print(f"Finished exploring layer {steps} (current candidates: {len(set_rest)})")

#                 new_set_rest = []
#                 for i in range(len(set_rest)):
#                     cor_i, pairing_i, path_i = set_rest[i]
#                     results = create_new_path(P_set, cor_i, pairing_i, path_i)

#                     for cor_next, pairing_next, path_next, ok_flag in results:
#                         if not ok_flag:
#                             continue

#                         # --- pruning: only 1 or primes from need_pair are allowed in cor ---
#                         vals = list(cor_next.values())
#                         if any((v != 1 and v not in allowed) for v in vals):
#                             continue

#                         new_set_rest.append((cor_next, pairing_next, path_next))

#                 set_rest = new_set_rest
#                 max_depth_reached = max(max_depth_reached, steps)
#                 steps += 1

#             # limit exceeded?
#             if steps > limit and len(set_rest) > 0:
#                 exceeded = True
#                 # pick one representative
#                 cor_rep, pairing_rep, path_rep = set_rest[0]
#                 representative = (cor_rep, pairing_rep)

#                 if print_path:
#                     print("\n === Representative (limit exceeded) ===")
#                     print(f"cor: {cor_rep}")
#                     print(f"pairing: {pairing_rep}")
#                     # print(f"last edge: {path_rep[-1] if path_rep else None}")

#                 # Return immediately with a representative when exceeded
#                 return True, representative, None

#         # Not exceeded anywhere
#         return False, None, max_depth_reached

#         signal.alarm(0)  # タイマー解除
#         return exceed_limit, rep, max_depth
    
#     except TimeoutException:
#         print(f"P = {need_pair} may not be primitive, forced termination after 10 minutes.")
#         signal.alarm(0)
#         # タイムアウトを示す特別フラグ
#         return "timeout", None, None

def dfs_explore2(P_set, cor, pairing, path,
                infinite_pair, remove_pair, need_pair, limit):

    results = []
    leaf_count = 0
    hit_limit = False
    rep_at_limit = None
    max_depth = 1

    # ★★ ここで need_pair を正規化 ★★
    # need_pair が [2,3,5] みたいな「int のリスト」なら [{2,3,5}] にする
    if need_pair:
        # すべて int なら「単一集合」とみなす
        if all(isinstance(x, int) for x in need_pair):
            need_pair_subsets = [set(need_pair)]
        else:
            # すでに [set(...), set(...)] などの形を想定
            need_pair_subsets = [set(sub) for sub in need_pair]
    else:
        need_pair_subsets = []

    # stack 要素: (cor, pairing, path, depth, cor_vals_set)
    init_vals_set = set(cor.values())
    stack = [(cor, pairing, path, 1, init_vals_set)]

    while stack:
        cor_cur, pairing_cur, path_cur, depth, cur_vals_set = stack.pop()

        if depth > max_depth:
            max_depth = depth

        # --- 深さ制限チェック ---
        if depth > limit:
            if not hit_limit:
                hit_limit = True
                rep_at_limit = (cor_cur, pairing_cur)

            key = frozenset(cor_cur.values())

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
                    # ★ ここで need_pair_subsets を使う ★
                    if need_pair_subsets:
                        if not any(sub.issubset(new_vals_set) for sub in need_pair_subsets):
                            continue

            stack.append((cor_new, pairing_new, path_new, depth + 1, new_vals_set))
            any_child = True

    return results, leaf_count, hit_limit, rep_at_limit, max_depth


# ???????
def tree_special(need_pair, limit, print_steps=None, print_path=True):

    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(600)

    try:
        r = len(need_pair)
        P_set = [chr(97 + i) for i in range(r)]

        infinite_pair = p5() + p6() + p7() + p8() + p9() + p10()
        remove_pair = [[p] for p in primes_list() if p not in need_pair]

        pairing_set = all_first_pairing(P_set)
        first_cor = create_cor(P_set)

        first_pair = [
            (first_cor, pairing_set[i], [((1, 0), (0, 1))])
            for i in range(len(pairing_set))
        ]

        max_depth_reached = 1

        # ====== 重要：limit 超えたら即 return ======
        for m, (cor, pairing, path) in enumerate(first_pair):

            _, leaf_count, hit_limit, rep_at_limit, max_depth = dfs_explore2(
                P_set, cor, pairing, path,
                infinite_pair, remove_pair, need_pair, limit
            )

            # 最大深さ更新
            max_depth_reached = max(max_depth_reached, max_depth)

            # ---- limit 超えた瞬間に即 return ----
            if hit_limit and rep_at_limit is not None:
                cor_rep, pairing_rep = rep_at_limit

                if print_path:
                    print("\n === Representative (limit exceeded) ===")
                    print(f"cor: {cor_rep}")
                    print(f"pairing: {pairing_rep}")

                signal.alarm(0)
                return True, (cor_rep, pairing_rep), None

        # ---- 1つも limit 超えがなければ有限型 ----
        signal.alarm(0)
        return False, None, max_depth_reached

    except TimeoutException:
        print(f"P = {need_pair} may not be primitive, forced termination after 10 minutes.")
        signal.alarm(0)
        return "timeout", None, None
