# =======================
# Для работы с JWT
# =======================
import jwt
import datetime 
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError


class JWTService:
    def __init__(self, logger = None):
        self.logger = logger

    def create_jwt(self, payload : dict, secret_key : str, algorithm = "HS256", expires_in_minutes: int = 30) -> str:
        """Создание токена
        (Args):
            user_id : int - ID пользователя
            secret_key : str - Ключ для создания JWT
            algorithm = "HS256" - Алгоритм 
            expires_in_minutes: int = 30 - Срок жизни токена в минутах
        """
        expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=expires_in_minutes)
        
        payload["exp"] = expiration_time.timestamp()
        print("PAYLOAD JWT: ", payload)
        encoded_jwt = jwt.encode(payload, secret_key, algorithm=algorithm)
        return encoded_jwt

    def valid_jwt(self, token : str, secret_key : str, algorithms : list = ["HS256"]) -> dict:
        """Валидация токена
        (Args):
            token : str - токен 
            secret_key : str - Ключ
            algorithms : list = ["HS256"] - Допустимые алгоритмы
        
        return : dict - payload
        """
        try:
            decoded_payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            return decoded_payload
        except ExpiredSignatureError:
            if self.logger:
                self.logger.error("Time life token end")
            raise ExpiredSignatureError("Time life token end")
        except InvalidTokenError:
            if self.logger:
                self.logger.error("Token not correct")
            raise InvalidTokenError("Token not correct")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error: {e}")
            raise ValueError(e)


