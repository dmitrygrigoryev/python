import datetime
import database_connector as db_con
import socket
class Task(object):
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
       
class Node(object):
    def __init__(self,cortage):
        self.id = cortage[0]
        self.ip = cortage[1]
        self.in_work = cortage[2]
        self.user_id = cortage[3]
        self.cpu = cortage[4]
        self.ram = cortage[5]
        self.online = cortage[6]
    def set_free_in_db(self,db_name):
        db = db_con.DatabaseConnection(db_name)
        SQL = 'UPDATE interface_node SET in_work=0 WHERE id=%s'%self.id
        db.execute_query(SQL)
        db.close()
    def set_node_inwork(self,db_name):
        db = db_con.DatabaseConnection(db_name)
        SQL = 'UPDATE interface_node SET in_work=1 WHERE id=%s'%self.id
        db.execute_query(SQL)
        db.close()
    def set_node_online(self,db_name,status):
        db = db_con.DatabaseConnection(db_name)
        if status:
            SQL = 'UPDATE interface_node SET online=1 WHERE id=%s'%self.id
        else:
            SQL = 'UPDATE interface_node SET online=0 WHERE id=%s'%self.id
        db.execute_query(SQL)
        db.close()   
    def check_online(self,port):
        try:
            worker_port = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            worker_port.connect ((self.ip, port))
            worker_port.send('ping')
            response = worker.port.recv(1024)
            if response:
                print response
            worker_port.close() 
            return 1
        except Exception:
            # print 'offline'
            worker_port.close() 
            return 0
        finally:
            worker_port.close() 
            
class RunningTask(object):
    def __init__(self,task,node):
        self.task = task
        self.node = node
        self.starttime = datetime.datetime.now()
        self.endtime = datetime.datetime.now()
        db = db_con.DatabaseConnection('C:\grigorev_dv\queue_manager\db.sqlite3')
        SQL = 'UPDATE interface_node SET in_work=1 WHERE id=%d'%self.node.id
        db.execute_query(SQL)
        db.close()
    def set_endtime(self):
        self.endtime = datetime.datetime.now()
    def calc_bonus(self):
        run_time = self.endtime-self.starttime
        self.bonus = (run_time.total_seconds()/3600)*0.25*self.task.cpu
        return self.bonus
    def set_status(self,status):
        db = db_con.DatabaseConnection('C:\grigorev_dv\queue_manager\db.sqlite3')
        SQL = "UPDATE interface_task SET status='calculating' WHERE id=%s"%self.task.id
        db.execute_query(SQL)
        db.close()
    def calc_penalty(self):
        pen = 0
        if self.task.prime:
            pen+=-15
        if self.task.moretime:
            pen+=-10
        self.penalty = pen
        db = db_con.DatabaseConnection('C:\grigorev_dv\queue_manager\db.sqlite3')
        # db.print_tables()
        #add penalty score
        SQL = 'SELECT score FROM interface_userprofile WHERE user_id_id=%s'%self.task.user_id
        score = db.get_data_by_query('interface_userprofile',SQL)[0][0]+self.penalty
        print score
        SQL = 'UPDATE interface_userprofile SET score=%s WHERE user_id_id=%s'%(score,self.task.user_id) 
        db.execute_query(SQL)
        db.close()    
    def finish_task(self):
        #free node
        print self.node.user_id
        db = db_con.DatabaseConnection('C:\grigorev_dv\queue_manager\db.sqlite3')
        rows = db.get_all_table_data('interface_node')
        for row in rows:
            print row
        SQL = 'UPDATE interface_node SET in_work=0 WHERE id=%d'%self.node.id
        db.execute_query(SQL)
        #set 'finished' status
        SQL = "UPDATE interface_task SET status='finished' WHERE id=%s"%self.task.id
        db.execute_query(SQL)
        #bonus for calc node owner
        print self.node.user_id
        SQL = 'SELECT score FROM interface_userprofile WHERE user_id_id=%s'%self.node.user_id
        score = db.get_data_by_query('interface_userprofile',SQL)[0][0]+self.calc_bonus()
        print score
        SQL = 'UPDATE interface_userprofile SET score=%s WHERE user_id_id=%s'%(score,self.node.user_id)
        db.execute_query(SQL)
        db.close()
        
