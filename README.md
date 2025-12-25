# Algorithm Description

This repository implements the algorithm used in the paper available on arXiv.
Using this algorithm, one can determine whether a finite subset $P$ of the
set of all prime numbers is of finite type or not.

---

## File Structure

- [`function1.py`](function/function1.py)  
  Contains functions for finding candidates of primitive sets.

- [`function2.py`](function/function2.py)  
  Contains functions for function3.

- [`function3.py`](function/function3.py)  
  Contains functions for determining whether a given set $P$ is a primitive set.

- [`primitive_sets.py`](function/primitive_sets.py)  
  Contains all primitive sets that have been found so far.

- [`tree.ipynb`](tree.ipynb)  
  A Jupyter notebook for running and testing the functions.

- [`figure`](figure/)  
  This folder contains a PDF that exhaustively covers all cases for $|P| \le 4$.

---

## How to Use the Algorithm

### Code 1 (Find candidates of primitive sets)

```python
# ===== input =====
P_num = 6
limit = 1000
infinite_pair = p5()
remove_pair = [[3],[5], [7,13]]
need_pair = [[2,11], [17]]

# =================


result = run_tree_search(
    P_num=P_num,
    limit=limit,
    infinite_pair=infinite_pair,
    remove_pair=remove_pair,
    need_pair=need_pair,
    print_path=False,
    verbose=True,
)

new_inf = result["newly_found_infinite_sigs"]
```

#### Description of Variables

- `P_num`  
  The number of elements of  $P$ to be searched.

- `limit`  
  The maximum depth of branching.

- `infinite_pair`  
  The collection of known primitive sets.  
  If set to `[]`, no restriction is imposed.

- `remove_pair`  
  Candidates containing at least one of the sets in `remove_pair` are excluded.  
  If set to `[]`, no restriction is imposed.

- `need_pair`  
  Candidates that do not contain any of the sets in `need_pair` are excluded.  
  If set to `[]`, no restriction is imposed.

- `print_path`  
  If `True`, all explored paths are printed.  
  In most cases, `False` is sufficient.

- `verbose`  
  If `True`, a summary of the computation is displayed.

In the above algorithm, all sets P satisfying the following conditions are output:

- |P| = 6,
- P does not contain {3}, {5}, or {7,13},
- P contains {2,11} or {17},
- L(P) >= 40.

---

#### Remark

As stated in Theorem 2.4, if a set P is of infinite type and P ⊂ Q, then Q is also of infinite type.

In this algorithm, if one runs

```python
P_element = 6
limit = 40
primitive_sets = []
remove_pair = []
need_pair = []
```

the algorithm searches for candidates of primitive sets with $|P| = 6$.
However, since primitive_sets = [], any set $P$ satisfying {2,3,5,7,19} $\subset P$ is of infinite type, and the algorithm may not terminate.
Therefore, special care is required in this setting.

### Code 2 (Check whether P is of finite type or not)

Given a finite set P, this function determines whether P is a primitive set.
More precisely, P is classified into one of the following four cases:

(1) P contains a known primitive set.  
(2) P is of finite type.  
(3) P is a primitive set (i.e., an infinite loop exists).  
(4) The result is inconclusive.

Example:
```python
P = [2,3,5,7,19]
limit = 1000
check_loop(P,limit)
```
Result:
```python
P = {2, 3, 5, 7, 19} is a primitive set,
initial : (2,3273)[(2, 3)] RRRLLRRRLR  cycle_start : (180047,101481)[(7, 3)] LLRRRLR  cycle_end : (3591119,2026347)[(7, 3)] (cycle length = 7)
```
In this case, $P$ is a primitive set. Moreover, $\mathrm{APT}_{P}(2,3273) = \infty$.
Let $(x_0, y_0) = (180047,101481)$ and $(x_7, y_7) = (3591119,2026347)$.
Then these pairs satisfy the conditions of Proposition 2.2.

Here, $(180047,101481)[(7, 3)]$ means that $N_{P}(180047) = 7$ and
$N_{P}(101481) = 3$.
The symbols $L$ and $R$ represent the operations
$(a,b) \mapsto (a+b,b)$ and $(a,b) \mapsto (a,a+b)$, respectively.
Thus, the sequence $LR$ corresponds to
$(a,b) \mapsto (a+b,b) \mapsto (a+b,a+2b)$.
