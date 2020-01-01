import unittest

class Tree:
    """Binary Tree Object"""
    
    def __init__(self, value, left_tree = None, right_tree = None):
        self.value = value
        self.left_tree = left_tree
        self.right_tree = right_tree
    
    @staticmethod
    def identity(n):
        if n == 1:
            return Tree(False)
        return Tree(False, Tree.identity(n-1), Tree.identity(n-1))
    
    ## operations
    
    def mul(self, other_tree):
        if (self.left_tree is None):
            left = None
            right = None
        # if the other_tree has top value of 1 (True)
        elif other_tree.value:
            left = self.right_tree.mul(other_tree.left_tree)
            right = self.left_tree.mul(other_tree.right_tree)
        else:
            left = self.left_tree.mul(other_tree.left_tree)
            right = self.right_tree.mul(other_tree.right_tree)
        res = Tree(self.value ^ other_tree.value, left, right)
        return res
        
    def __mul__(self, other_tree):
        return self.mul(other_tree)
        
    def power(self, n):
        if n == 0:
            return Tree.identity(self.depth())
        if n == 1:
            return self
        if n < 0:
            return self.inv().power(-n)
        return self.mul(self.power(n-1))
        
    def __pow__(self, n):
        return self.power(n)
    
    def inv(self):
        if self.is_leaf():
            return Tree(self.value)
        if self.value:
            return Tree(True, self.right_tree.inv(), self.left_tree.inv())
        return Tree(False, self.left_tree.inv(), self.right_tree.inv())
        
    def __eq__(self, other_tree):
        return (self.value == other_tree.value and self.left_tree == other_tree.left_tree and self.right_tree == other_tree.right_tree)
        
    # A tree of depth n has an action on sequences of size 2**n
    def act(self, seq):
        l = len(seq)
        # split the sequence in 2
        left = seq[0:int(l/2)]
        right = seq[int(l/2):l]
        # if this node is a leaf
        if self.is_leaf():
            if self.value:
                return right + left
            else:
                return left + right
        # if this node is not a leaf
        if self.value:
            return self.left_tree.act(right) + self.right_tree.act(left)
        else:
            return self.left_tree.act(left) + self.right_tree.act(right)
            
    # return a random sequence of size 2**n where n is the depth of the tree
    def give_me_a_seq(self):
        n = self.depth()
        seq = []
        for i in range(2**n):
            seq += [randint(0, 1)]
    
        return seq
        
    # return domains of the seq action
    def get_domains(self, init = None):
        if init is None:
            l = list(range(0, 2**self.depth()))
        else:
            l = init
        any_updates = True
        while(any_updates):
            any_updates = False
            l2 = self.act(l)
            # for each element of the sequences
            for i in range(0, len(l2)):
                # if the image has lower number than original
                if l2[i] < l[i]:
                    l[i] = l2[i]
                    any_updates = True
        return l
        

    # solve equations on beats
    # Solve g.B1 = B2 or g = B2/B1
    @staticmethod
    def solve(B1, B2):
		# check if a solution can exist
        if(sum(B1) != sum(B2)):
            return []
        l = len(B1)
        solutions = []
        # if the sequences have length 2, the solutions are given by the beat sum
        if(l == 2):
            # if both sequences are the same then the identity is a solution
            if(B1 == B2):
                solutions += [Tree(False)]
                # if additionaly B1 and B2 are constant beats, then the twist is also a solution
                if(sum(B1) == 0 or sum(B1) == 2):
                    solutions += [Tree(True)]
            # if the sequences are different (yet have the same sum) then they must be related by a twist
            else: solutions += [Tree(True)]
            return solutions

        # split the sequences in 2
        B1_left  = B1[0:int(l/2)]
        B1_right = B1[int(l/2):l]
        B2_left  = B2[0:int(l/2)]
        B2_right = B2[int(l/2):l]

        # we first look for a solution where the root is not twisted (root is 0)
        untwisted_left_sol = Tree.solve(B1_left, B2_left)
        untwisted_right_sol = Tree.solve(B1_right, B2_right)

        # we combine the untwisted solutions
        solutions = [ Tree(False, left, right) for left in untwisted_left_sol for right in untwisted_right_sol ]
        
        # we now look for solutions where the root is twisted (root is 1)
        twisted_left_sol = Tree.solve(B1_left, B2_right)
        twisted_right_sol = Tree.solve(B1_right, B2_left)

        # we combine the twisted solutions and add them to the solutions list
        solutions += [ Tree(True, left, right) for left in twisted_left_sol for right in twisted_right_sol ]
        
        return solutions

    #### Utility functions
    
    def is_leaf(self):
        return self.left_tree is None
        
    def depth(self):
        if self.is_leaf():
            return 1
        return 1 + self.left_tree.depth()
        
    # this function creates a graph for the tree using the network format
    # returns node_index, edge_index
    def graph_repr(self, tree = None, node_index = 0, edge_index = 0):
        if tree is None:
            tree = {'nodes':[{'id':node_index, 'label': int(self.value)}], 'edges':[], 'labels': {"0": "#000000", "1": "#FF0000"}}
        # if tree is not None
        # we create this node
        else:
            tree['nodes'] = tree['nodes'] + [{'id':node_index, 'label': int(self.value)}]

        # if no substrees
        if self.is_leaf():
            return node_index+1, edge_index, tree   
        
        # we create left edge
        tree['edges'] = tree['edges'] + [{'id':edge_index, 'source': node_index, 'target': node_index+1}]
        # we create child left tree
        new_node_index, edge_index, tree = self.left_tree.graph_repr(tree, node_index + 1, edge_index + 1)
        
        # we create right edge
        tree['edges'] = tree['edges'] + [{'id':edge_index, 'source': node_index, 'target': new_node_index}]
        # we create child right tree
        node_index, edge_index, tree = self.right_tree.graph_repr(tree, new_node_index, edge_index + 1)
        
        return node_index, edge_index, tree
        
        
    def __repr__(self, network = False):
        if network:
            a,b,tree = self.graph_repr()
            return tree
        if self.left_tree is None:
            return (str(self.value))
        else:
            return (str(self.value) + "(" + str(self.left_tree) + " " + str(self.right_tree) + ")")
            
    def __str__(self, network = False):
        if network:
            a,b,tree = self.graph_repr()
            return "%network " + str(tree).replace("'", '"')
        else:
            return self.__repr__(False)
            
            
    def network(self):
        a,b,tree = self.graph_repr()
        print("%network " + str(tree).replace("'", '"'))
        
        



#### Testing the code

class TestTree(unittest.TestCase):
    """
    Test the Tree class
    """
 
    def test_mul(self):
        """
        Test that multiplication, inversion and power is working
        """
        a = Tree(True, Tree(True), Tree(False))
        i = Tree(True, a, a)
        # test multiplication and powers
        self.assertEqual(a*a, Tree(False, Tree(True), Tree(True)))
        self.assertEqual(a ** 4, Tree.identity(2))
        #print(i ** 3)

        # test inverses and non-positive powers
        self.assertEqual(a * a.inv(), Tree.identity(2))
        self.assertEqual(i**0, Tree.identity(3))
        self.assertEqual(i**(-1) * i, Tree.identity(3))
        self.assertEqual(i**(-2) * i**2, Tree.identity(3))
#self.assertEqual(result, 3)
 
 
    def test_solve(self):
        """
        Test solving beat equation
        """
        self.assertEqual(len(Tree.solve([1, 1],  [1, 1])), 2) # this equation should have 2 solutions (full group T1)
        self.assertEqual(Tree.solve([1, 0],  [1, 0]), [Tree(False)]) # this equation should only have the identity as solution
        
        # test on Stab 1011 = {0, Tree(False, False, True)}
        s1011 = Tree.solve([1, 0, 1, 1],  [1, 0, 1, 1])
        self.assertEqual(len(s1011), 2)
        self.assertIn(Tree(False, Tree(False), Tree(True)), s1011)
        
        # test on Stab 1010 = {0, pure twist}
        s1010 = Tree.solve([1, 0, 1, 0],  [1, 0, 1, 0])
        self.assertEqual(len(s1010), 2)
        self.assertIn(Tree(True, Tree(False), Tree(False)), s1010)
        
        # check on a solution that does not have solutions
        self.assertEqual(Tree.solve([1, 1, 1, 0],  [1, 1, 1, 1]), [])
        
if __name__ == '__main__':
	unittest.main()
