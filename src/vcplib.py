import re
import networkx as nx
import random
import time
from itertools import combinations
""" 
    This python3 modul contains some necessary and common functions 
    like a parser, preprocessing functions, used in the evaluated VCP models.
"""

  
def dimacscol_to_networkxgraph( col_file ): #{
    """
    This is a Dimacs *.col [1] (Coloring Problem) Graph Format parser.
    [1] http://mat.gsia.cmu.edu/COLOR/instances/contents.ps 

    c ... comments ...
    p edge |V| |E|
    e u v
    n ID Value  

    Input:  a dimacs col file
    Return: a networkx graph
    """ 
    text = open( col_file, 'r').read()

    """ adjacency """
    edge_pattern = re.compile( 
    '((?<!\w)e\s+(\w+)\s+(\w+))+'  # group 2,3
    );
    adj = dict() 
    for item in edge_pattern.finditer( text ):
        u = item.group(2)
        v = item.group(3)
        if u not in adj:    adj[ u ] = []
        if v not in adj:    adj[ v ] = []
        adj[ u ].append(v)
        adj[ v ].append(u)

    return nx.Graph( adj )
#} 

def best_clique( G, PRINT ): #{
    """ 
        return: a clique Q that has a largest cardinality m:=|Q| and has the 
                most cut edges |cut(Q)| amoung the cliques with cardinality m.
                To this end, we find a clique Q that maximizes 
                        |Q|*|E| + |cut(Q)|                              (1)
                The menaing of the weight |E| is that for each clique Q with |Q|>=2 it holds 
                        |cut(Q)| < |E|
                and thus for each two cliques Q and Q' with |Q|>|Q'|, ie. |Q|>=|Q'|+1 it holds
                        |Q'|*|E| + |cut(Q')|  <  |Q'|*|E| + |E|
                                              =  (|Q'|+1)*|E|
                                              <= |Q|*|E|
                                              <= |Q|*|E| + |cut(Q)|.
    """
    E = [ (u,v) for u,v in G.edges() if u != v ]
    lenE = len(G.edges())
    lenV = len(G.nodes())
    Q=[]
    best_cutQ=0
    bestQplusCutQ = 0 
    MAX_TRY=int(300*lenE/lenV) 
    print( 'MAX_TRY', MAX_TRY )
    TIME_LIMIT=60
    print( 'TIME_LIMIT', TIME_LIMIT )
    Gcomplement = nx.complement( G )

    t0 = time.time()
    t_last_print=t0
    for i in range( MAX_TRY ):
        if time.time() - t0 > TIME_LIMIT:
            break

        random.seed(i)
        _Q=nx.maximal_independent_set( Gcomplement )

        setQ = set(_Q)
        lenQ = len(_Q)
        cutQ = sum([ 1 for u,v in E if len( setQ & {u,v} ) == 1 ]) 
        QplusCutQ = lenQ * lenE + cutQ                                  # see (1)
        if bestQplusCutQ < QplusCutQ:
            bestQplusCutQ = QplusCutQ
            Q = _Q
            best_cutQ=cutQ
            string='\t|Q|: %s\t |cut(Q)|: %s\t try: %i\t %.2f sec' % ( lenQ, cutQ, i, time.time()-t0 )
            if PRINT&8:
                print( string )
        if PRINT&8 and time.time() - t_last_print > 5:
            string='\t|Q|: %s\t |cut(Q)|: %s\t try: %i\t %.2f sec' % ( len(Q), best_cutQ, i, time.time()-t0 )
            t_last_print=time.time()
            print( string )

    return Q
#}

def coloring_preprocessing_fast( G ): #{
    """
	Removes dominated nodes.

	WARNING:
	========
	This method are using the condition
		if adj[u] <= adj[v]:	# <=
	instead of
		if adj[u] < adj[v]:	    # <
	and this is correct, iff graph has no reflexive edges (u,v) with u == v.
	Hence the reflexive edges must be deleted, before this method begins.  
    """ 
    for u,v in G.edges():
        if u == v:  
            G.remove_edge(u,v)  # remove reflexive edges

    dominator = { v: v for v in G.nodes() }
    n=len(G.nodes())+1
    while len(G.nodes()) < n:
        n=len(G.nodes())
        adj={ v:set(G.neighbors(v)) for v in G }
        Vredundant = []
        for u,v in combinations( G.nodes(), 2):
            if adj[u] <= adj[v]:
                # print ( u, '<', v )
                Vredundant.append( u )
                dominator[ u ]=v
            elif adj[v] <= adj[u]:
                # print ( v, '<', u )
                Vredundant.append( v )
                dominator[ v ]=u
        G.remove_nodes_from(Vredundant)
    return G,dominator
#}
