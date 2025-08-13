# =======================
# Сервис аутентификации и авторизации
# =======================
import logging
import sqlite3
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from services.DBService.dataBase import DataBase
from services.authService.hashPassService import HashPassService
from services.authService.jwtService import JWTService

class AuthService:
    def __init__(
        self, db : DataBase, 
        hashService : HashPassService, 
        jwtService : JWTService, 
        secret_key : str,
        logger : logging = None
        ):
        """Инициализация сервиса
        (Args):
            db : DataBase - ссылка на сервис для работы с БД 
            hashService : HashPassService - Для создания хеша
            jwtService : JWTService - Для создания jwt
            secret_key : str 
        """
        if logger:
            logger.debug(f"auth service init start")

        self.logger = logger
        self.db = db
        self.hashService = hashService
        self.jwtService = jwtService
        self.secret_key = secret_key

        if logger:
            logger.debug(f"auth service init end")

    def auth(self, username : str, password : str):
        """Аутентификация пользователя
        (Args):
            username : str - Имя пользователя
            password : str - Пароль
        
        return: str - jwt
        """
        if not username or not password:
            raise ValueError("'username' and 'password' can not is emprt or none")
        try:
            #Получить хеш пароля пользователя из бд
            user = self.db.get_user_info_username(username)   

            if not user:
                raise ValueError(f"user with username: {username} not found")
            
            hash_pass = self.hashService.create_hash_pass(password)
            
            #Сравнить Хеши
            if not self.hashService.check_hash_pass(password, user['hash_pass']):
                raise ValueError("username or password is not correct")
            
            for_payload = {
                "id" : user['id'],
                "dir_for_files" : str(user['dir_for_files'])
            }

            jwtoken = self.jwtService.create_jwt(
                for_payload, 
                self.secret_key, 
                expires_in_minutes=30 #config
            )
            return jwtoken 
        
        except sqlite3.Error as e:
            raise SystemError(e)
        except ValueError as e: #Для переброса внутренней ошибки ValueError
            raise ValueError(e)
        except Exception as e:
            raise SystemError(e)
        
    def valid(self, jwt : str) -> dict:
        """function for valid jwt"""
        try:
            payload = self.jwtService.valid_jwt(jwt, self.secret_key)
            return payload
        except ExpiredSignatureError as e:
            raise ExpiredSignatureError(e)
        except InvalidTokenError as e:
            raise InvalidTokenError(e)
        except Exception as e:
            raise Exception(e)