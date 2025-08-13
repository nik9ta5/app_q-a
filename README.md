# `app_q&a`
Приложение для ответов на вопросы по документам пользователей

## Описание
Частичная реализация серверной части приложения для ответов на вопросы по документам.

## Запуск

* Клонировать репозиторий
```bash
git clone https://github.com/nik9ta5/app_q-a.git
```
* Создать виртуальное окружение и активировать его
```bash
python -m venv venv
```
#### Windows:
```cmd
venv\Scripts\activate
```
#### Linux:
```bash
source venv/bin/activate
```

* Перейти в корневую директорию проекта
```bash
cd ./app_q-a
```
* Установить записимости из файла `requirements.txt`
```bash
pip install -r requirements.txt
```
* Отредактировать файл конфигурации 
* Запустить приложение через `main.py`
```bash
python main.py
```

## Компоненты

`./services/` - все компоненты приложения


* `./authService` - аутентификация, авторизация
* `./DBService/dataBase.py` - для работы с базой данных
* `./VDBService` - для работы с векторной базой данных
* `./userService` - для работы с пользователями
* `./documentService` - для работы с документами 
* `./promptService` - для работы с промптами
* `./LLM` - для работы с языковой моделью
* `./chatService/chatService.py` - реализация истории чата
* `./RAGService` - реализация RAG пайплайна
* `./embeddingService` - для работы с моделью для создания эмеддингов
* `./logService` - для логирования


## Интерфейс
GUI не реализован, взаимодействие с приложением осуществляется через отправку **HTTP** запросов

`http://127.0.0.1:8005`



## API Endpoints:

### 1. Регистрация пользователей
**Path**: `POST: /reg`
**Request Body**: Принимает JSON с данными о пользователе
**Пример**
```json
{
    "username" : "nikita",
    "password" : "pass"
}
```

### 2. Аутентификация пользователей 
**Path**: `POST: /auth`
**Request Body**: Принимает JSON с данными о пользователе
**Пример**
```json
{
    "username" : "nikita",
    "password" : "pass"
}
```

### 3. Отправка запроса с вопросом по документам
**Path**: `POST: /prompt`
**Request Body**: Принимает JSON с токеном и вопросом
**Пример**
```json
{
    "jwt" : "token.token.token",
    "message" : "This is text message for system"
}
```

### 4. Загрузка документов
**Path**: `POST: /load`
**Request Body**: Принимает токен и документы для загрузки на сервер
**Пример отпраки документов через Python `requests`**
```python
file_paths = [
    "Kak_uchitsya_mashina_Revolyutsia_v_oblasti_neyronnykh_setey_2021.pdf",
    "guide_build_agents.pdf",
]

docs = []
for file_path in file_paths:
if not os.path.exists(file_path):
    print(f"Файл {file_path} не найден")
    continue
docs.append((
    'docs', 
    (
    os.path.basename(file_path), 
    open(file_path, 'rb'), 
    'application/octet-stream'
    )
))

async def file_load(url, docs):
  data_payload = {
      "JWToken" : "token.token.token"
  }
  timeout = httpx.Timeout(60.0, connect=5.0) 
  async with httpx.AsyncClient(timeout=timeout) as client:
    response = await client.post(
        url,
        data=data_payload,
        files=docs
    )
    print(response.status_code)
    print(response.json())


if __name__ == "__main__":
  asyncio.run(file_load("http://localhost:8005/load", docs))
```