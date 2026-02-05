from math import prod, lcm
from itertools import permutations
from function.primitive_sets import p5, p6, p7, p8, p9, p10
from function.function1 import create_cor, divide_check, all_first_pairing, prime_factor, check_unique_in_pair

def assign_prime(P_set, cor, pairing, path, need_pair):
    result = []
    last_path = path[-1]
    new_element = tuple(a + b for a, b in zip(last_path[0], last_path[1]))

    if len(path) % 30 == 0 and all(cor[p] > 1 for p in P_set):
        N_P = prod(cor[p] for p in P_set)
        new_element = tuple(x if x % N_P == 0 else x % N_P for x in new_element)

    unique_values = [v for v in set(cor.values()) if v > 1]
    used_letters = set(letter for letters in pairing.values() for letter in letters)
    P_set_rest = [letter for letter in P_set if letter not in used_letters]

    # need_pair を「許可する素数集合」に正規化
    allowed_primes = None
    if need_pair:
        # need_pair = [[...]] or need_pair = [...]
        src = need_pair[0] if isinstance(need_pair[0], (list, tuple, set)) else need_pair
        allowed_primes = set(src)

    # allowed_primes があるなら「割り切れるか判定」だけで候補を作る
    def cand_from_allowed(x):
        x = abs(int(x))
        if x == 0:
            return []  # 0 は全素数で割れるが候補爆発するので、ここは状況次第（必要なら調整）
        return [p for p in allowed_primes if p > 1 and x % p == 0 and p not in unique_values]

    for i in range(len(P_set_rest) + 1):
        if i == 0:
            for num_tuple, keys in pairing.items():
                ordered_keys = sorted(keys)
                key_to_assign = next((k for k in ordered_keys if cor.get(k, 1) == 1), None)
                if key_to_assign is None:
                    continue

                if num_tuple[0] == 0:
                    target = new_element[0]
                    if allowed_primes is not None:
                        cand_primes = cand_from_allowed(target)
                    else:
                        cand_primes = prime_factor(target)

                elif num_tuple[1] == 0:
                    target = new_element[1]
                    if allowed_primes is not None:
                        cand_primes = cand_from_allowed(target)
                    else:
                        cand_primes = prime_factor(target)

                else:
                    l = lcm(num_tuple[0], new_element[0])
                    L = (l * num_tuple[1] // num_tuple[0]) - (l * new_element[1] // new_element[0])
                    target = L
                    if allowed_primes is not None:
                        cand_primes = cand_from_allowed(target)
                    else:
                        cand_primes = prime_factor(abs(target))

                # allowed_primes が無い場合でも unique_values は落とす
                if allowed_primes is None:
                    cand_primes = [p for p in cand_primes if p not in unique_values]

                for prime in cand_primes:
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



def create_new_path(P_set, cor, pairing, path, need_pair):
    div, res1 = divide_check(P_set, cor, pairing, path)
    if div >= 1:
        return res1
    else:
        res2 = assign_prime(P_set, cor, pairing, path, need_pair)
        return res2


def dfs_explore(P_set, cor, pairing, path,
                infinite_pair, remove_pair, need_pair, limit):

    results = []
    leaf_count = 0

    # --- (A) 有限探索での最深葉（旧版の best_* 相当：hit_limit が起きる前だけ更新）
    best_leaf_depth = 0
    best_leaf_cor = None
    best_leaf_pairing = None
    best_leaf_path = None

    # --- (B) limit を超えた瞬間の代表（旧版と同じ動きにするための代表）
    best_limit_cor = None
    best_limit_pairing = None
    best_limit_path = None

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
                #print("=== primitive_set candidate ===")
                #print("  vals      :", sorted(key))

            # ★ ここで探索を打ち切る（1個見つけたら終わり）
            return results, leaf_count, cor_cur, pairing_cur, path_cur, True

        # ★ ここは絶対に変えない（ユーザー要件）
        next_states = create_new_path(P_set, cor_cur, pairing_cur, path_cur, need_pair)

        any_child = False

        for cor_new, pairing_new, path_new, valid in next_states:
            if not valid:
                continue

            new_vals_set = set(cor_new.values())

            # ---- 新版で入れていた枝刈り（必要なら残す）
            if new_vals_set != cur_vals_set:
                if check_unique_in_pair(new_vals_set, infinite_pair, remove_pair):
                    continue

                if all(v > 1 for v in cor_new.values()):
                    if need_pair:
                        # need_pair は「許容する集合のリスト」という想定
                        if not any(set(sub).issubset(new_vals_set) for sub in need_pair):
                            continue

            stack.append((cor_new, pairing_new, path_new, depth + 1, new_vals_set))
            any_child = True

        if not any_child:
            leaf_count += 1

            # 旧版と同じ：hit_limit がまだ起きていない間だけ最深葉を更新
            if not hit_limit and depth > best_leaf_depth:
                best_leaf_depth = depth
                best_leaf_cor = cor_cur
                best_leaf_pairing = pairing_cur
                best_leaf_path = path_cur

            # if leaf_count % 10_000_000 == 0:
                # print(f"[leaf] reached {leaf_count:,} leaves")

    # 返す代表も旧版に合わせる：
    # - hit_limit True なら limit超え代表
    # - False なら最深葉
    if hit_limit:
        return results, leaf_count, best_limit_cor, best_limit_pairing, best_limit_path, True
    else:
        return results, leaf_count, best_leaf_cor, best_leaf_pairing, best_leaf_path, False


def tree_all_dfs(P_set, infinite_pair, remove_pair, need_pair, limit, print_path=True):

    pairing_set = all_first_pairing(P_set)
    first_cor = create_cor(P_set)

    # ★ first_pair は変えない（ユーザー指定）
    first_pair = [
        (first_cor, pairing_set[i], [((1, 0), (0, 1))])
        for i in range(len(pairing_set))
    ]

    best_global_cor = None
    best_global_pairing = None
    best_global_path = None
    best_global_len = 0

    init_idx = 0

    for cor0, pairing0, path0 in first_pair:
        init_idx += 1

        results, leaf_count, best_cor_i, best_pairing_i, best_path_i, hit_limit_i = dfs_explore(
            P_set, cor0, pairing0, path0,
            infinite_pair, remove_pair, need_pair, limit
        )

        if hit_limit_i:
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
