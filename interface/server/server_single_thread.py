import cPickle as pickle
import socket
import threading
import json
import sqlite3
import os
from abc import ABCMeta, abstractmethod, abstractproperty
import datetime
import time            
# OBSERVERVABLE         
class NetworkServerInterface(threading.Thread):
    """
        Class for network connection in another thread
        NetworkServerInterface - Observable object for QueueManager observer
        
        CONSTRUCTOR:
                interface = NetworkServerInterface('2727')
                
        PROPERTIES:
                self.web_port = web_port
                self.observers = []
                
        METHODS:
                def __init__():
                def register():
                def notify_observers():
                def close():
    """
    def __init__(self,web_port):
        threading.Thread.__init__(self)
        self.web_port = web_port
        self.observers = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def run(self):
        self.server_socket.bind(('10.50.70.173', 2727))
        self.server_socket.listen(5)
        while True:
            channel, details = self.server_socket.accept()
            data = channel.recv(1024)
            # a = data.split('::')
            if data:
               self.notify_observers(data)
               if data=='exit':
                    break
    def register(self,observer):
        self.observers.append(observer)
    def notify_observers(self,msg):
        for observer in self.observers:
            observer.recv_message(msg)
    def close(self):
        self.server_socket.close()
        
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
        self.nodes = []
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
        db = DatabaseConnection('C:\grigorev_dv\queue_manager\db.sqlite3')
        SQL_prime = 'SELECT * FROM interface_task WHERE prime ORDER BY date'
        rows = db.get_data_by_query('interface_task',SQL_prime)
        for row in rows:
            # print row
            task = Task(row)
            self.tasks_sorted.append(task)
        SQL_not_prime = 'SELECT * FROM interface_task WHERE NOT prime ORDER BY date'
        rows = db.get_data_by_query('interface_task',SQL_not_prime)
        for row in rows:
            # print row
            task = Task(row)
            self.tasks_sorted.append(task)
            # print task.prime
        db.close()
        
    def define_node(self,task):
        """
            That function defines calc node for the task and returns the 
            Node object
                
        """
        db = DatabaseConnection('C:\grigorev_dv\queue_manager\db.sqlite3')
        #system requirements
        SQL_sr = 'SELECT * FROM interface_node WHERE node_cpu>=%s AND node_ram>=%s AND  NOT in_work'%(task.cpu,task.ram)
        #on user node if it possible
        SQL_user = 'SELECT * FROM interface_node WHERE user_id_id=%s'%task.user_id
        rows_sr = db.get_data_by_query('interface_node',SQL_sr)
        for row in rows_sr:
            print row
        if not(rows_sr):
            return 0
        rows_user = set(db.get_data_by_query('interface_node',SQL_user))
        set_of_nodes = set(rows_sr)&rows_user
        db.close()
        if set_of_nodes:
            node = Node(set_of_nodes.pop())
            if node.check_online(2728):
                node.set_node_inwork('C:\grigorev_dv\queue_manager\db.sqlite3')
            else:
                pass
        else:  
            # for row in rows_sr:
            node = Node(rows_sr.pop(0))
            if node.check_online(2728):
                node.set_node_inwork('C:\grigorev_dv\queue_manager\db.sqlite3')
                # if self.check_node_online(node,2728):
                    # break
            # else:
                # return 0
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
             id,ip = cmd_list[0:2]
             rt_ind = self.get_index_running_by_id(id)
             rt = self.running[rt_ind]
             rt.set_endtime()
             rt.finish_task()
             
             print " Task id=%s finished on node IP %s"%(id,ip)
        elif cmd == 'online':
            param = cmd_list.pop(0)
            print param
        else:
            print "Unknown command"
            pass
        
    def send_task(self,task,node,node_port):
        self.worker_port = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip = str(node.ip)
        db = DatabaseConnection('C:\grigorev_dv\queue_manager\db.sqlite3')
        SQL = "UPDATE interface_task SET status='calculating' WHERE id = %s"%task.id
        db.execute_query(SQL)
        # print node_port
        try:
            self.worker_port.connect ((ip, node_port))
            dumped_task = pickle.dumps(task,2)
            self.worker_port.send(dumped_task)
        except Exception:
            print "Can't connect to calculator server"
            return 0
        finally:
            self.worker_port.close()
            db.close()
            return 1
        
    def get_index_running_by_id(self,task_id):
        length = len(self.running)
        for i in range(0,length):
            if self.running[i].task.id == task_id:
                return id
        else:
            return -1
               
    def check_node_online(self,node,node_port):
        pass
                
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
                       ind = self.tasks_sorted.index(task)
                       self.tasks_sorted.pop(ind)
                       rt = RunningTask(task,node)
                       rt.calc_penalty()
                       # print rt.penalty
                       self.running.append(rt)
                       res = self.send_task(task,node,2728)
                       if res:
                           print 'Task # %s change status to calculating on node %s'%(task.id,node.ip)
                           rt.set_status('calculating')
                       else:
                           print 'error in network connection'
                time.sleep(5) 

class RunningTask:
    def __init__(self,task,node):
        self.task = task
        self.node = node
        self.starttime = datetime.datetime.now()
        self.endtime = datetime.datetime.now()
    def set_endtime(self):
        self.endtime = datetime.datetime.now()
    def calc_bonus(self):
        run_time = self.endtime-self.starttime
        self.bonus = (run_time.total_seconds()/3600)*0.25*self.task.cpu
        return self.bonus
    def set_status(self,status):
        db = DatabaseConnection('C:\grigorev_dv\queue_manager\db.sqlite3')
        SQL = 'UPDATE interface_task SET status=%s WHERE id=%s'%(status,self.task.id)
        db.close()
    def calc_penalty(self):
        pen = 0
        if self.task.prime:
            pen+=-15
        if self.task.moretime:
            pen+=-10
        self.penalty = pen
        db = DatabaseConnection('C:\grigorev_dv\queue_manager\db.sqlite3')
        # db.print_tables()
        #add penalty score
        SQL = 'SELECT score FROM interface_userprofile WHERE user_id_id=%s'%self.task.user_id
        score = db.get_data_by_query('interface_userprofile',SQL)[0][0]+self.penalty
        SQL = 'UPDATE interface_userprofile SET score=%s WHERE user_id_id=%s'%(score,self.task.user_id) 
        db.execute_query(SQL)
        db.close()    
    def finish_task(self):
        #free node
        db = DatabaseConnection('C:\grigorev_dv\queue_manager\db.sqlite3')
        SQL = 'UPDATE interface_node SET in_work=0 WHERE id=%d'%self.node.id
        db.execute_query(SQL)
        #set 'finished' status
        SQL = "UPDATE interface_task SET status='finished' WHERE id=%s"%self.task.id
        db.execute_query(SQL)
        #bonus for calc node owner
        SQL = 'SELECT score FROM interface_userprofile WHERE user_id_id=%s'%self.node.user_id
        score = db.get_data_by_query('interface_userprofile',SQL)[0][0]+self.calc_bonus()
        SQL = 'UPDATE interface_userprofile SET score=%s WHERE user_id_id=%s'%(score,self.node.user_id)
        db.execute_query(SQL)
        db.close()

class Node:
    def __init__(self,cortage):
        self.id = cortage[0]
        self.ip = cortage[1]
        self.in_work = cortage[2]
        self.cpu = cortage[3]
        self.ram = cortage[4]
        self.user_id = cortage[5]
        self.online = cortage[6]
    def set_free_in_db(self,db_name):
        db = DatabaseConnection(db_name)
        SQL = 'UPDATE interface_node SET in_work=0 WHERE id=%s'%self.id
        db.execute_query(SQL)
        db.close()
    def set_node_inwork(self,db_name):
        db = DatabaseConnection(db_name)
        SQL = 'UPDATE interface_node SET in_work=1 WHERE id=%s'%self.id
        db.execute_query(SQL)
        db.close()
    def check_online(self,port):
        try:
            worker_port = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            worker_port.connect ((self.ip, port))
            worker_port.send('ping')
            response = worker.port.recv(1024)
            return 1
        except Exception:
            print 'offline'
            return 0
        finally:
            worker_port.close() 
        # if response:
            # print 'online'
            # return 1       
        # else:
            # print 'offline'
            # return 0
        
    
class Task:
    def __init__(self,cortage):
       self.id = cortage[0]
       self.path = cortage[1]
       self.options = cortage[2]
       self.user_id = cortage[3]
       self.defnode = cortage[4]
       self.moretime = cortage[5]
       self.prime = cortage[6]
       self.cpu = cortage[7]
       self.ram = cortage[8]
       self.status = cortage[9]
       self.date = cortage[10]
       self.node_id = cortage[11]

class DatabaseConnection:
    """
        class for working with SQLite database.
        Constructor:
            database name
            db = DatabaseConnection(db_name)

        Methods:
            -db.get_all_table_data('table_name')
            -db.get_data_by_query('table_name','sql_query')
    """
    def __init__(self,db_name): 
        self.db_name = db_name
        self.db_con = sqlite3.connect(self.db_name)
        
    def get_all_table_data(self,table_name):
        cur = self.db_con.cursor()
        if self.table_exists(table_name):
            SQL = "SELECT * from %s"%table_name
            cur.execute(SQL)
            rows = cur.fetchall()
            return rows
        else:
           return 0
    def execute_query(self,sql_query):
        cur = self.db_con.cursor()
        # try:
        cur.execute(sql_query)
            # return 1
        # except Exception:
            # return 0
    def get_data_by_query(self,table_name,sql_query):
        cur = self.db_con.cursor()
        if self.table_exists(table_name):
            cur.execute(sql_query)
            rows = cur.fetchall()
            return rows
        else:
            return 0
            
    def table_exists(self,name):
        c = self.db_con.cursor()
        SQL = "SELECT * FROM sqlite_master WHERE type='table' AND name='%s'"%name
        c.execute(SQL)
        if len(c.fetchall()) == 0:
            return False
        else:
            return True
    
    def print_tables(self):
        c = self.db_con.cursor()
        SQL = "SELECT * FROM sqlite_master WHERE type='table'"
        rows = c.execute(SQL)
        for row in rows:
            print row
    def close(self):
        self.db_con.commit()
        self.db_con.close()
        

if __name__ == '__main__':
    interface = NetworkServerInterface('2727')
    queue = QueueManager('2728')
    interface.register(queue)
    interface.start()
    queue.start()
    interface.join()
    queue.join()
    # print interface.observers
    # print interface.web_port


    
 