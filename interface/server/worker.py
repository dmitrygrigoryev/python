import socket
import json
# import sqlite3
import os
import re
import cPickle as pickle
import subprocess
import time
import queue_models as qm

def send_result(server_ip,server_port,task_id,worker_ip,result):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip,server_port))
    client.send('finish %s %s %s'%(task_id,worker_ip,result))
    client.close()
    
def send_cmd(server_ip,server_port,worker_ip,worker_port):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((server_ip,server_port))
        client.send('online %s:%s'%(worker_ip,worker_port))
    finally:
        client.close()
    
def register_node(server_ip,server_port,worker_ip,worker_port):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((server_ip,server_port))
        client.send('online %s:%s'%(worker_ip,worker_port))
        return 1
    except Exception:
        print "Can't connect to QueueManager"
        return 0
    finally:
        client.close()
    
def configure_worker():
    print socket.gethostbyname_ex(socket.gethostname())[2][0]
def get_def(project_dir):
    files = os.listdir(project_dir)
    defs = filter(lambda x: x.endswith('.def'), files)
    return defs[0]
    
def start_CFX(task):
    CFXROOT = os.environ['AWP_Root150']+'\\CFX\\bin\\'
    print task.options
    par = []
    options = json.loads(task.options)
    print options
    # print options['-ccl']
    cmd = []
    cmd.append(CFXROOT+'cfx5solve')
    cmd.append(['-chdir ',task.path])
    # cmd.append(task.path)
    deffile = get_def(task.path)
    cmd.append(["-def ",deffile])
    # cmd.append(["-par-local",''])
    # cmd.append(["-norun"])
    # if not task.moretime:
        # cmd.append(["-maxet ","\"3 [hr]\""])
    for key in options:
        # par = list(key+" ",options[key]+" ")
        if key=='-par-local':
            cmd.append(["-par-local",''])
            continue
        par.append(" "+key)
        par.append(" "+options[key])
        cmd.append(par)
        par = []
        # cmd.append(par)
    print cmd
    result = subprocess.call(cmd)
    print result
    return result
    
def check_license(name):
    p = subprocess.check_output("C:\\Program Files\\ANSYS Inc\\Shared Files\\Licensing\\winx64\\ansysli_util.exe -printavail", shell=False,universal_newlines=True)
    a = map(lambda x:''.join(x), p.split('\n'))
    lic_hash = {}
    lic_list = []
    for line in a:
       # print line
       a = line.strip()
       a = a.replace(" ","")
       b = a.split(':')
       if b[0] in [r'NAME',r'COUNT',r'USED']:
           lic_list.append(b)   
    a = len(lic_list)
    lic_test = {}
    
    for i in range(0,a,3):
        lic_name = lic_list[i][1]
        lic_cnt = lic_list[i+1][1]
        lic_used = lic_list[i+2][1]
        keys = lic_hash.keys()
        if not(lic_name in keys):
            lic_hash[lic_name] = {'cnt':lic_cnt,'used':lic_used}
        else:
            cnt = int(lic_hash[lic_name]['cnt']) + int(lic_cnt)
            lic_hash[lic_name] = {'cnt':cnt,'used':lic_used}        
    print lic_hash[name]
    return int(lic_hash[name]['cnt'])-int(lic_hash[name]['used'])

if __name__=='__main__':    
    worker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # worker_ip = unicode(socket.gethostbyname_ex(socket.gethostname())[2][0])
    worker_ip = '10.50.70.173'
    worker_port = 2728
    worker.bind((worker_ip, worker_port))
    worker.listen(2)
    manager_ip = '10.50.70.173'
    manager_port = 2727
    registred = register_node(manager_ip,manager_port,worker_ip,worker_port)
    print worker_ip
    while True:
        channel, details = worker.accept()
        data = channel.recv(1024)
        # channel.send('response')
        if data == 'ping':
            send_cmd(manager_ip,manager_port,worker_ip,worker_port)
            continue
        data_unpack = pickle.loads(data)
        print data_unpack
        options = json.loads(str(data_unpack.options))
        if data_unpack:
            if check_license('acfd'):
                res = start_CFX(data_unpack)
            else:
                time.sleep(5)
                continue
            print data_unpack
            send_result(manager_ip,manager_port,data_unpack.id,worker_ip,str(res))
    worker.close()
    # 89060738230