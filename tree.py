# Python program to demonstrate delete operation 
# in binary search tree 

# A Binary Tree Node

class Node:

    # Constructor to create a new node
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None

    # A utility function to insert a new node with given key in BST

    def insert(self, key):
        # If the tree is empty, return a new node
        if self is None:
            return Node(key)

        # Otherwise recur down the tree
        if key < self.key:
            self.left = insert(self.left, key)
        else:
            self.right = insert(self.right, key)

        # return the (unchanged) self pointer

    def delete(self, key):
        # Base Case
        if not self.key:
            return None

        # If the key to be deleted is smaller than the self's
        # key then it lies in left subtree
        if key < self.key:
            if self.left:
                self.left = self.left.delete(key)
            # else:
            #     self.left = Node(key)

        # If the kye to be delete is greater than the self's key
        # then it lies in right subtree
        elif key > self.key:
            if self.right:
                self.right = self.right.delete(key)
            else:
                self.right = Node(key)

        # If key is same as self's key, then this is the node
        # to be deleted
        else:
            # Node with only one child or no child
            if not self.left:
                temp = self.right
                self.key = None
                return temp

            elif not self.right:
                temp = self.left
                self.key = temp.key
                return temp

            # Node with two children: Get the inorder successor
            # (smallest in the right subtree)
            temp = self.minimum()

            # Copy the inorder successor's content to this node
            self.key = temp.key

            # Delete the inorder successor
            self.right = self.right.delete(temp.key)
            self.left = self.left.delete(temp.key)

        return self

    def minimum(self):
        current = self.left

        # loop down to find the leftmost leaf
        while current.left:
            current = current.left

        return current

    def maximum(self):
        current = self.right

        while current.right:
            current = current.right

        return current

    def pprint(self):
        if self.left:
            self.left.pprint()
        print(self.key)
        if self.right:
            self.right.pprint()
            # else:
            #     print(self.key), self.left.pprint()


def insert(node, key):
    # If the tree is empty, return a new node
    if node is None:
        return Node(key)

    # Otherwise recur down the tree
    if key < node.key:
        node.left = insert(node.left, key)
    else:
        node.right = insert(node.right, key)

    # return the (unchanged) node pointer
    return node


# Given a non-empty binary search tree, return the node
# with minum key value found in that tree. Note that the 
# entire tree does not need to be searched 
def minValueNode(node):
    current = node

    # loop down to find the leftmost leaf
    while (current.left is not None):
        current = current.left

    return current


# Given a binary search tree and a key, this function
# delete the key and returns the new root 
def deleteNode(root, key):
    # Base Case
    if root is None:
        return root

    # If the key to be deleted is smaller than the root's
    # key then it lies in left subtree
    if key < root.key:
        root.left = deleteNode(root.left, key)

    # If the kye to be delete is greater than the root's key
    # then it lies in right subtree
    elif (key > root.key):
        root.right = deleteNode(root.right, key)

    # If key is same as root's key, then this is the node
    # to be deleted
    else:
        # Node with only one child or no child
        if root.left is None:
            temp = root.right
            root = None
            return temp

        elif root.right is None:
            temp = root.left
            root = None
            return temp

        # Node with two children: Get the inorder successor
        # (smallest in the right subtree)
        temp = minValueNode(root.right)

        # Copy the inorder successor's content to this node
        root.key = temp.key

        # Delete the inorder successor
        root.right = deleteNode(root.right, temp.key)

    return root


# A utility function to do inorder traversal of BST
def inorder(root):
    if root is not None:
        inorder(root.left)
        print(root.key), inorder(root.right)


# Driver program to test above functions
""" Let us create following BST 
			50 
		/	 \ 
		30	 70 
		/ \ / \ 
	20 40 60 80 """

# root = None
# root = Node(50)
# root.insert(60)
# root.insert(40)
# root.insert(30)
# root.delete(4)
# root.delete(50)
# root.delete(60)
# root.delete(40)

# root.pprint()


# inorder(root)

# root = insert(root, 30)
# root = insert(root, 20)
# root = insert(root, 40)
# root = insert(root, 70)
# root = insert(root, 60)
# root = insert(root, 80)

# print(f"Inorder traversal of the given tree")
# inorder(root)
#
# print(f"Delete 20")
# root = delete(root, 20)
# print("Inorder traversal of the modified tree")
# inorder(root)
#
# print("\nDelete 30")
# root = delete(root, 30)
# print("Inorder traversal of the modified tree")
# inorder(root)
#
# print("\nDelete 50")
# root = delete(root, 50)
# print("Inorder traversal of the modified tree")
# inorder(root)

# This code is contributed by Nikhil Kumar Singh(nickzuck_007)