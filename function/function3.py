from function.function2 import tree_all_dfs
from function.primitive_sets import p5, p6, p7, p8, p9, p10
import math

def lcm(x, y):
    return (x * y) // math.gcd(x, y)

def P_div(N, P_set):
    return [p for p in P_set if N % p == 0]

def format_state(a, b, P_set):

    N = math.prod(P_set)
    g1 = math.gcd(a, N)
    g2 = math.gcd(b, N)

    def g_or_none(g):
        return None if g == 1 else g

    g1_disp = g_or_none(g1)
    g2_disp = g_or_none(g2)

    return f"({a},{b})[{(g1_disp, g2_disp)}]"

def lr_sequence(numeric_path, P_set):

    N = math.prod(P_set)
    steps = []

    for (a, b), (c, d) in zip(numeric_path, numeric_path[1:]):
        # L 判定: (a,b) -> (a, a+b)
        if (c - a) % N == 0 and (d - (a + b)) % N == 0:
            steps.append('L')
        # R 判定: (a,b) -> (a+b, b)
        elif ((c - (a + b)) % N == 0) and (d - b) % N == 0:
            steps.append('R')
        else:
            steps.append('?')  # 想定外の遷移
    return ''.join(steps)


def detect_tail_cycle(path_div):

    seen = {}
    div_pairs = [(tuple(x[1]), tuple(x[3])) for x in path_div]

    for i, key in enumerate(div_pairs):
        if key in seen:
            j = seen[key]         # key の最初の出現位置
            segment_len = i - j   # 周期候補の長さ

            if segment_len <= 0:
                continue

            # j からの1ブロックと i からの1ブロックが一致するか
            segment_old = div_pairs[j:j + segment_len]
            segment_new = div_pairs[i:i + segment_len]

            if segment_old == segment_new:
                # ★ 2回目側（i〜）を cycle 本体とみなす ★
                start_idx = i
                end_idx = i + segment_len - 1
                return start_idx, end_idx, segment_len
        else:
            seen[key] = i

    return None, None, 0


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

def is_infinite_from_rep_and_path(rep, path):
    cor, pairing = rep
    P_set = sorted(set(cor.values()))

    numeric_path = lift_path_to_numeric(rep, path)
    if not numeric_path:
        return False, None, None

    path_div = [
        (a, P_div(a, P_set), b, P_div(b, P_set))
        for (a, b) in numeric_path
    ]

    start_idx, end_idx, period = detect_tail_cycle(path_div)
    if start_idx is None:
        return False, None, None

    cs_idx = start_idx
    ce_idx = end_idx+1

    initial     = numeric_path[0]
    cycle_start = numeric_path[cs_idx]
    cycle_end   = numeric_path[ce_idx]

    # period は「検出したパターンの周期候補（ノード数）」として残しておく
    return True, initial, (cycle_start, cycle_end, period, cs_idx, ce_idx)



def solve_axes_by_crt(rep):
    cor, pairing = rep

    P_set = sorted(set(cor.values()))
    N = math.prod(P_set)

    for x, y, _Pset_unused, _N_unused in candidate_pairs(rep):

        if math.gcd(math.gcd(x, y), N) == 1:
            return x, y, N

    return None

def lift_path_to_numeric(rep, path):

    res = solve_axes_by_crt(rep)
    if res is None:
        return None
    x_axis, y_axis, N = res

    numeric_path = []
    for (v1, v2) in path:
        i1, j1 = v1
        i2, j2 = v2
        a = (i1 * x_axis + j1 * y_axis)
        b = (i2 * x_axis + j2 * y_axis)
        numeric_path.append((a, b))

    return numeric_path

def check_loop(need_pair, limit):

    primitive_sets = p5() + p6() + p7() + p8() + p9() + p10()
    need_set = set(need_pair)

    for P in primitive_sets:
        P_set = set(P)
        if P_set.issubset(need_set) and need_set != P_set:
            return f"{need_pair} contains primitive set {sorted(P)}"

    best_cor, best_pairing, best_path, flag = tree_all_dfs(
        P_set=need_pair,
        need_pair=need_pair,
        limit=limit,
        print_path=False,
    )

    P_str = "{" + ", ".join(map(str, need_pair)) + "}"

    if best_cor is not None:
        P_set = sorted(set(best_cor.values()))
    else:
        P_set = sorted(set(need_pair))

    # finite-type
    if flag == 0:
        if best_path is None or best_cor is None or best_pairing is None:
            return f"P = {P_str} is of finite type (no valid path up to limit {limit})."

        rep = (best_cor, best_pairing)
        numeric_path = lift_path_to_numeric(rep, best_path)

        if not numeric_path:
            return (
                f"P = {P_str} is of finite type, "
                f"but numeric lifting failed."
            )

        steps = lr_sequence(numeric_path, P_set)
        N = math.prod(P_set)

        a, b = numeric_path[-1]

        def gcd_pair(x, y):
            g1 = math.gcd(x, N)
            g2 = math.gcd(y, N)
            return g1, g2

        aL, bL = a, a + b
        g1L, g2L = gcd_pair(aL, bL)

        aR, bR = a + b, b
        g1R, g2R = gcd_pair(aR, bR)

        extended_end = None
        extended_steps = steps

        if g1L == 1 or g2L == 1:
            extended_end = (aL, bL)
            extended_steps = steps + 'L'
        elif g1R == 1 or g2R == 1:
            extended_end = (aR, bR)
            extended_steps = steps + 'R'

        if extended_end is not None:
            end_a, end_b = extended_end
        else:
            end_a, end_b = a, b

        init_a, init_b = numeric_path[0]

        initial_str = format_state(init_a, init_b, P_set)
        end_str     = format_state(end_a, end_b, P_set)

        return (
            f"P = {P_str} is of finite type, "
            f"initial : {initial_str} {extended_steps}  "
            f"end : {end_str}"
        )

    # primitive
    if best_cor is None or best_pairing is None or best_path is None:
        return f"P = {P_str}: inconclusive (hit limit but no representative/path)."

    rep = (best_cor, best_pairing)

    numeric_path = lift_path_to_numeric(rep, best_path)
    if not numeric_path:
        return (
            f"P = {P_str}: inconclusive "
            f"(numeric lifting failed on deepest path)."
        )

    steps = lr_sequence(numeric_path, P_set)

    infinite_detected, initial, cycle_info = is_infinite_from_rep_and_path(rep, best_path)

    if infinite_detected:
        cycle_start, cycle_end, period, cs_idx, ce_idx = cycle_info

        init_a, init_b = initial
        cs_a, cs_b     = cycle_start
        ce_a, ce_b     = cycle_end

        initial_str     = format_state(init_a, init_b, P_set)
        cycle_start_str = format_state(cs_a, cs_b, P_set)
        cycle_end_str   = format_state(ce_a, ce_b, P_set)

        steps_to_cs = steps[:cs_idx]

        steps_cycle = steps[cs_idx:ce_idx]
        cycle_len_display = len(steps_cycle)

        return (
            f"P = {P_str} is a primitive set, "
            f"initial : {initial_str} {steps_to_cs}  "
            f"cycle_start : {cycle_start_str} {steps_cycle}  "
            f"cycle_end : {cycle_end_str} "
            f"(cycle length = {cycle_len_display})"
        )

    else:
        return (
            f"P = {P_str}: inconclusive "
            f"(no cycle detected on the deepest path)."
        )
