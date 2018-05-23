from socket import socket, AF_INET, SOCK_STREAM
from jim.utils import send_message, get_message
from jim.config import *
import time

from jim.core import JimPresence, JimMessage, Jim, JimResponse, JimDelContact, JimAddContact, JimContactList,\
    JimGetContacts, JimRandomKey, JimGetPassw, JimPicture, JimProfileUpdate, JimGetProfile, JimGetStory

from threading import Thread

import  hashlib
import hmac

from queue import Queue



class Client:

    def __init__(self, sock,login='guest',password=None):
        self.login = login
        self.sock = sock
        self.password = password
        self.contacts = []
        self.request_queue = Queue()
    """Модули для интерфейса"""
    def get_contacts(self):
        jimmessage = JimGetContacts(self.login)
        send_message(self.sock, jimmessage.to_dict())
        response = self.request_queue.get()
        response.quantity
        massege = self.request_queue.get()
        contacts = massege.user_id
        return contacts

    def add_contact(self,username):
        message = JimAddContact(self.login, username)
        send_message(self.sock, message.to_dict())
        response = self.request_queue.get()
        return response

    def del_contact(self,username):
        message = JimDelContact(self.login, username)
        send_message(self.sock, message.to_dict())
        response = self.request_queue.get()
        print(response)
        return response

    def send_mes(self,to,text):
        message = JimMessage(to, self.login, text)
        send_message(self.sock, message.to_dict())

    def send_img(self,to,img_size):
        message = JimPicture(to, self.login, img_size)
        send_message(self.sock, message.to_dict())
        response = self.request_queue.get()
        return response

    def update_profile(self,info,ava_size):
        message = JimProfileUpdate(self.login,info,ava_size)
        send_message(self.sock, message.to_dict())
        response = self.request_queue.get()
        return response

    def get_responce(self):
        try:
            resp = self.request_queue.get()
            print(resp)
            responce = resp.response
        except:
            responce = 'No answer from server'
        return responce

    def get_profile(self,name):
        message = JimGetProfile(self.login,name)
        send_message(self.sock,message.to_dict())

    def get_story(self,name):
        message = JimGetStory(self.login, name)
        send_message(self.sock, message.to_dict())
        print(message.to_dict())

    """Модули для терминала"""

    def create_presence(self):
        # Сообщение имени
        jim_presence = JimPresence(self.login, self.password)
        messege = jim_presence.to_dict()
        return messege

    def get_passw(self):
        jim_passw=JimGetPassw(self.login)
        messege = jim_passw.to_dict()
        return  messege

    def translate_response(self, response):
        """
        Разбор сообщения
        :param response: Словарь ответа от сервера
        :return: корректный словарь ответа
        """
        result = Jim.from_dict(response)
        # возвращаем от
        return result.to_dict()

    def create_message(self, message_to, text):
        #Сообщение кому то
        message = JimMessage(message_to, self.login, text)
        return message.to_dict()

    def read_messages(self):
        while True:
            message = get_message(self.sock)
            try:
                if FROM in message:
                    print('{}:{}'.format(message[FROM],message[MESSAGE]))
                elif RESPONSE in message:
                    print(message[RESPONSE])
                elif CONTACT_LIST in message:
                    self.contacts.append(message[CONTACT_LIST])
                    print(message[CONTACT_LIST])
            except:
                print(message)

    def write_messages(self):
        while True:
            text = input(':)>')
            if text.startswith('list'):
                jimmessage = JimGetContacts(self.login)
                send_message(self.sock, jimmessage.to_dict())
            else:
                command, param = text.split()
                if command == 'add':
                    message = JimAddContact(self.login, param)
                    send_message(service, message.to_dict())
                elif command == 'del':
                    message = JimDelContact(self.login, param)
                    send_message(service, message.to_dict())
                elif command == MSG:
                     messege = JimMessage(command,self.login,param)
                     print(messege.to_dict())
                     send_message(service,messege.to_dict())

    def create_person(self):

        while True:
            login= input('login')
            passw = input('passw')
            passw_again= input('passw_again')
            if passw == passw_again and passw!=None:
                self.login = login
                self.password = passw
                break
            else:
                print('Incorrect passsword')

    def send_person(self):
        while True:
            self.create_person()
            presence = self.create_presence()
            send_message(self.sock, presence)
            responce = get_message(self.sock)
            responce = self.translate_response(responce)
            if responce['response'] == OK:
                print('профиль добавлен')
                break
            elif responce['response'] == ACCOUNT_ERROR:
                print('Такой пользователь уже есть')
            else:
                print(responce)

    def log_in(self):
        while True:
            self.login = input('login')
            self.password = input('password')
            mes = self.get_passw()
            print(mes)
            send_message(self.sock,mes)
            resp = get_message(self.sock)
            if resp[RESPONSE] == OK:
                code = self.sock.recv(32)
                messege = self.hash_resp(code)
                self.sock.send(messege)
                responce = get_message(self.sock)
                responce = self.translate_response(responce)
                if responce[RESPONSE] == OK:
                    print('ok')
                    break
            else:
                print(resp[RESPONSE])

    def hash_resp(self,keyword):
        passw = self.password.encode('utf-8')
        hash = hmac.new(passw, keyword)
        digest = hash.digest()
        return digest

    def start(self):
        run = input('Войти или содать in/cr')
        if run == 'cr':
            self.send_person()
        elif run == 'in':
            self.log_in()
        try:
            a =self.get_contacts()
            print(a)
        except Exception as e:
            print(e)
        listener = Thread(target=self.read_messages)
        listener.daemon = False
        writer= Thread(target=self.write_messages)
        writer.daemon = True

        writer.start()
        listener.start()


