# from jim.protocol import JimMessage, JimResponse
# from jim.errors import MandatoryKeyError
from jim.config import MESSAGE
from PyQt5.QtCore import QObject, pyqtSignal
from jim.utils import get_message
from jim.core import Jim, JimResponse, JimMessage, JimPicture, JimSendProfile
from jim.exceptions import WrongParamsError, ToLongError, WrongActionError, WrongDictError, ResponseCodeError
from jim.config import *


class Receiver:
    ''' Класс-получатель информации из сокета
    '''

    def __init__(self, sock, request_queue):
        # запоминаем очередь ответов
        self.request_queue = request_queue
        # запоминаем сокет
        self.sock = sock
        self.is_alive = False

    def process_message(self, message):
        """метод для обработки принятого сообщения, будет переопределен в наследниках"""
        pass

    def process_pictures(self, message):
        pass

    def poll(self):
        self.is_alive = True
        while True:
            if not self.is_alive:
                break
            data = get_message(self.sock)
            try:
                # Преобразуем словарь в Jim, Это может быть action, а может быть response
                jm = Jim.from_dict(data)

                # Если это сообщение
                if isinstance(jm, JimMessage):
                    self.process_message(jm)
                elif isinstance(jm,JimPicture):
                    self.process_pictures(jm)
                elif isinstance(jm,JimSendProfile):
                    self.process_profiles(jm)
                else:
                    # Это либо ответ от сервера либо действия с контактами
                    # мы это складываем в очередь
                    self.request_queue.put(jm)
            except Exception as e:
                # Ошбики быть не должно так как сервер отправлять верные данные
                # но лучше этот случай все равно обработать
                # выведем ошибку, но лучше писать в будующем в log
                print(e)


    def stop(self):
        self.is_alive = False


class ConsoleReciever(Receiver):
    """Консольный обработчик входящих сообщений"""

    def process_message(self, message):
        # Выводим текст сообщения в консоль и рисуем от кого пришло
        print("\n>> user {}: {}".format(message.from_, message.message))


class GuiReciever(Receiver, QObject):
    """GUI обработчик входящих сообщений"""
    # мы его наследуюем от QObject чтобы работала модель сигнал слот
    # можно и не наследовать, но тогда надо передавать объект в который мы будем сообщения выводить
    # через сигнал слот более гибко т.к. мы можем обработать сигнал как хотим уже внутри gui
    # событий (сигнал) что пришли данные
    gotData = pyqtSignal(str)
    gotPic = pyqtSignal(bytes)

    gotInfo = pyqtSignal(str)
    gotAva = pyqtSignal(bytes)
    # событие (сигнал) что прием окончен
    finished = pyqtSignal(int)

    def __init__(self, sock, request_queue):
        # инициализируем как Receiver
        Receiver.__init__(self, sock, request_queue)
        # инициализируем как QObject
        QObject.__init__(self)

    def process_message(self, message):
        """Обработка сообщения"""
        # Генерируем сигнал (сообщаем, что произошло событие)
        # В скобках передаем нужные нам данные
        text = '{}:\n{}>{}'.format(message.time,message.from_,message.message)
        self.gotData.emit(text)

    def process_pictures(self,message):
        size = message.message
        text = '{} >>> image'.format(message.from_)
        b_picture = self.sock.recv(size)
        try:
            self.gotPic.emit(b_picture)
            self.gotData.emit(text)
        except Exception as e:
            print(e)

    def process_profiles(self,message):
        b_avatar = None
        if message.account_avatar:
            b_avatar = self.sock.recv(message.account_avatar)
        info = message.account_info
        try:
            self.gotAva.emit(b_avatar)
            self.gotInfo.emit(info)
        except Exception as e:
            print(e)

    def poll(self):
        super().poll()
        # Когда обработка событий закончиться сообщаем об этом генерируем сигнал finished
        self.finished.emit(0)



    # def process_message(self, message, window):
    #     """Обработка сообщения"""
    #     # Генерируем сигнал (сообщаем, что произошло событие)
    #     # В скобках передаем нужные нам данные
    #     text = '{} >>> {}'.format(message.from_, message.message)
    #     window.listWidgetMessages.addItem(text)