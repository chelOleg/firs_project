"""Все ошибки """

class WrongInputError(Exception):
    pass

class WrongParamsError(WrongInputError):
    """Неверные параметры для действия"""

    def __init__(self, params):
        self.params = params

    def __str__(self):
        return 'Wrong action params: {}'.format(self.params)

class WrongActionError(WrongInputError):
    """Когда передано неверное действие"""

    def __init__(self, action):
        self.action = action

    def __str__(self):
        return 'Wrong action: {}'.format(self.action)

class WrongDictError(WrongInputError):
    """Когда пришел неправильный словарь"""

    def __init__(self, input_dict):
        self.input_dict = input_dict

    def __str__(self):
        return 'Wrong input dict: {}'.format(self.input_dict)

class ToLongError(Exception):
    """Ошибка когда наше поле длинее чем надо"""

    def __init__(self, name, value, max_length):
        """
        :param name: имя поля
        :param value: текущее значение
        :param max_length: максимальное значение
        """
        self.name = name
        self.value = value
        self.max_length = max_length

    def __str__(self):
        return '{}: {} to long (> {} simbols)'.format(self.name, self.value, self.max_length)

class UsernameToLongError(Exception):
    def __init__(self, username):
        self.username = username

    def __str__(self):
        return 'Имя пользователя {} должно быть менее 26 символов'.format(self.username)

class ResponseCodeError(Exception):
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return 'Неверный код ответа {}'.format(self.code)

class ResponseCodeLenError(ResponseCodeError):
    def __str__(self):
        return 'Неверная длина кода {}. Длина кода должна быть 3 символа.'.format(self.code)

class MandatoryKeyError(Exception):
    def __init__(self, key):
        self.key = key

    def __str__(self):
        return 'Не хватает обязательного атрибута {}'.format(self.key)

class ContactDoesNotExist(Exception):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'Contact {} does not exist'.format(self.name)