from function.function1 import tree_all_dfs, generate_P_set
from function.primitive_sets import p5, p6, p7, p8

def main():
    # input----------------------
    P_num = 7
    limit = 90
    infinite_pair = p5() + p6() + p7()
    remove_pair = [[5]]
    need_pair = []
    #----------------------------
    P_set = generate_P_set(P_num)
    inf_pair = [tuple(sorted(sig)) for sig in infinite_pair]

    B, count, reps, infinite_pair = tree_all_dfs(
        P_set=P_set,
        infinite_pair=infinite_pair,
        remove_pair=remove_pair,
        need_pair=need_pair,
        limit=limit,
        print_path=False,
    )

    print("\n===== Summary =====")
    if infinite_pair:
        print("\n===== Infinite-type signatures (hit limit) =====")
        for sig in sorted({tuple(sorted(sig)) for sig in infinite_pair}):
            if sig not in inf_pair:
                print(list(sig))

if __name__ == "__main__":
    main()


