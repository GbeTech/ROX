import bintrees

tree = bintrees.AVLTree()
tree.insert((1, 1, 1), "one")
tree.insert((1, 0, 1), "two")
tree.insert((1, 1, 0), "zero")

print(tree.min_item())