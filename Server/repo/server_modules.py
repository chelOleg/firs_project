import select
import sys
import os
import time
from socket import socket, AF_INET, SOCK_STREAM

from jim.utils import send_message, get_message, adres
from jim.config import *
from jim.core import Jim, JimMessage, JimResponse, JimContactList, JimAddContact, JimDelContact, JimRandomKey, JimSendProfile
from jim.exceptions import WrongInputError, ContactDoesNotExist

import log.server_log_config
import logging
from log.decorators import Log

from repo.base import session, msession
from repo.base_core import Repo, MongoRepo

import hmac
import json

import asyncio

logger = logging.getLogger('server')
log = Log(logger)


class Handler:

    def __init__(self,window = None):
        self.repo = Repo(session)
        self.mrepo = MongoRepo(msession)
        self.window = window
        self.story_base = True

    @log
    def presence_response(self, sock, presence_message):
        print(presence_message)
        presence = Jim.from_dict(presence_message)
        ok = JimResponse(OK)
        error = JimResponse(ACCOUNT_ERROR)
        try:
            username = presence.account_name
            if presence.action == PRESENCE:
                passw = presence.account_passw
                if not self.repo.client_exists(username):
                    self.repo.add_client(username, passw)
                    response = ok
                else:
                    response = error
            elif presence.action == GET_PASSW:
                if self.repo.client_exists(username):
                    send_message(sock,ok.to_dict())
                    not_passw = self.repo.get_passw(username)
                    resp = self.log_in(sock, not_passw)
                    response = JimResponse(resp)
                else:
                    response = error
        except Exception as e:
            response = JimResponse(WRONG_REQUEST, error=str(e))
        finally:
            return response.to_dict(), username

    def log_in(self, client, not_passw):
        messege = os.urandom(32)
        client.send(messege)

        secret_key = not_passw.encode('utf-8')
        hash = hmac.new(secret_key, messege)
        digest = hash.digest()

        response = client.recv(len(digest))
        if hmac.compare_digest(digest, response):
            return OK
        else:
            return ACCOUNT_ERROR

    @log
    def write_responses(self, requests, names, clients):
        for message, sock in requests:
            try:
                print(message)
                action = Jim.from_dict(message)
                if action.action == GET_CONTACTS:
                    contacts = self.repo.get_contacts(action.account_name)
                    response = JimResponse(ACCEPTED, quantity=len(contacts))
                    send_message(sock, response.to_dict())
                    contact_names = [contact.Name for contact in contacts]
                    message = JimContactList(contact_names)
                    send_message(sock, message.to_dict())
                elif action.action == ADD_CONTACT:
                    user_id = action.user_id
                    username = action.account_name
                    try:
                        self.repo.add_contact(username, user_id)
                        response = JimResponse(ACCEPTED)
                        send_message(sock, response.to_dict())
                    except ContactDoesNotExist as e:
                        response = JimResponse(WRONG_REQUEST, error='Такого контакта нет')
                        send_message(sock, response.to_dict())
                elif action.action == DEL_CONTACT:
                    user_id = action.user_id
                    username = action.account_name
                    try:
                        self.repo.del_contact(username, user_id)
                        response = JimResponse(ACCEPTED)
                        send_message(sock, response.to_dict())
                    except ContactDoesNotExist as e:
                        response = JimResponse(WRONG_REQUEST, error='Такого контакта нет')
                        send_message(sock, response.to_dict())

                elif action.action == UPDATE_PROFILE:
                    username = action.account_name
                    info = action.account_info
                    ava_size = action.account_avatar
                    b_avatar = None
                    try:
                        if ava_size:
                            b_avatar = self.getting_image(sock,ava_size)
                        self.repo.edit_profile(username,info,b_avatar)
                        response = JimResponse(ACCEPTED)
                        send_message(sock, response.to_dict())
                    except Exception as e:
                        self.set_error(e)
                elif action.action == GET_PROFILE:
                    username = action.account_name
                    user_id = action.user_id
                    try:
                        avatar, info =self.repo.get_profile(user_id)
                        if avatar:
                            response = JimSendProfile(info,len(avatar))
                            send_message(sock,response.to_dict())
                            sock.send(avatar)
                        else:
                            response = JimSendProfile(info)
                            send_message(sock,response.to_dict())
                    except Exception as e:
                        self.set_error(e)
                        text = "Mongo base disabled \n Storyes don't saving"
                        self.set_text(text)

                elif action.action == GET_STORYES:
                    name = action.account_name
                    if self.story_base:
                        try:
                            friend_name = action.user_id
                            if friend_name == MSG:
                                for story in self.mrepo.get_histories(friend_name):
                                    send_message(sock,story)
                                    time.sleep(0.0025)
                            else:
                                for story in self.mrepo.get_histories(name,friend_name):
                                    send_message(sock,story)
                                    time.sleep(0.0025)
                                    #await asyncio.sleep(1)
                        except Exception as e:
                            text = "Mongo base disabled \n Storyes don't saving"
                            self.story_base = False
                            self.set_error(e)
                            self.set_text(text)
                    else:
                        message = JimMessage(name,'server','story base offline')
                        send_message(sock,message.to_dict())

                elif action.action == MSG:
                    if action.to == MSG:
                        for client in clients:
                            send_message(client, action.to_dict())
                            if self.story_base:
                                self.add_story(action.to_dict())
                    else:
                        try:
                            to = action.to
                            client_sock = names[to]
                            send_message(client_sock, action.to_dict())
                            if self.story_base:
                                self.add_story(action.to_dict())
                        except:
                            to = action.from_
                            from_ = 'server'
                            message ='{} offline'.format(action.to)
                            message = JimMessage(to,from_,message)
                            send_message(sock, message.to_dict())
                elif action.action == IMG:
                    if action.to in names:
                        b_image = self.getting_image(sock,action.message)
                        to = action.to
                        client_sock = names[to]
                        send_message(client_sock, action.to_dict())
                        client_sock.send(b_image)
                    elif action.to == MSG:
                        b_image =self.getting_image(sock,action.message)
                        for client in clients:
                            send_message(client, action.to_dict())
                            client.send(b_image)
                    else:
                        mes = JimResponse(USER_OFFLINE)
                        send_message(sock, mes.to_dict())

            except WrongInputError as e:
                response = JimResponse(WRONG_REQUEST, error=str(e))
                send_message(sock, response.to_dict())
            except Exception as e:
                text ='Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername())
                self.set_error(e)
                self.set_text(text)
                sock.close
                clients.remove(sock)

    def getting_image(self,sock,size):
        mes = JimResponse(ACCEPTED)
        send_message(sock, mes.to_dict())
        b_image = sock.recv(size)
        return b_image

    def add_story(self,story):
        try:
            if self.story_base:
                self.mrepo.add_history(story)
        except Exception as e:
            text = "Mongo base disabled \n Storyes don't saving"
            self.story_base = False
            self.set_error(e)
            self.set_text(text)

    @log
    async def read_requests(self, writers, clients):
        responses = []
        for sock in writers:
            try:
                messege = get_message(sock)
                responses.append((messege, sock))
            except:
                text ='Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername())
                self.set_text(text)
                clients.remove(sock)
        return responses

    def set_error(self,error):
        # if self.window:
        #     window.ErLine.addItem(error)
        # else:
            print(error)

    def set_text(self,text):
        # if self.window:
        #     self.window.InfoWindow.addItem(text)
        # else:
            print(text)

class Server:

    def __init__(self, name, handler):
        self.name = name
        self.handler = handler
        self.server = socket(AF_INET, SOCK_STREAM)
        self.clients = []
        self.names = {}

    @log
    async def connection(self,client):
        while True:
            try:
                presence = get_message(client)
                response, client_name = self.handler.presence_response(client, presence)
                send_message(client, response)
                if response[RESPONSE] == OK:
                    return client_name
            except:
                return ERROR

    # def getting_clients(self, window = None):
    #     try:
    #         client, addr = self.server.accept()
    #         print(client)
    #         client_name = self.connection(client)
    #         if client_name == ERROR:
    #             raise OSError
    #
    #     except OSError as e:
    #         pass
    #     else:
    #         self.clients.append(client)
    #         self.names[client_name] = client
    #         text ='Подключение {}'.format(client_name)
    #         self.handler.set_text(text)

    async def listen(self):
        while True:
            try:
                client, addr = self.server.accept()
                client_name = await self.connection(client)
                if client_name == ERROR:
                    raise OSError

            except OSError as e:
                pass
            else:
                self.clients.append(client)
                self.names[client_name] = client
                text = 'Подключение {}'.format(client_name)
                self.handler.set_text(text)
            finally:
                wait = 0
                w = []
                r = []
                try:
                    w, r, e = select.select(self.clients, self.clients, [], wait)
                except:
                    pass
                requests = await self.handler.read_requests(w, self.clients)
                self.handler.write_responses(requests,self.names, self.clients)

    @Log
    def drop_story_base(self):
        text = self.handler.mrepo.delete_histories()
        self.handler.set_text(text)

    @log
    def start(self):

        self.server.bind(adres())
        self.server.listen(15)
        self.server.settimeout(0.2)
        text ='{} работает'.format(self.name)
        self.handler.set_text(text)
        # qt disainer не работает с асинхронными потоками
        eloop =asyncio.get_event_loop()
        eloop.run_until_complete(self.listen())



