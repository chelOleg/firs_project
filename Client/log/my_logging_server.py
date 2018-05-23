import logging

logging.basicConfig(
    filename='server_logs',
    format = '%(asctime)s %(levelname)-10s %(module)s %(funcname)s %(messege)s',
    level=logging.DEBUG
)

log=logging.getLogger('server_basic_log')
help(log)

log.debug('Дебаг')
log.info('Инфо')
log.warning('Угроза')
log.critical('УУУУГГГГРРРОООЗЗААА!!!!!(Важно)')
