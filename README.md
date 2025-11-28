# Algorithmの説明

これは\url(arxiv)で用いているアルゴリズムである。
このアルゴリズムを用いることで素数全体の部分集合Pがfinite-typeかどうかを判定することが可能である。

いい感じの表を作る。ファイル名：説明　（ファイル名のところえを押したらそのファイルに飛べるようにしたい。）
function_tree.py：primitive setの候補を見つける関数を記載し得ている。
function_check_infinite.py：primitive setかどうかを判定する関数を関数を記載している。
primitive_sets.py：今まで見つかっているprimitive setを記載している。
tree.ipynb：関数を動作させることができる。


## How to use the Algorithm
### code 1 (Find candidates of primitive sets.)
```python
P_element = 6
limit = 40
primitive_sets = p5()
remove_pair = [[3],[5], [7,13]]
need_pair = [[2,11], [17]]

B, count, reps = tree_all(P_set(P_element), primitive_sets, remove_pair, need_pair, limit, print_steps=10,      print_path=False)
view_result(B, count, reps)
```

変数の説明を表にする。　変数名：説明：さらに説明
P_element：探索したい$P$の要素数
limit：どのくらい分岐をさせるか
primitive_sets：見つかっているprimitive setの集合：[]とすると指定なし。
remove_pair：removed_pairのどれか一つでも含む候補を除外する：[]とすると指定なし。
need_pair：need_pairのどれかを含んでいない候補を除外する：[]とすると指定なし。
print_steps：print_steps層ごとに終わったらlogを出す。：Falseでlogを出さなくする。
print_path：全パターン結果を列挙する：TrueもしくはFalse。基本的にFalseでいい。


上のアルゴリズムでは$|P| = 6$で、$P \not\supset \{3\}$ or $\{5\}$ or $\{7,13\}$かつ$P \supset \{2,11\}$ or $\{17\}$を満たす$P$であって、$L(P) \geq 40$を満たす$P$を全てs出力する。

注意：Theorem 2.4にあるように$P$がinfinite typeで、$P \subset Q$であれば$Q$もinfinite typeであった。このアルゴリズムでは、以下のように

```python
P_element = 6
limit = 40
primitive_sets = []
remove_pair = []
need_pair = []
```
$|P| = 6$であるprimitive setの候補を探索しているが、primitive_sets = []であるため、primitive set $\{2,3,5,7,19\} \subset P$を満たす$P$はinfinite typeとなるのでアルゴリズムが終了しないので気をつけなければいけない。

### code 2 (Check whether P is of finite type or not.)