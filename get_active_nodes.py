from nodelist import public_nodes

from websocket import create_connection as wss_create
from websocket import enableTrace
from time import time, sleep

import multiprocessing as mp
import pandas as pd

max_timeout = 2.0

def pretty_print(df):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        # pretty print entire thing
        print(df)

def wss_test(node):
    """
    Create a websocket connection test
    """
    try:
        start = time()
        rpc = wss_create(node, timeout=max_timeout)
        latency = (time() - start)
        return latency
    except Exception as e:
        # print(e) # suppress errors
        return None


def fetch_node_latency(node):
    name = mp.current_process().name
    node_info = dict()
    latency = wss_test(node)
#    print(f"{name}: {node}, latency: {latency}")
    node_info = {'node': node, 'latency': latency}
    return node_info

        
if __name__ == '__main__':
    
    nodelist = public_nodes()
    pool_size = mp.cpu_count()*2
    latency_info = []
    
    with mp.Pool(processes=pool_size) as pool:
        latency_info = pool.map(fetch_node_latency, nodelist)

    pool.close()
    pool.join()

    print("Active nodes within your range:")
    
    df = pd.DataFrame(latency_info)
    dfc = df.dropna()
    dfc = dfc.sort_values('latency', ascending=True)
    dfc = dfc.reset_index()
    pretty_print(dfc)

    
