import logging.config
import os
import sys

class Loggerd:
    """
        Object to handle logging for our backend HTTP and DNS server

    """
    def __init__(self):
        self.config = {
                'version': 1,
                'disable_existing_loggers': False,
                'formatters': {
                    'standard': {
                        'format': '%(asctime)s [%(levelname)s] %(message)s'
                    },
                },
                'handlers': {
                    'backend_info': {
                        'level': 'INFO',
                        'formatter': 'standard',
                        'class': 'logging.handlers.RotatingFileHandler',
                        'filename':  os.path.join(sys.path[0], 'logs/backend_info.log'),
                        'mode': 'a',
                        'backupCount': '16'
                    },
                    'backend_error': {
                        'level': 'ERROR',
                        'formatter': 'standard',
                        'class': 'logging.handlers.RotatingFileHandler',
                        'filename':  os.path.join(sys.path[0], 'logs/backend_error.log'),
                        'mode': 'a',
                        'backupCount': '16'
                    },
                },
                'loggers': {
                    'backend_info_log': {'handlers': ['backend_info'], 'level': 'INFO', 'propagate': False},
                    'backend_error_log': {'handlers': ['backend_error'], 'level': 'ERROR', 'propagate': False},
                }
            }
        logging.config.dictConfig(self.config)
        logging.getLogger().setLevel(logging.DEBUG)
        self.info_log = logging.getLogger('backend_info_log')
        self.error_log = logging.getLogger('backend_error_log')


    def info(self, data, addr):
        """
            Function to log the notifications our server generates

            :param data: the data to be logged
            :param addr: the ip address of the agent
        """
        team = addr.split('.')[2]
        msg = '[{}] [Team - {}] {}\n'.format(addr[0], team, data)
        self.info_log.info(msg)

    def error(self, data, addr):
        """
            Function to log the errors our servers generate

            :param data: the data to be logged
            :param addr: the ip address of the agent
        """
        team = addr.split('.')[2]
        msg = '[{}] [Team - {}] {}\n'.format(addr[0], team, data)
        self.error_log.error(msg)
