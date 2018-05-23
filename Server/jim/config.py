"""Константы для jim протокола, настройки"""
# Ключи
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
ACCOUNT_PASSW = 'account_passw'
ACCOUNT_INFO = 'account_info'
ACCOUNT_AVATAR = 'account_avatar'
USER_ID = 'user_id'
RESPONSE = 'response'
ERROR = 'error'
ALERT = 'alert'
QUANTITY = 'quantity'

# Значения
PRESENCE = 'presence'
KEY ='key'
B_KEY ='back_key'
GET_PASSW ='get_password'
MSG = 'msg'
TO = 'to'
FROM = 'from'
IMG_SIZE ='image_size'
MESSAGE = 'message'
GET_CONTACTS = 'get_contacts'
CONTACT_LIST = 'contact_list'
ADD_CONTACT = 'add_contact'
DEL_CONTACT = 'del_contact'
IMG ='image'
UPDATE_PROFILE = 'profile_update'
GET_PROFILE = 'get_profile'
SEND_PROFILE ='send_profile'
GET_STORYES = 'messege_story'
# Коды ответов (будут дополняться)
BASIC_NOTICE = 100
OK = 200
ACCEPTED = 202
WRONG_REQUEST = 400  # неправильный запрос/json объект
SERVER_ERROR = 500
ACCOUNT_ERROR = 255
USER_OFFLINE = 256

# Кортеж из кодов ответов
RESPONSE_CODES = (USER_OFFLINE, BASIC_NOTICE, OK, ACCEPTED, WRONG_REQUEST, SERVER_ERROR, ACCOUNT_ERROR)

USERNAME_MAX_LENGTH = 25
MESSAGE_MAX_LENGTH = 500

ENCODING = 'utf-8'

# Кортеж действий
ACTIONS = (IMG, PRESENCE, MSG, GET_CONTACTS, CONTACT_LIST, ADD_CONTACT, DEL_CONTACT, GET_PASSW, B_KEY, GET_PROFILE, SEND_PROFILE, UPDATE_PROFILE, GET_STORYES)
