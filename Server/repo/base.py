import os
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, create_engine, BLOB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class Clients_base(Base):
    __tablename__ = 'Clients_base'

    ClientsContactsId = Column(Integer, primary_key=True)
    ClientId = Column(Integer, ForeignKey('Clients.Name'))
    ContactId = Column(Integer, ForeignKey('Clients.Name'))

    def __init__(self, client_id, contact_id):
        self.ClientId = client_id
        self.ContactId = contact_id

    def __repr__(self):
        return 'client_id={}-friend_id={}'.format(self.ClientId, self.ContactId)

class Clients(Base):
    __tablename__ ='Clients'
    ClientId = Column(Integer, primary_key=True)
    Name = Column(String, unique=True)
    Passw = Column(String, nullable=True)
    Info = Column(String, nullable=True)
    Avatar = Column(BLOB, nullable=True)


    def __init__(self, name, passw, info = None, avatar = None):
        self.Name=name
        self.Passw=passw
        if info:
            self.Info = info
        if avatar:
            self.Avatar = avatar

    def __repr__(self):
        return "<Client ('%s')>" % self.Name

    def __eq__(self, other):
        # Клиенты равны если равны их имена
        return self.name == other.name

# путь до папки где лежит этот модуль
DB_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
# путь до файла базы данных
DB_PATH = os.path.join(DB_FOLDER_PATH, 'ClientBase.db')
#создаем движок
engine = create_engine('sqlite:///{}'.format(DB_PATH), echo=False)
# Не забываем создать структуру базы данных
Base.metadata.create_all(engine)
# Создаем сессию для работы
Session = sessionmaker(bind=engine)
session = Session()

Msession = sessionmaker(bind=engine)
msession = Msession()
#list= session.query(Clients).all()
#print(list)
#list= session.query(Clients_base).all()
#print(list)
#Jhon do
#Any many
#Tedy bear