import networkx as nx
from vcplib import *
import subprocess, time


def color( G, PRINT=8, TLIM=3600, **args ): #{
    """ 
    LANGUAGE: python3
    MODEL:    aymmetric partial ordering based hybrid model POPH-S in [1]
    [1] D.Faber, A.Jabrayilov and P.Mutzel, "SAT Encoding of Partial Ordering Models for Graph Coloring Problems"
    """
    print_solution=False
    UPWARDSEARCH=True
    ASYM=False
    if "print_solution"  in args:   print_solution=args['print_solution']
    if "UPWARDSEARCH"    in args:   UPWARDSEARCH  =args['UPWARDSEARCH']
    if "ASYM"            in args:   ASYM          =args['ASYM']
    print( "args:", [ key for key in args if args[ key ] ])

    V_0 = len(G.nodes())
    E_0 = len(G.edges())

    G,dominator = coloring_preprocessing_fast( G )     

    V = G.nodes()
    E = G.edges()
    if PRINT&8:	print( 'V:', *G.nodes() )       # Vertex order can be used to construct the solution

    H = len(set(nx.greedy_color(G).values()))
    ub = H

    Q = best_clique( G, PRINT )
    lb = len(Q) 

    if lb == ub: 
        rt   = 0
        print( V_0, E_0, len(V), len(E), lb, ub, lb, ub, 'init', end=' ' )
        return 0

    if PRINT&8:	print ( 'Q: ', Q )
    if PRINT&8:	print ( 'degree: ', [G.degree(v) for v in Q] )

    t0 = time.time()
    SAT_FILE_PATH = ("/tmp/vcpsatfile.%s" % time.time_ns())

    try:
        if UPWARDSEARCH:
            print( "linearsearch_upward..." )
            lb2, ub2 =  linearsearch_upward( G, lb, ub, Q, PRINT, TLIM, SAT_FILE_PATH, ASYM )
        else:
            print( "binayr search..." )
            lb2, ub2 =  binarysearch( G, lb, ub, Q, PRINT, TLIM, SAT_FILE_PATH, ASYM )
        print("args:", [ key for key in args if args[ key ] ])
        rt = "%.1f" % (time.time() - t0)
        print(V_0, E_0, len(V), len(E), lb, ub, lb2, ub2, rt, end=" ")
    except:
        import traceback; traceback.print_exc()
        print("args:", [ key for key in args if args[ key ] ])
        rt = "%.1f" % (time.time() - t0)
        print(V_0, E_0, len(V), len(E), lb, ub, "-", "-", rt, end=" ")
#}

def binarysearch( G, lb, ub, Q, PRINT, TLIM, SAT_FILE_PATH, ASYM ): #{
    t0 = time.time()
    tlim = TLIM
    while True: 

        H = int( (lb+ub)/2 )

        is_colorable = iscolorable( G, H, Q, PRINT, tlim, SAT_FILE_PATH, ASYM )
        t_used = time.time() - t0
        tlim = TLIM - t_used      
        print( "lb=%s\t ub=%s\t iscolorable(H=%s)\t exit_code=%s\t t=%.2fs" % (lb,ub,H,is_colorable,t_used) )

        if is_colorable == 10:
            ub = H

        if is_colorable == 20:
            lb = H+1

        if is_colorable == 0:
            break  # exitstatus=0 -> timout

        if lb==ub or int(tlim) <= 0:  # kissat needs a time>=1 in integral seconds
            break

    return lb, ub;
#}

def linearsearch_upward( G, lb, ub, Q, PRINT, TLIM, SAT_FILE_PATH, ASYM ): #{
    t0 = time.time()
    tlim = TLIM
    while lb < ub:

        H = lb
 
        is_colorable = iscolorable( G, H, Q, PRINT, tlim, SAT_FILE_PATH, ASYM )

        t_used = time.time() - t0
        tlim   = TLIM - t_used
        print( "lb=%s\t ub=%s\t iscolorable(H=%s)\t exit_code=%s\t t=%.2fs" % (lb,ub,H,is_colorable,t_used) )

        if is_colorable == 10:
            ub = lb

        if is_colorable == 20:
            lb += 1

        if is_colorable == 0:   # exitstatus=0 -> timout
            break

        if int(tlim) <= 0:      # kissat needs a time>=1 in integral seconds
            break

    return lb, ub;
#}

def iscolorable( G, H, Q, PRINT, TLIM, SAT_FILE_PATH, ASYM ): #{
    """ 
        SAT encoding of POPH for H-colorability
    """
    y = dict()      # POP vars
    x = dict()      # ASS vars
    var=1
    for v in G.nodes():
        for i in range(H):
            y[i,v] = var
            var += 1
    for v in G.nodes():
        for i in range(H):
            x[v,i] = var
            var += 1
    
    cnf_formula = list()

    for i in range( len(Q) ): 
        # y[i,Q[i]].UB = 0
        s = "-%s 0\n" % y[i,Q[i]]
        cnf_formula.append( s )

    """ POP -to-> ASS 
        See [1].
    """
    for v in G.nodes():
        # x[u,0] == 1-y[0,u] 
        s1 =  "-%s -%s 0\n" % (x[v,0], y[0,v])
        s2 =  "%s %s 0\n" % (x[v,0], y[0,v])
        cnf_formula.append( s1 )
        cnf_formula.append( s2 )
        for i in range(1,H): 
            # x[v,i] = y[i-1,v]-y[i,v]
            s1 =  "-%s %s 0\n" % (x[v,i], y[i-1,v])
            s2 =  "-%s -%s 0\n" % (x[v,i], y[i,v])
            s3 =  "%s -%s %s 0\n" % (x[v,i], y[i-1,v], y[i,v])
            cnf_formula.append( s1 )
            cnf_formula.append( s2 )
            cnf_formula.append( s3 )
               
    for v in G.nodes():
        # y[H-1,v].UB = 0
        s = "-%s 0\n" % y[H-1,v] 
        cnf_formula.append( s )

    for u in G.nodes():
        for i in range(H-1): 
            # y[i,u]    -y[i+1,u] >= 0
            s =  "%s -%s 0\n" % (y[i,u], y[i+1,u])
            cnf_formula.append( s )

    for u,v in G.edges():
        for i in range(H):    
            # x[u,i] + x[v,i] <= 1
            s = "-%s -%s 0\n" % ( x[u,i], x[v,i] ) 
            cnf_formula.append( s )

    if ASYM:
        """ 
        Independent-Set Order (ISO) model 2 from [MZ2008]: 
        ============================================
            ISO symmetry breaking is not needed in case H<=|Q|+1, as there is no symmetry: 
            only the last |Q|+1-th color-class is not pinned and cannot be changed with 
            other classes, since the remaining first |Q| color-classes are pinned.
        """
        lenQ = len(Q)
        if H >= lenQ+2:

            print( "iscolorable: ISO constraints used, since  |Q|=%s,  H=%s" % (lenQ, H) )
        
            pi = Q + [v for v,d in sorted(nx.degree(G), key=lambda x: x[1], reverse=True) if v not in Q]
            if PRINT&16:	print ('pi:', pi)

            for h in range(lenQ, H):
                # -y[h,pi[h]] >= 0
                s =  "-%s 0\n" % y[h,pi[h]]
                cnf_formula.append( s )

                for i in range(lenQ+1, len(pi)):
                    # y[h, pi[i] ] <= sum( x[u,h] for u in pi[:i] ) 
                    s = ("-%s "% y[h,pi[i]])   + ' '.join( "%s" % x[u,h]  for u in pi[:i] ) + " 0\n"
                    cnf_formula.append( s )


    print ("p CNF %s %s\n" % (len(G.nodes())*H, len(cnf_formula)) )
    cnf_formula.insert( 0, "p cnf %s %s\n" % (len(G.nodes())*H, len(cnf_formula)) )


    SAT_FILE = open( SAT_FILE_PATH, "w" )
    for i, clause in enumerate(cnf_formula):
        SAT_FILE.write( clause )
        cnf_formula[i]=None                     # clean garbage
    del cnf_formula                             # clean garbage
    SAT_FILE.close()


    process = subprocess.run( ["kissat", "--relaxed", SAT_FILE_PATH, ("--time=%i"%TLIM) ] )
    subprocess.run( ["rm", SAT_FILE_PATH ] )

    return process.returncode
#}
