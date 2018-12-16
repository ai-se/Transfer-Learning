"""
XTREE
"""
import os
import sys
# Update path
root = os.path.join(os.getcwd().split('src')[0], 'src')
if root not in sys.path:
    sys.path.append(root)

import numpy as np
import pandas as pd
from pdb import set_trace
from collections import Counter

from tools.containers import Thing
from sklearn.base import BaseEstimator
from tools.Discretize import discretize, fWeight

class XTREE(BaseEstimator):
    def __init__(self, opt=None):
        self.min=1
        self.klass=-1
        self.prune=False
        self.debug=True
        self.verbose=True
        self.max_level=10
        self.infoPrune=1

    def _show(self, tree=None, lvl=-1):        
        if tree is None:
            tree = self.tree
        if tree.f:
            print(('|..' * lvl) + str(tree.f) + "=" + "(%0.2f, %0.2f)" % tree.val + "\t:" + "%0.2f" % (tree.score), end="")
        if tree.kids:
            print('')
            for k in tree.kids:
                self._show(k, lvl + 1)
        else:
            print("")

    def _nodes(self, tree, lvl=0):
        if tree:
            yield tree, lvl
            for kid in tree.kids:
                lvl1 = lvl
                for sub, lvl1 in self._nodes(kid, lvl1 + 1):
                    yield sub, lvl1

    def _leaves(self, tree):
        for node, _ in self._nodes(tree):
            # print "K>", tree.kids[0].__dict__.keys()
            if not node.kids:
                yield node

    def _find(self,  test_instance, tree_node=None):
        if tree_node is None:
            tree_node = self.tree

        if len(tree_node.kids) == 0:
            return tree_node
    
        for kid in tree_node.kids:
            if kid.val[0] <= test_instance[kid.f] < kid.val[1]:
                return self._find(test_instance, kid)
            elif kid.val[1] == test_instance[kid.f] == self.tree.t.describe()[kid.f]['max']:
                return self._find(test_instance, kid)

    def _tree_builder(self, tbl, rows=None, lvl=-1, asIs=10 ** 32, up=None, klass=-1, branch=[],
            f=None, val=None, opt=None):
        
        here = Thing(t=tbl, kids=[], f=f, val=val, up=up, lvl=lvl
                    , rows=rows, modes={}, branch=branch)

        features = fWeight(tbl)

        if self.prune and lvl < 0:
            features = fWeight(tbl)[:int(len(features) * self.infoPrune)]

        name = features.pop(0)
        remaining = tbl[features + [tbl.columns[self.klass]]]
        feature = tbl[name].values
        klass = tbl[tbl.columns[self.klass]].values
        N = len(klass)
        here.score = np.mean(klass)
        splits = discretize(feature, klass)
        lo, hi = min(feature), max(feature)

        def _pairs(lst):
            while len(lst) > 1:
                yield (lst.pop(0), lst[0])

        cutoffs = [t for t in _pairs(sorted(list(set(splits + [lo, hi]))))]

        if lvl > (self.max_level if self.prune else int(len(features) * self.infoPrune)):
            return here
        if asIs == 0:
            return here
        if len(features) < 1:
            return here

        def _rows():
            for span in cutoffs:
                new = []
                for f, row in zip(feature, remaining.values.tolist()):
                    if span[0] <= f < span[1]:
                        new.append(row)
                    elif f == span[1] == hi:
                        new.append(row)
                yield pd.DataFrame(new, columns=remaining.columns), span

        def _entropy(x):
            C = Counter(x)
            N = len(x)
            return sum([-C[n] / N * np.log(C[n] / N) for n in C.keys()])

        for child, span in _rows():
            n = child.shape[0]
            toBe = _entropy(child[child.columns[self.klass]])
            if self.min <= n < N:
                here.kids += [self._tree_builder(child, lvl=lvl + 1, asIs=toBe, up=here
                                    , branch=branch + [(name, span)]
                                    , f=name, val=span, opt=opt)]

        return here

    def fit(self, X, y):
        raw_data = pd.concat([X,y], axis=1)
        self.tree = self._tree_builder(raw_data)
        return self

    def predict(self, Xt, yt):
        new_df = pd.DataFrame(columns=Xt.columns)
        for row_num in range(len(Xt)):
            if yt.iloc[row_num]: 
                old_row = Xt.iloc[row_num]
                pos = self._find(old_row)
                set_trace()
        return self
