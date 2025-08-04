# =======================
# Для создания хешей
# =======================
import bcrypt


class HashPassService:
    def __init__(self):
        pass

    def create_hash_pass(self, password : str) -> str:
        """Функция для создания хеша от пароля
        (Args):
            password : str - Пароль
        
        return: str - хеш
        """
        hashed_pwd = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed_pwd

    def check_hash_pass(self, password : str, hash_pass : str) -> bool:
        """Проверка на совпадение пароля и хеша
        (Args):
            password : str - Исходный пароль
            hash_pass : str - Хеш
        
        return - bool    
        """
        # hash_pass.encode("utf-8") - Если хеш не как байтовая строка
        return bcrypt.checkpw(password.encode("utf-8"), hash_pass)