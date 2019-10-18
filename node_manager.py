#!/usr/bin/env python3
from nodelist import public_nodes

from websocket import create_connection as wss_create
from time import time
from tqdm import tqdm
from itertools import repeat
from multiprocessing import freeze_support

import multiprocessing as mp
import platform
import subprocess


max_timeout = 2.0  # max ping time is set to 2s
host = '8.8.8.8'


def ping(host, network_timeout=3):
    """Send a ping packet to the specified host, using the system "ping" command."""
    args = ['ping']
    platform_os = platform.system().lower()

    if platform_os == 'windows':
        args.extend(['-n', '1'])
        args.extend(['-w', str(network_timeout * 1000)])
    elif platform_os in ('linux', 'darwin'):
        args.extend(['-c', '1'])
        args.extend(['-W', str(network_timeout)])
    else:
        raise NotImplemented('Unsupported OS: {}'.format(platform_os))

    args.append(host)

    try:
        if platform_os == 'windows':
            output = subprocess.run(args, check=True, universal_newlines=True).stdout
            if output and 'TTL' not in output:
                return False
        else:
            subprocess.run(args, check=True)

        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def wss_test(node, max_timeout):
    """
    Test websocket connection to a node
    """
    try:
        start = time()
        wss_create(node, timeout=max_timeout)
        latency = (time() - start)
        return latency
    except Exception as e:
        # print(e) # suppress errors
        return None


def check_node(node, timeout):
    """
    check latency of an individual node
    """
    latency = wss_test(node, timeout)
    node_info = {'Node': node, 'Latency': latency}
    return node_info


def get_sorted_nodelist(nodelist, timeout):
    """
    check all nodes and poll for latency, 
    eliminate nodes with no response, then sort  
    nodes by increasing latency and return as a list
    """    
    pool_size = mp.cpu_count()*2
    n = len(nodelist)
    
    with mp.Pool(processes=pool_size) as pool:
        latency_info = list(tqdm(pool.starmap(check_node, zip(nodelist, repeat(timeout))), total=n))

    pool.close()
    pool.join()

    filtered_list = [i for i in latency_info if i['Latency'] is not None]             
    sorted_list = sorted(filtered_list, key=lambda k: k['Latency'])
    sorted_node_list = [i['Node'] for i in sorted_list]

    return sorted_node_list


if __name__ == '__main__':
    freeze_support()

    if ping(host, 1)is False:
        print("internet NOT available! Please check your connection!")    
    else:
        nodelist = public_nodes()
        total_nodes = len(nodelist)

        var = input("Please enter min timeout in ms or Enter for default = 2.0ms :")
        if var is not None:
            max_timeout = var
        else:
            max_timeout = 2.0

        print(f" Your min time out is: {max_timeout} ms")

        print(f"Polling nodes...total nodes querying: {total_nodes}")
        nodes = get_sorted_nodelist(nodelist, max_timeout)

        active_nodes = len(nodes)
        if active_nodes > 0:
            print(f"Discovered {active_nodes} out of {total_nodes} Active nodes within {max_timeout}s range: ")
            for i in nodes:
                print(i)
        else:
            print("No active nodes within your range")

