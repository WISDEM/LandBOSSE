import numpy as np


class GridSearchTreeNode:
    def __init__(self):
        self.cell_specification = None
        self.children = []
        self.value = None


class GridSearchTree:
    def __init__(self, parametric_list):
        self.parametric_list = parametric_list

    def build_grid_tree_and_return_grid(self):
        root = self.build_tree()
        grid = self.dfs_search_tree(root, traversal=[])
        return grid

    def build_tree(self, depth=0, root=None):
        row = self.parametric_list.iloc[depth]
        cell_specification = f"{row['Dataframe name']}/{row['Row name']}/{row['Column name']}"
        start = row['Start']
        end = row['End']
        step = row['Step']

        if root == None:
            root = GridSearchTreeNode()

        # Putting the stop at end + step ensures the end value is in the sequence
        for value in np.arange(start, end + step, step):
            child = GridSearchTreeNode()
            child.value = value
            child.cell_specification = cell_specification
            root.children.append(child)
            if len(self.parametric_list) > depth + 1:
                self.build_tree(depth + 1, child)

        return root

    def dfs_search_tree(self, root, traversal, path=None):
        path = [] if path is None else path[:]

        if root.cell_specification is not None:
            path.append({
                'cell_specification': root.cell_specification,
                'value': root.value,
            })

        if len(root.children) == 0:
            traversal.append(path)

        for child in root.children:
            self.dfs_search_tree(child, traversal, path)

        return traversal
