# =======================
# Сервис, отвечающий за работу с БД
# =======================
import os
import sqlite3


class DataBase:
    def __init__(self, path2database : str, database_name : str, path2schema_file_database : str, new_init = False, logger = None):
        """Конструктор, инициализация БД
        (Args):
            path2database : str - Путь до директории с файлом БД
            database_name : str - Название файла БД
            path2schema_file_database : str - Путь до файла со схемой БД
            new_init = False - Полная инициализация БД (загружать схему)
            logger = None - Логировании (import logger)
        """
        if logger:
            logger.debug(f"db init start")
            
        self.logger = logger
        self.path2database = path2database
        self.database_name = database_name
        self.path2schema_file_database = path2schema_file_database
        self.full_path2db = f"{self.path2database}/{self.database_name}"


        #Create dir for database file
        os.makedirs(path2database, exist_ok=True)
        
        try:
            # first init database
            if new_init:
                # read full sql script for create DB
                with open(path2schema_file_database, 'r', encoding="UTF-8") as file:
                    sql_script = file.read()

                with sqlite3.connect(f"{path2database}/{database_name}") as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.executescript(sql_script)
                    conn.commit()

        except FileNotFoundError:
            if logger:
                logger.error(f"Error: file schema '{path2schema_file_database}' not found")
        
        except sqlite3.Error as e:
            if logger:
                logger.error(f"Error db init: {e}")
        
        except Exception as e:
            if logger:
                logger.error(f"Error: {e}")
        
        finally:
            if logger:
                logger.debug(f"db init end")


    def get_user_info_username(self, username : str) -> dict:
        """Получение информации о пользователе по username
        (Args):
            username : str - Имя пользователя
        
        return: dict() - user info or None (if not found user)
        """
        try:
            with sqlite3.connect(self.full_path2db) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                query_str = "SELECT * FROM users WHERE username = ?"
                cursor.execute(query_str, (username,))
                
                user = cursor.fetchone()
                return dict(user) if user else None
                
        except sqlite3.Error as e:
            if self.logger:
                self.logger.error(f"Error select user: {username},\n{e}")
            raise sqlite3.Error(e)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error: {e}")
            raise Exception(e)
        finally:
            if self.logger:
                self.logger.info(f"select complite")


    def get_user_info_id(self, id : int) -> dict:
        """Получение информации о пользователе по id
        (Args):
            id : int - Имя пользователя
        
        return: dict() - user info or None (if not found user)
        """
        try:
            with sqlite3.connect(self.full_path2db) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                query_str = "SELECT * FROM users WHERE id = ?"
                cursor.execute(query_str, (id,))
                
                user = cursor.fetchone()
                return dict(user) if user else None
                
        except sqlite3.Error as e:
            if self.logger:
                self.logger.error(f"Error select user: {id},\n{e}")
            raise sqlite3.Error(e)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error: {e}")
            raise Exception(e)
        finally:
            if self.logger:
                self.logger.info(f"select complite")

    
    def insert_new_user(self, username : str, email : str, hash_pass : str, dir_for_files : str):
        """Добавление нового пользователя
        (Args):
            username : str - Имя пользователя
            email : str - Почта
            hash_pass : str - Хеш пароля
            dir_for_files : str- Путь до директории с файлами пользователя на сервере (мб тоже сделать хеш)
        """
        if not username or not email or not hash_pass:
            raise ValueError("'username', 'email', 'hash_pass' can not empty or None")
        if not dir_for_files:
            raise ValueError("'dir_for_files' empty")
        
        try:
            with sqlite3.connect(self.full_path2db) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                query_str = "INSERT INTO users(username, email, hash_pass, dir_for_files) VALUES (?, ?, ?, ?)"
                cursor.execute(query_str, (username, email, hash_pass, dir_for_files))
                conn.commit()
                
        except sqlite3.Error as e:
            if self.logger:
                self.logger.error(e)
            raise ValueError(e)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error: {e}")
            raise ValueError(e)
        finally:
            if self.logger:
                self.logger.info(f"insert complite")
    