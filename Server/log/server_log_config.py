import logging
import logging.handlers
import os


# Папка где лежит этот файл
LOG_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
# Пусть до серверного лога
SERVER_LOF_FILE_PATH = os.path.join(LOG_FOLDER_PATH, 'server.log')
# Формат сообщения
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
# Создаем логгер с именем server
server_logger = logging.getLogger('server')
# Создаем обработчик с ротацией файлом по дням
server_handler = logging.handlers.TimedRotatingFileHandler(SERVER_LOF_FILE_PATH, when='d')
# Связываем обработчик с форматером
server_handler.setFormatter(formatter)
# Связываем логгер с обработчиком
server_logger.addHandler(server_handler)
# Устанавливаем уровень сообщений
server_logger.setLevel(logging.INFO)