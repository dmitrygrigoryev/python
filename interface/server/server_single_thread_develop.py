import cPickle as pickle
import socket
import threading
import json
import subprocess
# import sqlite3
# import os
# from abc import ABCMeta, abstractmethod, abstractproperty
# import datetime
import time
import NetworkServerInterface
import queue_models as qm
import database_connector as db_con            
        
# OBSERVER
class QueueManager(threading.Thread):
    """
        QueueManager - class for work with queue
        CONSTRUCTOR:
            - queue = QueueManager('2728',database)
        PROPERTIES:
            self.db = db
            self.nodes = []
            self.tasks = []
            self.tasks_sorted = []
            self.register_nodes()
            self.render_queue()
        METHODS:
            def register_nodes(self):
            def render_queue(self):
            def recv_message(self,msg):
            def run(self):
    """
    def __init__(self,worker_port):
        threading.Thread.__init__(self)
        db = db_con.DatabaseConnection('C:\grigorev_dv\queue_manager\db.sqlite3')
        # SQL = 'SELECT * FROM interface_node'
        node_rows = db.get_all_table_data('interface_node')
        self.nodes = []
        for node_row in node_rows:   
            self.nodes.append(qm.Node(node_row))
        self.tasks = []
        self.tasks_sorted = []
        # self.register_nodes()
        self.render_queue()
        self.running = []
        
    def render_queue(self):
        """
            Function for render the queue by priority options
            Push the 'prime' calcs at the begin of queue
        """
        db = db_con.DatabaseConnection('C:\grigorev_dv\queue_manager\db.sqlite3')
        SQL_prime = "SELECT * FROM interface_task WHERE prime AND status='in queue' ORDER BY date"
        rows = db.get_data_by_query('interface_task',SQL_prime)
        for row in rows:
            # print row
            task = qm.Task(row)
            self.tasks_sorted.append(task)
        SQL_not_prime = "SELECT * FROM interface_task WHERE NOT prime AND status='in queue' ORDER BY date"
        rows = db.get_data_by_query('interface_task',SQL_not_prime)
        for row in rows:
            # print row
            task = qm.Task(row)
            self.tasks_sorted.append(task)
            # print task.prime
        db.close()
        
    def define_node(self,task):
        """
            That function defines calc node for the task and returns the 
            Node object
                
        """
        db = db_con.DatabaseConnection('C:\grigorev_dv\queue_manager\db.sqlite3')
        #system requirements
        # db.print_tables()
        SQL_sr = "SELECT * FROM interface_node WHERE node_cpu>=%s AND node_ram>=%s AND online"%(task.cpu,task.ram)
        rows_sr = db.get_data_by_query('interface_node',SQL_sr)
        print rows_sr
        nodes = []
        for row in rows_sr:
            nodes.append(qm.Node(row))
        print nodes
        print rows_sr
        #on user node if it possible
        SQL_user = 'SELECT * FROM interface_node WHERE user_id_id=%s'%task.user_id
        rows_user = set(db.get_data_by_query('interface_node',SQL_user))
        print "LSLFLKJSLK"
        print rows_user
        if not(rows_sr):
            return 0
        set_of_nodes = set(rows_sr)&rows_user
        db.close()
        if set_of_nodes:
            node = qm.Node(set_of_nodes.pop())
            if node.check_online(2728):
                node.set_node_inwork('C:\grigorev_dv\queue_manager\db.sqlite3')
            else:
                node.set_node_online('C:\grigorev_dv\queue_manager\db.sqlite3',False)
                # pass
        else:  
            for row in rows_sr:
                node = qm.Node(rows_sr.pop(0))
                if node.check_online(2728):
                    node.set_node_inwork('C:\grigorev_dv\queue_manager\db.sqlite3')
                    break
                else:
                    node.set_node_online('C:\grigorev_dv\queue_manager\db.sqlite3',False)
                    continue
                # if self.check_node_online(node,2728):
                    # break
            # else:
                # return 0
        print node.ip   
        if node:
            return node
        else:
            return 0
       
    def recv_message(self,msg): 
        """
            Receives messages from server network interface/
        """
        cmd_list = msg.split()
        cmd = cmd_list.pop(0)
        if cmd == 'update':
            param = cmd_list.pop(0)
            if param == 'tasks':
                self.render_queue()
            elif param == 'nodes':
                self.register_nodes()
        elif cmd == 'finish':
             # param = cmd_list.pop(0)
             id,ip,res = cmd_list[0:3]
             rt_ind = self.get_index_running_by_id(id)
             rt = self.running[rt_ind]
             rt.set_endtime()
             rt.finish_task()
             
             print " Task id=%s finished on node IP %s with exit code %s"%(id,ip,res)
        elif cmd == 'online':
            param = cmd_list.pop(0)
            ip,port = param.split(':')
            # print ip,port
            self.set_node_online(ip)
        else:
            print "Unknown command"
            pass
            
    def set_node_online(self,node_ip):
        db = db_con.DatabaseConnection('C:\grigorev_dv\queue_manager\db.sqlite3')
        stroka = unicode(node_ip)
        SQL = "SELECT id FROM interface_node WHERE node_ip=%r"%node_ip
        node_id = db.get_data_by_query('interface_node',SQL)[0][0]
        # print node_id
        SQL = 'UPDATE interface_node SET online=1 WHERE id=%s'%node_id
        db.execute_query(SQL)
        # print row
        db.close()
        # print "Node IP %s registred"%node_ip
        
    def send_task(self,task,node,node_port):
        self.worker_port = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip = str(node.ip)
        options = json.loads(task.options)
        if not task.moretime:
            options['-maxet'] = "\"3 [hr]\""
            task.options = json.dumps(options)
        if task.cpu>1:
            if not("-parfile-read" in options.keys()):
                options["-part"] =str(task.cpu)
            options["-par-local"] = ''
        try:
            self.worker_port.connect ((ip, node_port))
            #edit task for multicore start CFX
            # print task.options
            # options = json.loads(task.options)
            print options
            task.options = json.dumps(options)
            dumped_task = pickle.dumps(task,2)
            self.worker_port.send(dumped_task)
        except Exception:
            print "Can't connect to calculator server"
            return 0
        finally:
            self.worker_port.close()
            # db.close()
            return 1
    def check_license(self,name):
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
    def get_index_running_by_id(self,task_id):
        length = len(self.running)
        for i in range(0,length):
            if self.running[i].task.id == task_id:
                return id
        else:
            return -1
                
    def run(self):
         """
             Main cycle of QueueManager
             Shift tasks from the top of queue and send it to the workers
         """

         while True:
            if self.tasks_sorted:
                for task in self.tasks_sorted:
                    node = self.define_node(task)
                    if node:
                       if self.check_license('acfd'): 
                           ind = self.tasks_sorted.index(task)
                           self.tasks_sorted.pop(ind)
                           rt = qm.RunningTask(task,node)
                           rt.calc_penalty()
                           print node.ip
                           self.running.append(rt)
                           res = self.send_task(task,node,2728)
                           if res:
                               print 'Task # %s change status to calculating on node %s'%(task.id,node.ip)
                               rt.set_status('calculating')
                           else:
                               print 'error in network connection'
                    else:
                        print "slonopotams otake"
                time.sleep(5)         
            else:
                for node in self.nodes:
                    if not(node.check_online(2728)):
                       node.set_node_online('C:\grigorev_dv\queue_manager\db.sqlite3',False)
                    else:
                       node.set_node_online('C:\grigorev_dv\queue_manager\db.sqlite3',True)
                time.sleep(5)
       

if __name__ == '__main__':
    interface = NetworkServerInterface.NetworkServerInterface('2727')
    queue = QueueManager('2728')
    interface.register(queue)
    interface.start()
    queue.start()
    interface.join()
    queue.join()


    
 