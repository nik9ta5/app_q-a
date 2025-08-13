# =======================
# Сервис, отвечающий за управление пользователями
# =======================
import os
import uuid
import logging

from services.DBService.dataBase import DataBase
from services.authService.hashPassService import HashPassService

class UserService:
    def __init__(
        self, db : DataBase, 
        hashService : HashPassService,
        logger : logging = None,
        base_dir : str = "./TEMP"
        ):

        if logger:
            logger.debug(f"user service init start")

        self.logger = logger
        self.db = db
        self.hashService = hashService
        self.base_dir = base_dir

        if logger:
            logger.debug(f"user service init end")


    def reg(self, username : str, email : str, password : str) -> bool:
        """Регистрация нового пользователя"""
        #Сделать хеш пароля
        hash_pass = self.hashService.create_hash_pass(password)

        try:
            #Создать директорию для файлов пользователей
            os.makedirs(self.base_dir, exist_ok=True)
            path2dir_for_files = str(uuid.uuid4())
            os.makedirs(f"{self.base_dir}/{path2dir_for_files}")

            #Добавить пользователя
            self.db.insert_new_user(
                username,
                email,
                hash_pass,
                path2dir_for_files
            )
            return True
        #Поймать ошики
        except ValueError as e:
            raise ValueError(e)
