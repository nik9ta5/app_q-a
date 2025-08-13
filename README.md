# `app_q-a`
Приложение для ответов на вопросы по документам пользователей

## Описание
Частичная реализация серверной части приложения для ответов на вопросы по документам.

## Диаграмма компонентов
![Диаграмма компонентов](./app_doc/comp_diagrm.svg)

### Компоненты

`./services/` - все компоненты приложения


* `./authService` - аутентификация, авторизация
* `./DBService` - работа с базой данных
* `./VDBService` - работа с векторной базой данных
* `./userService` - управление пользователями
* `./documentService` - работа с документами 
* `./promptService` - обработка промптов
* `./LLM` - взаимодействие с языковой моделью
* `./chatService` - история чата
* `./RAGService` - реализация RAG-пайплайна
* `./embeddingService` - генерация векторных представлений (эмбеддингов)
* `./logService` - логирование


## Запуск
**Версия Python, использованная при разработке:** `3.10.11`

* Клонировать репозиторий
```bash
git clone https://github.com/nik9ta5/app_q-a.git
cd ./app_q-a
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
* Установить зависимости из файла `requirements.txt`
```bash
pip install -r requirements.txt
```
* Отредактировать файл конфигурации: `./config/AppConfig.yaml`
* Запустить приложение через `main.py`
```bash
python main.py
```

## Интерфейс
GUI не реализован.
Взаимодействие с приложением осуществляется через отправку **HTTP**-запросов

```
http://127.0.0.1:8005
```



## API Endpoints:

### 1. Регистрация пользователей
**Path**: `POST: /reg`
**Request Body:**
```json
{
    "username" : "nikita",
    "password" : "pass"
}
```
**Response Body:**
```json
{
    "message" : "server message",
    "system_message" : "system message"
}
```

### 2. Аутентификация пользователей 
**Path**: `POST: /auth`
**Request Body:**
```json
{
    "username" : "nikita",
    "password" : "pass"
}
```
**Response Body:**
```json
{
    "jwt" : "token.token.token"
}
```

### 3. Отправка запроса с вопросом по документам
**Path**: `POST: /prompt`
**Request Body:**
```json
{
    "jwt" : "token.token.token",
    "message" : "This is text message for system"
}
```
**Response Body:**
```json
{
    "message" : "server message",
    "system_message" : "system message"
}
```

### 4. Загрузка документов
**Path**: `POST: /load`
**Пример отправки документов через Python `requests`**
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
**Response Body:**
```json
{
    "message" : "server message",
    "system_message" : "system message"
}
```