##################################################################################
##  SBC - GIA                                                        11/12/2023 ##
##                          FUNCTIONS AND CLASSES                               ##
##                                                                              ##
##################################################################################

# ----- Imports -----

import pandas as pd
import numpy as np
import pickle
from graphviz import Digraph
from ast import literal_eval


#  ----- Class DecisionTree -----

class DecisionTree:

    # -----Inner Class DecisionNode -----

    class _DecisionNode:
        def __init__(self, value=None, children=None, subset=None, path=None):
            """
            Initializes a DecisionNode.
                :param value: The The feature/question/cases subset associated with this node
                :param subset: The subset of Cas instances at this node. Only different from {} at leaf nodes.
                :param parent: DecisionNode instance being the parent of the actual DecisionNode instance. None if DecisionNode instance is root of the entire tree.
                :param path: The path taken to reach this node.
            """

            self._value = value
            self._children = children
            self._subset = subset
            self._path = path

    def __init__(self, value = None, children = {}, subset = None, path = {}, max_depth=6, dataset = pd.DataFrame()):
        
        self._max_depth = max_depth
        self._root = self._DecisionNode(value,children,subset,path)
        self._dataset = dataset
    
    def add_child(self, answer, child):
        """
        Adds a child tree associated with a specific answer.
            :param answer: The answer or value leading to the child tree.
            :param child: The child tree to add.
        """
        children = self._root._children.copy()
        children[answer] = child._root
        self._root._children = children

        #self._root._children[answer] = child._root <-- Check why does this not work
    
    def is_leaf(self):
        """
        Determines if this tree's node is a leaf node (i.e., has no children).
            :return: True if the node is a leaf node, False otherwise.
        """
        return len(self._root._children) == 0
    
    def get_child(self, answer):
        """
        Retrieves the child tree corresponding to a given answer.
            :param answer: The answer or value for which the child tree is needed.
            :return: The child tree associated with the given answer.
        """
        child = DecisionTree()
        child._root = self._root._children.get(answer)
        return child
    
    def get_children(self):
        """
        Retrieves the whole set of children trees corresponding to this tree.
            :return: A list of (answer,tree_child) tuples containing the list of children trees corresponding to the actual tree root
        """
        list_childs = []
        for answer,child in self._root._children.items():
            child_tree = DecisionTree()
            child_tree._root = child
            list_childs.append((answer,child_tree))
        return list_childs

    
    def get_leaves(self):
        
        """
        Retrieves the whole set of leaf nodes that hung from the actual DecisionTree instance
        """
        set_leaves = []
        def aux(tree):
            if tree.is_leaf():
                set_leaves.append(tree._root)
            else:
                for _,child in tree.get_children():
                    aux(child)
        aux(self)
        return set(set_leaves)
    
    def modify_leaf(self,path,subset):
        """
        Modifies the '_subset' attribute of a node in a tree structure.
            :param path: List of indices representing the path to the node to be modified.
            :param subset: The new value for the '_subset' attribute.
        """
        child = self._root._children[path[self._root._value]]
        child_as_tree = self.get_child(path[self._root._value])
        while not child_as_tree.is_leaf():
            child2 = child._children[path[child._value]]
            child_as_tree = child_as_tree.get_child(path[child._value])
            child = child2
        child._subset = subset
        child._value = f"Subset Cases:\n {[cas.id_cas for cas in subset]}"
    
    def save(self, filename):
        """
        Saves the current state of the decision tree to a file.
            :param filename: The name of the file to save the tree.
        """
        with open(filename + '.pkl', 'wb') as file:
            pickle.dump(self, file)
    
    def load(self, filename):
        """
        Loads a decision tree from a file.
            :param filename: The name of the file to load the tree from.
            :return: The root node of the loaded decision tree.
        """
        with open(filename + '.pkl', 'rb') as file:
            return pickle.load(file)

    def build_tree(self, features, data = None, path={}, depth=0):
        """
        Builds a decision tree recursively.
            :param features: A list of features to use for splitting the data.
            :param data: The dataset to build the tree from.
            :param path: A dictionary representing the path taken to reach the current node.
            :param depth: The current depth in the tree.
            :param max_depth: The maximum depth of the tree.
            :return: The root node of the decision tree.
        """
        data = self._dataset if (data is None) else data

        # Base case: Return a leaf node if maximum depth is reached, no features left, or no data
        #            The leaf have a set of Case instances that meet the attributs
        if depth == self._max_depth or len(features) == 0:
            subset_cases, list_cases = set(), []
            
            for index, row in data.iterrows():
                problem_description = (row["genere_persona"], row["any_naixement"], row["pref_adaptacio_peli"], row["pref_best_seller"],
                                       row["pref_tipus_lectura"],row["pref_sagues"], row["Comèdia"], row["Ficció"], row["Ciència Ficció"],
                                       row["Històrica"], row["Romàntic"], row["Fantasia"], row["Ciència"], row["Creixement personal"],
                                       row["Policiaca"], row["Juvenil"], row["pagines_max"], row["comprat"], row["Idioma"])
                
                subset_cases.add(Case(index, row["id_usuari"], problem_description, row["id_llibre"], row["score"]))
                list_cases.append(index)

            value = f"Subset Cases:\n {list_cases}"
            return DecisionTree(value=value,subset=subset_cases,path=path)
        
        # Select the current feature to split on.
        #     `any_naixement` requires specific treatment because we are looking for an interval
        
        current_feature = features[0]
        tree = DecisionTree(value=current_feature,path=path)

        if current_feature != 'any_naixement':
            possible_answers = self._dataset[current_feature].unique()
            
            for answer in possible_answers:
                # Create a subset of data corresponding to the current answer
                subset = data[data[current_feature] == answer]
                
                remaining_features = features[1:]
                new_path = path.copy()
                new_path[current_feature] = answer
                
                # Recursively call `build_tree` to build the subtree
                child_tree = self.build_tree(remaining_features, subset, new_path, depth + 1)
                tree.add_child(answer, child_tree) 
        else:
            # Based on the stadistic study, we use 2003 to split `any_naixement`
            subset_1 = data[data[current_feature] < 2003]
            subset_2 = data[data[current_feature] >= 2003]
            remaining_features = features[1:]

            new_path_1 = path.copy(); new_path_2 = path.copy()
            new_path_1[current_feature] = "< 2003"
            new_path_2[current_feature] = ">= 2003"
                
            # Recursively call `build_tree` to build the subtree twice.
            child_tree_1 = self.build_tree(remaining_features, subset_1, new_path_1, depth + 1)
            child_tree_2 = self.build_tree(remaining_features, subset_2, new_path_2, depth + 1)
            tree.add_child("< 2003", child_tree_1)
            tree.add_child(">= 2003", child_tree_2)

        return tree

    def print_tree(self, depth=0):
        """
        Prints a representation of the decision tree.
            :param node: The current node in the tree.
            :param depth: The depth of the current node, used for indentation.
        """
        if self.is_leaf():  # If it's a leaf tree, print its value
            print("  " * depth + "Leaf:", self._root._value)
        else:  # If it's a decision node
            print("  " * depth + "Question:", self._root._value)
            for (answer,child) in self.get_children():  # Iterate through children
                print("  " * (depth + 1) + "Answer:", answer)
                child.print_tree(depth + 2)  # Recursively print each child node


    def plot_node(self, graph, node, node_id, parent_id=None, label=None):
        """
        Plots a single node and its connections in the decision tree graph.
            :param graph: The graph object to which nodes and edges are added.
            :param node: The current node to plot.
            :param node_id: The unique identifier for the current node.
            :param parent_id: The identifier of the parent node.
            :param label: The label for the edge connecting to the parent node.
        """
        if node.is_leaf():  # If it's a leaf node
            graph.node(node_id, label=node.value, shape="box")
            if parent_id is not None:
                graph.edge(parent_id, node_id, label=str(label))
        
        else:  # If it's a decision node
            graph.node(node_id, label=node.value)
            if parent_id is not None:
                graph.edge(parent_id, node_id, label=str(label))
            
            for answer, child in node.children.items():  # Iterate through children
                child_id = f"{node_id}_{str(answer)}"
                self.plot_node(graph, child, child_id, node_id, label=answer)

    def build_Digraph(self):
        """
        Creates a graph representation of the decision tree.
            :param root: The root node of the decision tree.
            :return: The graph object representing the tree.
        """
        self._graph = Digraph(comment='Decision Tree')

        def add_node(graph, node, node_id, parent_id=None, label=None):
            """
            Plots a single node and its connections in the decision tree graph.
                :param graph: The graph object to which nodes and edges are added.
                :param node: The current node to plot.
                :param node_id: The unique identifier for the current node.
                :param parent_id: The identifier of the parent node.
                :param label: The label for the edge connecting to the parent node.
            """
            if node.is_leaf():  # If it's a leaf tree
                graph.node(node_id, label=node._root._value, shape="box")
                if parent_id is not None:
                    graph.edge(parent_id, node_id, label=str(label))
            
            else:  # If it's a decision node
                graph.node(node_id, label=node._root._value)
                if parent_id is not None:
                    graph.edge(parent_id, node_id, label=str(label))
                
                for answer, child in node.get_children():  # Iterate through children
                    child_id = f"{node_id}_{str(answer)}"
                    add_node(graph, child, child_id, node_id, label=answer)
        
        add_node(self._graph,self,'root')
    
    def plot_tree(self):
        self.build_Digraph()
        self._graph.render('decision_tree', view=True)

    def evaluate_case_through_tree(self, case, list_parents):
        """
        Evaluates a case through the decision tree to find the corresponding leaf node.
            :param node: The current node in the tree.
            :param case: The case to be evaluated, represented as a dictionary of features.
            :returns: 1) The leaf node corresponding to the case, or None if no valid path is found.
                      2) The list of DecisionNode instances that are the ancestors of this leaf node.
        """
        if self.is_leaf():
            return self._root,list_parents

        feature_to_check = self._root._value # The feature that the current node is querying
        feature_value_in_case = case.get(feature_to_check)

        # If the feature is not in the case, evaluation cannot proceed
        if feature_value_in_case is None:
            return None

        # Find the child node corresponding to the answer in the case
        child_tree = self.get_child(feature_value_in_case)

        # If there is no corresponding child tree, the path is invalid
        if child_tree._root is None:
            return None

        return child_tree.evaluate_case_through_tree(case, list_parents = list_parents + [child_tree])

    def make_trace(self, new_case):
        """
        Traces and prints the path taken for a given case in the decision tree.
            :param decision_tree_root: The root node of the decision tree.
            :param new_case: The new case to be traced, represented as a dictionary of features.
        """
        leaf_node,_ = self.evaluate_case_through_tree(new_case, [self])
        # Trace and print the path:
        print("This case has been categorized in this leaf as they share the following attributes:")
        for attribute, answer in leaf_node._path.items():
            print(f"       - The attribute {attribute} has an answer of {str(answer)}.")




# ----- Class Case -----

class Case:
    def __init__(self, id_cas=None, id_usuari=None, problema=(None,)*19, solucio=None, puntuacio=None):
        """
        Initializes a case instance.
            :param id_cas: Case ID.
            :param id_usuari: User ID associated with the case.
            :param problema: A tuple representing the problem, containing attributes like gender, year of birth,
                             preferences in movies, books, reading types, genres, etc.
            :param solucio: The solution associated with this case.
            :param puntuacio: The score or rating of the solution.
        """
        self.id_cas = id_cas
        self.id_usuari = id_usuari
        self.genere_persona, self.any_naixement, self.pref_adaptacio_peli, self.pref_best_seller, self.pref_tipus_lectura, self.pref_sagues, self.comedia,\
        self.ficcio, self.ciencia_ficcio, self.historica, self.romance, self.fantasia, self.ciencia, self.creixement_personal,\
        self.policiaca, self.juvenil, self.pagines_max, self.comprat,self.idioma = problema
        self.solucio = solucio
        self.puntuacio = puntuacio
    
    #Getters

    def get_problem_vector(self):
        """
        Returns a vector with the descriptor attributes ordered as in the feature importance variable.
            :return: A list of problem attributes in the order of their importance.
        """
        return [self.genere_persona, self.pref_sagues, self.pref_tipus_lectura, self.romance,
                self.ciencia_ficcio, self.any_naixement, self.comedia, self.historica, self.ficcio,
                self.fantasia, self.ciencia, self.creixement_personal, self.policiaca, self.juvenil,
                self.pagines_max, self.pref_adaptacio_peli, self.pref_best_seller]
    
    #Setters
    

    def from_dict(self, case_dict):
        """
        Updates the attributes of the instance based on a dictionary representation of a case.
        
        :param case_dict: A dictionary containing case attributes. Each key corresponds to an attribute
                          of the case, and the associated value is the attribute's value.
        """
        self.id_usuari = case_dict['id_usuari']
        self.genere_persona, self.any_naixement, self.pref_adaptacio_peli, self.pref_best_seller, \
        self.pref_tipus_lectura, self.pref_sagues, self.comedia, self.ficcio, self.ciencia_ficcio, \
        self.historica, self.romance, self.fantasia, self.ciencia, self.creixement_personal, \
        self.policiaca, self.juvenil, self.pagines_max, self.idioma = [case_dict[key] for key in ["genere_persona", "any_naixement", "pref_adaptacio_peli", "pref_best_seller", "pref_tipus_lectura", "pref_sagues", "Comèdia", "Ficció", "Ciència Ficció", "Històrica", "Romàntic", "Fantasia", "Ciència", "Creixement personal", "Policiaca", "Juvenil", "pagines_max", "idioma"]]
    
    def to_dict(self):
        """
        Converts the attributes of a Case instance to a dictionary.
            :return: A dictionary with attribute names as keys and their corresponding values.
        """
        return {
            'id_cas': self.id_cas,
            'id_usuari': self.id_usuari,
            'genere_persona': self.genere_persona,
            'any_naixement': "< 2003" if (self.any_naixement < 2003) else ">= 2003",
            'pref_adaptacio_peli': self.pref_adaptacio_peli,
            'pref_best_seller': self.pref_best_seller,
            'pref_tipus_lectura': self.pref_tipus_lectura,
            'pref_sagues': self.pref_sagues,
            'Comèdia': self.comedia,
            'Ficció': self.ficcio,
            'Ciència Ficció': self.ciencia_ficcio,
            'Històrica': self.historica,
            'Romàntic': self.romance,
            'Fantasia': self.fantasia,
            'Ciència': self.ciencia,
            'Creixement personal': self.creixement_personal,
            'Policiaca': self.policiaca,
            'Juvenil': self.juvenil,
            'pagines_max': self.pagines_max,
            'comprat': self.comprat,
            'idioma': self.idioma,
            'solucio': self.solucio,
            'puntuacio': self.puntuacio
        }

    def set_id_case(self,id):
        self.id_cas = id
    
    def set_puntuacio(self,puntuacio):
        self.puntuacio = puntuacio
    
    def set_solucio(self,id_book):
        self.solucio = id_book
    
    def set_comprat(self,comprat):
        self.comprat = comprat
    
    #Python-like methods
        
    def copy(self):
        return Case(id_usuari=self.id_usuari,problema=(self.genere_persona, self.any_naixement, self.pref_adaptacio_peli, self.pref_best_seller, \
        self.pref_tipus_lectura, self.pref_sagues, self.comedia, self.ficcio, self.ciencia_ficcio, \
        self.historica, self.romance, self.fantasia, self.ciencia, self.creixement_personal, \
        self.policiaca, self.juvenil, self.pagines_max, 'No', self.idioma))




#-----Functionalities-----#

# 1. Data and Features
#data = pd.read_csv("Cases.csv")

#Hem de llegir la columna de idioma com a objectes set() per a fe rmés senzilla la implementació.
#data['Idioma'] = data.Idioma.apply(literal_eval)


#features_by_importance = ['genere_persona', 'pref_sagues', 'pref_tipus_lectura', 'Romàntic', 'Ciència Ficció', 'any_naixement', 
#                                  'Comèdia', 'Històrica', 'Ficció', 'Fantasia', 'Ciència', 'Creixement personal', 'Policiaca', 'Juvenil', 
#                                  'pagines_max', 'pref_adaptacio_peli', 'pref_best_seller']

# 2. Create the DT

#dt_instance = DecisionTree(dataset=data, max_depth=6)  # Adjust max_depth if needed
#dt = dt_instance.build_tree(features_by_importance)

#  2.1 Or load it

#PATH_FILE = "Decision_tree"
#dt_instance = DecisionTree()
#dt = dt_instance.load(PATH_FILE)


# 3. DT Graphic (Optional)
#dt.plot_tree()

# 4. New case to be classified:
#case1 = data.iloc[60]

# 5. Make Trace
#dt.make_trace(case1)

# 6. Save DT

#PATH_FILE = "Decision_tree"
#dt.save(PATH_FILE)

