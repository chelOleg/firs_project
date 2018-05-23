import os
import sys
import time
from socket import socket, AF_INET, SOCK_STREAM

from repo.client_modules import Client
from jim.utils import send_message, get_message, adres
from jim.config import *

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QThread, pyqtSlot, QCoreApplication
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFileDialog
from handlers import GuiReciever

from PIL import Image, ImageDraw
from PIL.ImageQt import ImageQt

from Filter_pack import mini_picture, set_bits, get_bits, negative, gray, sepia

"""in_window"""
def cr_client():
    login = in_window.CrLogin.text()
    password = in_window.CrPassw.text()
    password_again = in_window.CrPasswII.text()
    if password == password_again:
        client.login = login
        client.password = password
        send_client()
    else:
        error = 'Passwor and Password again must be same'
        in_window.CrText.addItem(error)

def send_client():
    try:
        presence = client.create_presence()
        send_message(client.sock, presence)
        responce = get_message(client.sock)
        responce = client.translate_response(responce)
        if responce['response'] == OK:
            error ='Accept'
            open_chat()
            in_window.close()
        elif responce['response'] == ACCOUNT_ERROR:
            error ='This user name already exist'
        else:
            error = responce
        in_window.CrText.addItem(error)
    except Exception as e:
        in_window.CrText.addItem(e)

def in_client():
    try:
        client.login = in_window.LogLogin.text()
        client.password = in_window.LogPassw.text()
        mes = client.get_passw()
        send_message(client.sock, mes)
        resp = get_message(client.sock)
        if resp[RESPONSE] == OK:
            code = client.sock.recv(32)
            messege = client.hash_resp(code)
            client.sock.send(messege)
            responce = get_message(client.sock)
            responce = client.translate_response(responce)
            if responce[RESPONSE] == OK:
                in_window.LogText.addItem("You're welcome")
                open_chat()
                in_window.close()
            else:
                in_window.LogText.addItem("Wrong password")
        else:
                in_window.LogText.addItem("Wrong login")
    except Exception as e:
        window.CrText.addItem(e)

def in_connect(in_window):
    in_window.CrButton.clicked.connect(cr_client)
    in_window.LogButton.clicked.connect(in_client)
    in_window.ExitButtonII.clicked.connect(QCoreApplication.instance().quit)
    in_window.ExitButtonI.clicked.connect(QCoreApplication.instance().quit)

"""chat_window"""
def load_contacts(contacts):
    chat_window.ContactView.clear()
    chat_window.ContactView.addItem(MSG)
    for contact in contacts:
        chat_window.ContactView.addItem(contact)

def add_contact():
    try:
        username = chat_window.ContactLine.text()
        if username:
            responce = client.add_contact(username)
            print(responce.to_dict())
            if responce.response == ACCEPTED:
                chat_window.ContactView.addItem(username)
            else:
                text='Error {}:{}'.format(responce.response,responce.error)
                chat_window.Rline.setText(text)
    except Exception as e:
        chat_window.Rline.setText(e)

def del_contact():
    try:
        current_item = chat_window.ContactView.currentItem()
        username = current_item.text()
        response = client.del_contact(username)
        if response.response == ACCEPTED:
            current_item = chat_window.ContactView.takeItem(chat_window.ContactView.row(current_item))
            del current_item
        else:
            text = 'Error {}:{}'.format(response.response, response.error)
            chat_window.Rline.setText(text)
    except Exception as e:
        chat_window.Rline.setText(e)

def send_msg():
    selected_index = chat_window.ContactView.currentIndex()
    text = chat_window.MessegeLine.toPlainText()
    if text:
        try:
            user_name = selected_index.data()
            client.send_mes(user_name, text)
            if user_name != client.login and user_name != MSG:
                msg = '{} >> {}'.format(client.login, text)
                chat_window.MessegesView.addItem(msg)
            chat_window.MessegeLine.clear()
        except:
            text ='You must select user'
            chat_window.Rline.setText(text)

def send_img():
    try:
        selected_index = chat_window.ContactView.currentIndex()
        fnames = QFileDialog.getOpenFileName()
        fname = fnames[0]
        user_name = selected_index.data()
        if fname and user_name:
            new_name = 'send_hash.jpg'
            mini_picture(fname,new_name)
            b_image = get_bits(new_name)
            responce = client.send_img(user_name,len(b_image))
            if responce.response == ACCEPTED:
                client.sock.send(b_image)
            elif responce.response == USER_OFFLINE:
                text = 'server >>> {} offline'.format(user_name)
                chat_window.MessegesView.addItem(text)
            os.remove(new_name)
    except Exception as e:
        chat_window.Rline.setText(e)

@pyqtSlot(str)
def update_chat(data):
    try:
        msg = data
        chat_window.MessegesView.addItem(msg)
    except Exception as e:
        chat_window.Rline.setText(e)

@pyqtSlot(bytes)
def show_img(data):
    fname = 'time_hash.jpg'
    set_bits(data,fname)
    try:
        image = Image.open(fname)
        img_tmp = ImageQt(image.convert('RGBA'))
        pixmap = QPixmap.fromImage(img_tmp)
        chat_window.ResImg.setPixmap(pixmap)
        os.remove(fname)
    except Exception as e:
        print(e)

def open_chat():
    th.start()
    chat_window.show()
    contact_list = client.get_contacts()
    chat_window.MyName.setText(client.login)
    load_contacts(contact_list)

def addSmile():
    try:
        chat_window.MessegeLine.textCursor().insertHtml('<img src="%s" />' % 'surprise.gif')
    except Exception as e:
        chat_window.Rline.setText(e)

def get_picture(filter=None):
    try:
        fnames = QFileDialog.getOpenFileName()
        fname = fnames[0]
        image = Image.open(fname)
        image = image.resize((125,125), Image.ANTIALIAS)
        if filter:
            image = filter(image)
        image.save('curr_image.jpg')
        img_tmp = ImageQt(image.convert('RGBA'))
        pixmap = QPixmap.fromImage(img_tmp)
        chat_window.ResImg.setPixmap(pixmap)
    except Exception as e:
        chat_window.Rline.setText(e)

def edit_profile():
    try:
        profile_window.show()
        profile_window.FriendName.setText(client.login)
        client.get_profile(client.login)
    except:
        pass

def load_story():
    try:
        current_item = chat_window.ContactView.currentItem()
        name = current_item.text()
        chat_window.MessegesView.clear()
        client.get_story(name)
    except:
        text = 'You must select user'
        chat_window.Rline.setText(text)

def chat_connect(chat_window):
    chat_window.AddContact.clicked.connect(add_contact)
    chat_window.DelContact.clicked.connect(del_contact)
    chat_window.SendButton.clicked.connect(send_msg)
    chat_window.Img.clicked.connect(send_img)
    chat_window.LoadStory.clicked.connect(load_story)

    chat_window.OpenFile.triggered.connect(get_picture)
    chat_window.FilterSepia.triggered.connect(lambda: get_picture(sepia))
    chat_window.FilterNegative.triggered.connect(lambda: get_picture(negative))
    chat_window.FilterGray.triggered.connect(lambda: get_picture(gray))
    chat_window.EditProfile.triggered.connect(edit_profile)
    chat_window.Smile.triggered.connect(addSmile)
    chat_window.ContactView.itemDoubleClicked.connect(get_profile)

"""Profile_window"""
def profile_update():
    try:
        fname = 'ava_hash.jpg'
        avatar = get_bits(fname)
        info = profile_window.MyInfo.toPlainText()
        if avatar:
            response = client.update_profile(info,len(avatar))
            if response.response == ACCEPTED:
                client.sock.send(avatar)
                text = client.get_responce()
            else:
                text = 'no answer from server'
        elif info:
            response = client.update_profile(info)
            text = response.response
        else:
            thext = 'change something'
        profile_window.ErLine.setText(text)
    except Exception as e:
        profile_window.ErLine.setText(e)

def load_avatar():
    fnames = QFileDialog.getOpenFileName()
    fname = fnames[0]
    if fname:
        new_name = 'ava_hash.jpg'
        try:
            os.remove(new_name)
        except:
            pass
        mini_picture(fname, new_name,150,150)
        image = Image.open(new_name)
        img_tmp = ImageQt(image.convert('RGBA'))
        pixmap = QPixmap.fromImage(img_tmp)
        profile_window.MyAvatar.setPixmap(pixmap)

def get_profile():
    try:
        profile_window.show()
    except:
        pass
    current_item = chat_window.ContactView.currentItem()
    name = current_item.text()
    client.get_profile(name)
    profile_window.FriendName.setText(name)

@pyqtSlot(str)
def info_load(data):
    profile_window.ProfileVeiw.clear()
    if data:
        try:
            profile_window.ProfileVeiw.addItem(data)
        except Exception as e:
            profile_window.ErLine.setText(e)

@pyqtSlot(bytes)
def ava_load(data):
    if data:
        fname = 'ava2_hash.jpg'
        set_bits(data, fname)
        try:
            image = Image.open(fname)
            img_tmp = ImageQt(image.convert('RGBA'))
            pixmap = QPixmap.fromImage(img_tmp)
            profile_window.Avatar.setPixmap(pixmap)
            os.remove(fname)
        except Exception as e:
            profile_window.ErLine.setText(e)

def profile_connect(profile_window):
    profile_window.LoadButton.clicked.connect(load_avatar)
    profile_window.SaveButton.clicked.connect(profile_update)

"""listner"""
def listener_connect(listener):
    listener.gotAva.connect(ava_load)
    listener.gotInfo.connect(info_load)
    listener.gotData.connect(update_chat)
    listener.gotPic.connect(show_img)

if __name__ == '__main__':
    s = socket(AF_INET, SOCK_STREAM)
    s.connect(adres())

    client = Client(s)

    app = QtWidgets.QApplication(sys.argv)
    listener = GuiReciever(client.sock, client.request_queue)

    in_window = uic.loadUi('qLogin_window.ui')
    chat_window = uic.loadUi('qTable.ui')
    profile_window = uic.loadUi('qProfile.ui')

    th = QThread()
    listener.moveToThread(th)
    th.started.connect(listener.poll)

    listener_connect(listener)
    in_connect(in_window)
    chat_connect(chat_window)
    profile_connect(profile_window)

    in_window.show()

    sys.exit(app.exec_())