from nodelist import public_nodes

from websocket import create_connection as wss_create
from websocket import enableTrace
from time import time, sleep

import multiprocessing as mp
from tqdm import tqdm

max_timeout = 2.0 # max ping time is set to 2

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
    node_info = {'Node': node, 'Latency': latency}
    return node_info


def get_active_nodes(drop_inactive=True):
    nodelist = public_nodes()
    pool_size = mp.cpu_count()*2
    n = len(nodelist)

    with mp.Pool(processes=pool_size) as pool:
        latency_info = list(tqdm(pool.imap(fetch_node_latency, nodelist), total=n))

    pool.close()
    pool.join()

    if drop_inactive:
        filtered_list = [i for i in latency_info if i['Latency'] is not None]
    else:
        filtered_list = latency_info
        
    sorted_list = sorted(filtered_list, key=lambda k: k['Latency'])
    sorted_node_list = [i['Node'] for i in sorted_list]

    return sorted_node_list

        
if __name__ == '__main__':

    print("Polling nodes...")
    nodes = get_active_nodes(drop_inactive=True)
    print(" - 100%\n")

    if len(nodes) > 0:
        print("Active nodes within your range:")            
        for i in nodes:
            print(i)
    else:
        print("No active nodes within your range")
