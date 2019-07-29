from nodelist import public_nodes

from websocket import create_connection as wss_create
from time import time
import multiprocessing as mp
from tqdm import tqdm
from urllib.request import urlopen

max_timeout = 2.0 # max ping time is set to 2

def internet_on():
    try:
        urlopen('http://8.8.8.8', timeout=2)
        return True
    except:
        return False


def wss_test(node):
    """
    Test websocket connection to a node
    """
    try:
        start = time()
        rpc = wss_create(node, timeout=max_timeout)
        latency = (time() - start)
        return latency
    except Exception as e:
        # print(e) # suppress errors
        return None


def check_node(node):
    """
    check latency of an individual node
    """
    node_info = dict()
    latency = wss_test(node)
    node_info = {'Node': node, 'Latency': latency}
    return node_info


def get_sorted_nodelist(nodelist):
    """
    check all nodes and poll for latency, 
    eliminate nodes with no response, then sort  
    nodes by increasing latency and return as a list
    """    
    pool_size = mp.cpu_count()*2
    n = len(nodelist)
    
    with mp.Pool(processes=pool_size) as pool:
        latency_info = list(tqdm(pool.imap(check_node, nodelist), total=n))

    pool.close()
    pool.join()

    filtered_list = [i for i in latency_info if i['Latency'] is not None]             
    sorted_list = sorted(filtered_list, key=lambda k: k['Latency'])
    sorted_node_list = [i['Node'] for i in sorted_list]

    return sorted_node_list


if __name__ == '__main__':

    if internet_on() is False:
        print("internet NOT available! Please check your connection!")    
    else:    

        nodelist = public_nodes()    
        print("Polling nodes...")
        nodes = get_sorted_nodelist(nodelist)
        print(" - 100%\n")
    
        if len(nodes) > 0:
            print("Active nodes within your range:")            
            for i in nodes:
                print(i)
        else:
            print("No active nodes within your range")

