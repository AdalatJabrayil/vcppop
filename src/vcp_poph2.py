import networkx as nx
from vcplib import *
from gurobipy import *


def color( G, PRINT=8, TLIM=3600, **args ): #{
    """ 
    LANGUAGE: python3
    MODEL:    VCP-POPH2 in [1]
    [1] A.Jabrayilov and P.Mutzel, "Strengthened Partial-Ordering Based ILP Models for the Vertex Coloring Problem"
    """
    print_solution=False
    degrP=False          # nodes with higher degree get higher branching priority 
    if "print_solution"  in args:   print_solution=args['print_solution']
    if "degrP"           in args:   degrP=args['degrP']
    print( "args:", [ key for key in args if args[ key ] ])

    V_0 = len(G.nodes())
    E_0 = len(G.edges())

    G,dominator = coloring_preprocessing_fast( G )     

    V = G.nodes()
    E = G.edges()
    if PRINT&16:	print ( 'V:', V )

    H = len(set(nx.greedy_color(G).values()))
    ub = H

    Q = best_clique( G, PRINT )
    lb = len(Q) 

    if lb == ub: 
        rt   = 0
        print( V_0, E_0, len(V), len(E), lb, ub, lb, ub, 'init', end=' ' )
        return 0

    chi = Q[-1]
    Q =   Q[:-1]

    if PRINT&8:	print ( 'Q, chi: ', Q, chi )
    if PRINT&8:	print ( 'degree: ', [G.degree(v) for v in Q], G.degree(chi) )

    try:
        #  __  __           _      _ 
        # |  \/  | ___   __| | ___| |
        # | |\/| |/ _ \ / _` |/ _ \ |
        # | |  | | (_) | (_| |  __/ |
        # |_|  |_|\___/ \__,_|\___|_|
        #                            
        p = Model("coloring")
        p.params.OutputFlag = 1&PRINT
        p.params.SEED       = 0	    # randomized=False
        p.params.THREADS    = 1	    # nur ein thread
        p.params.TimeLimit  = TLIM

        y = { (i,u): p.addVar(vtype=GRB.BINARY) for u in V for i in range(H) }
        x = { (u,i): p.addVar(vtype=GRB.BINARY) for u in V for i in range(H) }
        p.update()

        """ precolor Q """
        for i in range( len(Q) ): 
            y[i,Q[i]].UB = 0
        p.update()

        """ branching priority depending on vertex degrees """
        if degrP:
            for v,d in nx.degree(G):
                for i in range( H ):
                    y[i,v].BranchPriority = d
                    x[v,i].BranchPriority = d
            p.update()

        """ a color>H-1 may not be used, only colors 0,1,...,(H-1) are allowed """
        y[H-1,chi].UB = 0
        p.update()

        # """    _     _           _   _       
        #   ___ | |__ (_) ___  ___| |_(_)_   __
        #  / _ \| '_ \| |/ _ \/ __| __| \ \ / /
        # | (_) | |_) | |  __/ (__| |_| |\ V / 
        #  \___/|_.__// |\___|\___|\__|_| \_/  
        #           |__/                       
        # """
        p.setObjective( 1 + sum ([ y[i,chi] for i in range(H) ]),   GRB.MINIMIZE)


        # """        _     _           _   
        #  ___ _   _| |__ (_) ___  ___| |_ 
        # / __| | | | '_ \| |/ _ \/ __| __|
        # \__ \ |_| | |_) | |  __/ (__| |_ 
        # |___/\__,_|_.__// |\___|\___|\__|
        #               |__/               
        # """
        """ POP -to-> ASS """
        for u in V:
            p.addConstr( x[u,0] == 1-y[0,u] )
            for i in range(1,H):
                p.addConstr( x[u,i] == y[i-1,u]-y[i,u] )

        """ (*1)  is  redundant, since: 0 <= x[u,i] == y[i-1,u]-y[i,u] """
        # for u in V:
        #     for i in range(H-1): 
        #         p.addConstr( y[i,u] - y[i+1,u] >= 0 )

        """ (*2) chi """
        for u in V:
            for i in range(H):
                p.addConstr( y[ i, chi ] - y[ i, u ] >= 0 )

        """ (*3) """
        for u,v in E:
            p.addConstr( y[0,chi] >= x[u,0] + x[v,0] )
            for i in range(1,H):
                p.addConstr( y[i-1,chi] >= x[u,i] + x[v,i] )

        # (*4)
        for u in G.neighbors(chi):
            for i in range(H-1):
                p.addConstr( y[ i+1, chi ] - y[ i, u ] >= 0 )

        p.optimize()

        if print_solution:
            print_solution_for_check_sol(dominator,H,y)

        print("args:", [ key for key in args if args[ key ] ])
        print(V_0, E_0, len(V), len(E), lb, ub, p.objBound, p.objVal, ('%.1F' % p.runtime), end=' ')
    except:
        import traceback; traceback.print_exc()
        print("args:", [ key for key in args if args[ key ] ])
        print(V_0, E_0, len(V), len(E), lb, ub, "-", "-", ('%.1F' % p.runtime), end=' ')
#}

def print_solution_for_check_sol(dominator,H,y): #{
    """
    This method writes the solution of DIMACS instances such that the program check_sol can validate this solution. 
    DIMACS instances have the col format [1]:

    c Comment: remainder of line ignored.
    p edges |V| |E|

    where |V| is the number of nodes ( to be numbered 1...|V| ) 
    and   |E| the number of edges.
    [1] https://mat.gsia.cmu.edu/COLOR02/#XXHOS

    USE check_sol:
    ~$ ls myciel4.col | vcp | awk -v OFS='\n' '$1 ~ /print_solution_for_check_sol/{$1=""; print}' | sed '/^$/d' > /tmp/temp.sol
    ~$ check_sol -p 1 -i myciel4.col -s /tmp/temp.sol

    """
    try:
        sol = get_solution(dominator,H,y)
        solution=[ sol[str(i)] for i in range(1,len(sol)+1) ]
        print("print_solution_for_check_sol:color(1),...,color(|V|):", " ".join(str(c) for c in solution) )
    except:
        print("print_solution_for_check_sol:color(1),...,color(|V|): EXCEPTION: the VCP instance is not in DIMACS col format, correct col file contains the line 'p edge ||V| |E|' and the nodes must be numbered 1,...,|V|.")
#}

def get_solution(dominator,H,y): #{
    epsilon=0.000000001
    sol={}
    for v in dominator:

        u = dominator[ v ]
        while u != dominator[ u ]:  u = dominator[ u ]

        if abs(y[0,u].x) <= epsilon:
            sol[ u ] = 0+1
        for i in range(1,H):
            if abs( y[i,u].x + (1-y[i-1,u].x) ) <= epsilon:
                sol[ u ] = i+1

        sol[ v ] = sol[ u ]

    return sol
#}
