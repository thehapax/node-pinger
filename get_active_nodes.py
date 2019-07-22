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
        print(df.to_string(index=False))

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
    #print(f"{name}: {node}, latency: {latency}")
    print('#', end='', flush=True)
    node_info = {'Node': node, 'Latency': latency}
    return node_info


def get_active_nodes():
    nodelist = public_nodes()
    pool_size = mp.cpu_count()*2
    latency_info = []

    with mp.Pool(processes=pool_size) as pool:
        latency_info = pool.map(fetch_node_latency, nodelist)

    pool.close()
    pool.join()
    
    df = pd.DataFrame(latency_info)
    dfc = df.dropna()
    dfc = dfc.sort_values('Latency', ascending=True)
    return dfc

        
if __name__ == '__main__':

    print("Polling nodes...")
    df = get_active_nodes()
    print(" - 100%\n")

    if df.empty == False:
        print("Active nodes within your range:")    
        pretty_print(df)
    else:
        print("No active nodes within your range")
