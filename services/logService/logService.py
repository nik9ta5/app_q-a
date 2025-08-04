import logging
from datetime import datetime

class CustomLogger:
    def __init__(
        self, 
        path2log_dir, 
        log_file_name, 
        logging_lavel,
        outputConsole = False
        ):
        self.path2log_dir = path2log_dir
        self.log_file_name = log_file_name
        
        full_path2file_log = f"{path2log_dir}/{log_file_name}"
        logging.basicConfig(
            level=logging_lavel,  # Уровень логирования
            format='%(asctime)s - %(levelname)s\n%(message)s',  # Формат сообщений
            handlers=[
                logging.FileHandler(full_path2file_log),  # Запись в файл
                logging.StreamHandler() if outputConsole else None # Вывод в консоль (опционально)
            ],
            encoding='utf-8'
        )

        self._my_logger = logging.getLogger()

    def getLogger(self):
        return self._my_logger