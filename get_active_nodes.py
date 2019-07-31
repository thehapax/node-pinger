from nodelist import public_nodes

from websocket import create_connection as wss_create
from time import time

import multiprocessing as mp
from tqdm import tqdm

max_timeout = 2.0  # max ping time is set to 2
nodelist = public_nodes()


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

    total_nodes = len(nodelist)
    print(f"Polling nodes...total nodes querying: {total_nodes}")
    nodes = get_active_nodes(drop_inactive=True)
    print(" - 100%\n")

    active_nodes = len(nodes)
    if active_nodes > 0:
        print(f"Discovered {active_nodes} out of {total_nodes} Active nodes within {max_timeout}s range: ")
        for i in nodes:
            print(i)
    else:
        print("No active nodes within your range")
