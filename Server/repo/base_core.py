from repo.base import Clients, Clients_base
from jim.exceptions import ContactDoesNotExist

from repo.base import session, msession

from pymongo import MongoClient

class Repo:
    """Серверное хранилище"""

    def __init__(self, session):
        """
        Запоминаем сессию, чтобы было удобно с ней работать
        :param session:
        """
        self.session = session

    def add_client(self, username, passw):
        """Добавление клиента"""
        new_item = Clients(username, passw)
        self.session.add(new_item)
        self.session.commit()

    def get_passw(self,username):
        client = self.get_client_by_username(username)
        if client:
            data = self.session.query(Clients).filter(Clients.Name == username).first()
            return data.Passw

    def client_exists(self, username):
        """Проверка, что клиент уже есть"""
        result = self.session.query(Clients).filter(Clients.Name == username).count() > 0
        return result

    def get_client_by_username(self, username):
        """Получение клиента по имени"""
        client = self.session.query(Clients).filter(Clients.Name == username).first()
        return client

    def add_contact(self, client_username, contact_username):
        """Добавление контакта"""
        contact = self.get_client_by_username(contact_username)
        if contact:
            client = self.get_client_by_username(client_username)
            if client:
                cc = Clients_base(client_id=client.ClientId, contact_id=contact.ClientId)
                self.session.add(cc)
                self.session.commit()
            else:
                # raise NoneClientError(client_username)
                pass
        else:
            raise ContactDoesNotExist(contact_username)

    def del_contact(self, client_username, contact_username):
        """Удаление контакта"""
        contact = self.get_client_by_username(contact_username)
        if contact:
            client = self.get_client_by_username(client_username)
            if client:
                cc = self.session.query(Clients_base).filter(
                    Clients_base.ClientId == client.ClientId).filter(
                    Clients_base.ContactId == contact.ClientId).first()
                self.session.delete(cc)
                self.session.commit()
            else:
                # raise NoneClientError(client_username)
                pass
        else:
            raise ContactDoesNotExist(contact_username)

    def get_contacts(self, client_username):
        """Получение контактов клиента"""
        client = self.get_client_by_username(client_username)
        result = []
        if client:
            # Тут нету relationship поэтому берем запросом
            contacts_clients = self.session.query(Clients_base).filter(Clients_base.ClientId == client.ClientId).all()
            for contact_client in contacts_clients:
                contact = self.session.query(Clients).filter(Clients.ClientId == contact_client.ContactId).first()
                result.append(contact)
            print(result)
        return result

    def get_profile(self,username):
        client = self.get_client_by_username(username)
        if client:
            data = self.session.query(Clients).filter(Clients.Name == username).first()
            return data.Avatar, data.Info

    def edit_profile(self,username,info=None,avatar=None):
        try:
            data = self.session.query(Clients).filter(Clients.Name == username).first()
            if info:
                data.Info = info
            if avatar:
                data.Avatar = avatar
            session.commit()
        except Exception as e:
            session.rollback()
            print(e)

class MongoRepo():
    """Хранилище сообщений"""
    def __init__(self, msession):
        self.session = msession
        mongo_client = MongoClient()
        histories_mongo = mongo_client.histories_db
        self.histories = histories_mongo.histories

    def add_history(self, history_dict):
        self.histories.insert_one(history_dict)

    def get_histories(self,name = None,nameII = None):
        mfilter ={'to':name}
        if name and nameII:
            mfilter = {"$or":[{'from':name,'to':nameII},{'from':nameII,'to':name}]}
        result =[]
        for history in self.histories.find(mfilter):
            del history ['_id']
            result.append(history)
        return result

    def delete_histories(self):
        try:
            self.histories.drop()
            text ='BASE DROPED'
            return text
        except Exception as e:
            text ="Can't connect mongo server \n{]".format(e)
            return text


# mong = MongoRepo(msession)
# er = mong.get_histories('Any','Jhon')
# for ob in er:
#     print(ob)

