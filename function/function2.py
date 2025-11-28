import math
from function.function1 import tree_special
from function.primitive_sets import p5, p6, p7, p8, p9, p10
import math

def lcm(x, y):
    return (x * y) // math.gcd(x, y)

def P_div(N, P_set):
    return [p for p in P_set if N % p == 0]

def generate_path(a0, b0, P_set, max_depth=1000):
    N = math.prod(P_set)
    stack = [(a0, b0, 0, [])]

    while stack:
        a, b, depth, current_path = stack.pop()
        new_path = current_path + [(a, b)]

        if depth == max_depth:
            div_path = [(x, P_div(x, P_set), y, P_div(y, P_set)) for x, y in new_path]

            if div_path and (not div_path[-1][1] or not div_path[-1][3]):
                new_path = new_path[:-1]
                div_path = div_path[:-1]

            return new_path, div_path

        if P_div(a, P_set) and P_div(b, P_set):
            a_new = (a + b) % N
            b_new = (a + b) % N
            stack.append((a, a_new, depth + 1, new_path))
            stack.append((b_new, b, depth + 1, new_path))

    return None, None

def detect_tail_cycle(path):
    seen = {}
    div_pairs = [(tuple(x[1]), tuple(x[3])) for x in path]

    for i, key in enumerate(div_pairs):
        if key in seen:
            j = seen[key]
            segment_len = i - j
            segment_old = div_pairs[j:j + segment_len]
            segment_new = div_pairs[i:i + segment_len]
            if segment_old == segment_new:
                return path[i:i + segment_len], segment_len
        else:
            seen[key] = i

    return None, 0

def primes_from_cor(cor):
    P_set = sorted(set(cor.values()))
    N = math.prod(P_set)
    return P_set, N

def constraints_from_pairing(cor, pairing):
    cons = []
    for (i, j), labels in pairing.items():
        labels_unique = set(labels)
        for lbl in labels_unique:
            p = cor[lbl]
            cons.append((i, j, p))
    return cons

def extract_axis_mods(cor, pairing):
    mx = 1
    my = 1
    for (i, j), labels in pairing.items():
        if (i, j) == (1, 0):
            for lbl in set(labels):
                mx = lcm(mx, cor[lbl])
        elif (i, j) == (0, 1):
            for lbl in set(labels):
                my = lcm(my, cor[lbl])
    return mx, my

def satisfies_all_constraints(x, y, cons):
    for (i, j, p) in cons:
        if (i * x + j * y) % p != 0:
            return False
    return True

def candidate_pairs(rep):
    cor, pairing = rep
    P_set, N = primes_from_cor(cor)
    cons = constraints_from_pairing(cor, pairing)

    mx, my = extract_axis_mods(cor, pairing)
    if mx == 0: mx = 1
    if my == 0: my = 1
    for x in range(mx, N, mx):
        for y in range(max(x + 1, my), N, my):
            if not satisfies_all_constraints(x, y, cons):
                continue
            yield x, y, P_set, N

def is_infinite_via_rep(rep, max_depth=1000):
    cor, pairing = rep
    P_set, N = primes_from_cor(cor)

    for a, b, _Pset_unused, _N_unused in candidate_pairs(rep):
        if math.gcd(math.gcd(a, b), N) != 1:
            continue

        path_mod, path_div_mod = generate_path(a, b, P_set, max_depth=max_depth)
        if path_div_mod is None:
            continue

        cycle_part, cycle_len = detect_tail_cycle(path_div_mod)
        if cycle_part:
            return True, (a, b)

    return False, None

def check_loop(need_pair, limit, try_depth=1000):
    # すべての既知 primitive sets を結合
    primitive_sets = p5() + p6() + p7() + p8() + p9() + p10()

    # ==== 追加処理：need_pair が primitive set の真の上位集合なら中止 ====
    need_set = set(need_pair)

    for P in primitive_sets:
        P_set = set(P)
        if P_set.issubset(need_set) and need_set != P_set:
            return (
                f"{need_pair} contains primitive set {sorted(P)}"
            )

    # ==== ここから通常の処理 ====
    exceed_limit, rep, max_depth = tree_special(
        need_pair, limit, print_steps=None, print_path=False
    )

    P_str = "{" + ", ".join(map(str, need_pair)) + "}"

    if not exceed_limit:
        return f"P = {P_str} is of finite type, L(P) = {max_depth}"

    if rep is None:
        return f"P = {P_str}: inconclusive (exceed_limit=True but no rep)."

    infinite_detected, pair = is_infinite_via_rep(rep, max_depth=try_depth)
    if infinite_detected:
        a, b = pair
        return f"P = {P_str} is a primitive set, initial pair ({a}, {b})."
    else:
        return f"P = {P_str}: inconclusive (no cycle detected up to depth {try_depth})."

