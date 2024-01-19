# -*- coding: utf-8 -*-

# Copyright (c) 2004 - 2010 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing some graphical utility functions.
"""

class RecursionError(OverflowError, ValueError):
    """
    Unable to calculate result because of recursive structure.
    """
    
def sort(nodes, routes, noRecursion = False):
    """
    Function to sort widgets topographically.
    
    Passed a list of nodes and a list of source, dest routes, it attempts
    to create a list of stages, where each sub list is one stage in a process.
    
    The algorithm was taken from Boa Constructor.
    
    @param nodes list of nodes to be sorted
    @param routes list of routes between the nodes
    @param noRecursion flag indicating, if recursion errors should be raised
    @exception RecursionError a recursion error was detected
    @return list of stages
    """
    children, parents = _buildChildrenLists(routes)
    
    # first stage is those nodes having no incoming routes...
    stage = []
    stages = [stage]
    taken = []
    for node in nodes:
        if not parents.get(node):
            stage.append(node)
    
    if nodes and not stage:
        # there is no element, which does not depend on some other element!
        stage.append(nodes[0])
    
    taken.extend(stage)
    nodes = filter(lambda x, l = stage: x not in l, nodes)
    while nodes:
        previousStageChildren = []
        nodelen = len(nodes)
        
        # second stage are those nodes, which are direct children of the first stage
        for node in stage:
            for child in children.get(node, []):
                if child not in previousStageChildren and child not in taken:
                    previousStageChildren.append(child)
                elif child in taken and noRecursion:
                    raise RecursionError((child, node))
        
        # unless they are children of other direct children...
        stage = previousStageChildren
        removes = []
        for current in stage:
            currentParents = parents.get(current, [])
            for parent in currentParents:
                if parent in stage and parent != current:
                    # might wind up removing current
                    if not current in parents.get(parent, []):
                        # is not mutually dependant
                        removes.append(current)
        
        for remove in removes:
            while remove in stage:
                stage.remove(remove)
        
        stages.append(stage)
        taken.extend(stage)
        nodes = filter(lambda x, l = stage: x not in l, nodes)
        if nodelen == len(nodes):
            if noRecursion:
                raise recursionError(nodes)
            else:
                stages.append(nodes[:])
                nodes = []
    
    return stages
    
def _buildChildrenLists(routes):
    """
    Function to build up parent - child relationships.
    
    Taken from Boa Constructor.
    
    @param routes list of routes between nodes
    @return dictionary of child and dictionary of parent relationships
    """
    childrenTable = {}
    parentTable = {}
    for sourceID, destinationID in routes:
        currentChildren = childrenTable.get(sourceID, [])
        currentParents = parentTable.get(destinationID, [])
        if not destinationID in currentChildren:
            currentChildren.append(destinationID)
        if not sourceID in currentParents:
            currentParents.append(sourceID)
        childrenTable[sourceID] = currentChildren
        parentTable[destinationID] = currentParents
    return childrenTable, parentTable
