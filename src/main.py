import networkx as nx
import os, sys
import vcplib

degrP=False
ASYM=True
UPWARDSEARCH=True
TIME_LIMIT=3600

if __name__ == '__main__':
    model = sys.argv[ 1 ] 
    graph = sys.argv[ 2 ] 

    for par in sys.argv:
        if par=="DEGRP":
            degrP=True
        elif par=="ASYM":
            ASYM=True
        elif par=="BINARYSEARCH":
            UPWARDSEARCH=False
        elif par.split('=')[0]=='t':
            TIME_LIMIT=int(par.split('=')[1])
    
    extension = os.path.splitext( graph )[1]

    if extension == '.col':
        print_solution=True
        G = vcplib.dimacscol_to_networkxgraph( graph )
    elif extension == '.gml':
        G = nx.read_gml( graph ) 
        print_solution=False
    elif extension == '.graphml':
        G = nx.read_graphml( graph ) 
        print_solution=False
    else:
        print("Unknown graph file format detected: '%s'." % extension)
        sys.exit(2)

    if model == "vcp_pop2.py":
        from vcp_pop2 import *
        color(G,PRINT=9,TLIM=TIME_LIMIT,degrP=degrP,print_solution=print_solution ); print( graph )

    elif model == "vcp_poph2.py":
        from vcp_poph2 import *
        color(G,PRINT=9,TLIM=TIME_LIMIT,degrP=degrP,print_solution=print_solution ); print( graph )

    elif model == "vcp_pop_sat.py":
        from vcp_pop_sat import *
        color(G,PRINT=9,TLIM=TIME_LIMIT,UPWARDSEARCH=UPWARDSEARCH,ASYM=ASYM); print( graph )

    elif model == "vcp_poph_sat.py":
        from vcp_poph_sat import *
        color(G,PRINT=9,TLIM=TIME_LIMIT,UPWARDSEARCH=UPWARDSEARCH,ASYM=ASYM); print( graph )
