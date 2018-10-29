import json
import sys
import multiprocessing as mp
import os
import time
import math
import random
from time import sleep
import string
import subprocess
import threading
from client import Client

def rand_val(size):
    return ''.join(random.choices(string.ascii_lowercase+string.digits, k=size))

#Note: This run_client() has been influenced by the code of Soumen's research project
def run_client(config):
    host = config[0][0]
    port = config[0][1]
    fname = config[0][2]
    stream = config[1]
    for msg in stream:
        req_type = msg.split()[0]
        c = Client(host, port)
        start = time.time()
        c.send_data(msg.encode('utf-8'))
        latency = time.time() - start
        c.sock.close()
        with open(fname, 'a') as f:
            f.write(req_type+' '+str(latency)+'\n')
        sleep(0.5)

def get_keys(fname):
    keys = []
    with open(fname, 'r') as f:
        for line in f.readlines():
            keys.append(line.strip('\n'))
    selected_keys = []
    size = math.ceil(len(keys)*0.1)
    for i in random.sample(range(len(keys)), size):
        selected_keys.append(keys[i])
    return selected_keys

def gen_get(key):
    return 'GET '+str(key)+'\n'

def gen_put(key):
    val = rand_val(len(key))
    return 'PUT '+str(key)+' '+val+'\n'

def make_request_streams(conf):
    req_rate = conf['request_rate'] # requests/sec
    duration = conf['duration'] # in seconds
    size = conf['data_size']
    r_ratio = conf['rw_ratio']
    w_ratio = 1 - r_ratio
    tot_reqs = duration*req_rate 
    #Assumption: Each client sends approx 2 requests/sec
    num_clients = math.ceil(req_rate/2)
    #Get the popular 10% keys
    keys = get_keys(conf['keys_file'])
    streams = []
    for c in range(num_clients):
        stream = []
        for i in range(math.ceil(tot_reqs/num_clients)):
            index = random.randint(0, len(keys)-1)
            if random.random()<=r_ratio:
                stream.append(gen_get(keys[index]))
            else:
                stream.append(gen_put(keys[index]))
        streams.append(stream)
    return streams, num_clients

filename = sys.argv[1]
with open(filename) as f:
    conf = json.load(f)
host = conf['server']['ip']
port = conf['server']['port']
j = int(sys.argv[2])
for i in range(1,len(conf['workloads'])):
    outfile = 'out_%s'%(conf['workloads'][j]['id'])
    req_streams, num_clients = make_request_streams(conf['workloads'][j])
    #create j-processes based on conf and stream[j] passed as arg
    pool_args = [[[host, port, outfile], stream] for stream in req_streams]
    with mp.Pool(num_clients) as pool:
        pool.map(run_client, pool_args)
    print("DONE")
    break
