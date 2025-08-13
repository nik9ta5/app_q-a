# =======================
# Точка входа в приложение
# =======================
import os
import uuid
import shutil
import logging
import yaml

# Для того, чтобы сервисы инициализировались 1 раз
import functools

import torch

import uvicorn
from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, Response, status, HTTPException, UploadFile, File, Header, Form, Depends

from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

# ======== SERVICES IMPORT ========
from services.logService.logService import CustomLogger
from services.DBService.dataBase import DataBase
from services.authService.hashPassService import HashPassService
from services.authService.jwtService import JWTService
from services.authService.authService import AuthService
from services.userService.userService import UserService

from services.embeddingService.embeddingService import SentenceTransformerEmbedding
from services.VDBService.vectorDataBase import VectorDBService

from services.documentService.documentLoader import DocumentLoader
from services.documentService.textSplitter import TextSplitterService
from services.documentService.documentService import DocumentService

from services.promptService.promptService import PromptService
from services.chatService.chatService import ChatService

from services.LLM.transformers_LLM import LLM_transformers
from services.RAGService.RAGService import RAGService

# ======== CONFIG LOAD ========
with open(f'./config/AppConfig.yaml', 'r') as file:
    CONFIG = yaml.safe_load(file)
print(f"===== CONFIG =====\n{CONFIG}\n===============")

# ======== VARIABLES ========
SECRET_KEY = CONFIG['secret_key']
FILE_LIMIT = CONFIG['file_limit']

#FAST API Application
app = FastAPI()



# <======== SERVICES INIT START ========>
@functools.lru_cache()
def get_logger():
    return CustomLogger(
        CONFIG['dir_for_logs'], 
        CONFIG['log_filename'], 
        logging_lavel=logging.DEBUG,
        outputConsole=True
    )

@functools.lru_cache()
def get_db():
    return DataBase(
        CONFIG["dir_for_db"], 
        CONFIG["db_filename"], 
        CONFIG["path2scheme_db"], 
        new_init=CONFIG['new_init_db'], 
        logger=get_logger().getLogger()
    )

@functools.lru_cache()
def get_hash_service():
    return HashPassService()

@functools.lru_cache()
def get_jwt_service():
    return JWTService(logger=get_logger().getLogger())

@functools.lru_cache()
def get_auth_service():
    return AuthService(get_db(), get_hash_service(), get_jwt_service(), SECRET_KEY, logger=get_logger().getLogger())

@functools.lru_cache()
def get_user_service():
    return UserService(get_db(), get_hash_service(), logger=get_logger().getLogger(), base_dir=CONFIG["dir_for_temp_dirs"])

@functools.lru_cache()
def get_sentense_transformer_embedding():
    return SentenceTransformerEmbedding(
        cache_folder=CONFIG["dir_for_cache_models"]
    )

@functools.lru_cache()
def get_vdb():
    return VectorDBService(
        CONFIG["dir_for_db"],
        CONFIG["vdb_filename"],
        get_sentense_transformer_embedding(),
        logger=get_logger().getLogger()
    )
    
@functools.lru_cache()
def get_document_loader():
    return DocumentLoader()

@functools.lru_cache()
def get_text_spliter():
    return TextSplitterService(
        chunk_size=CONFIG["split_document_chunk_size"], 
        chunk_overlap=CONFIG["split_document_chunk_overlap"]
    )

@functools.lru_cache()
def get_document_service():
    return DocumentService(
        get_document_loader(),
        get_text_spliter(),
        get_vdb(),
        logger=get_logger().getLogger()
    )
    
@functools.lru_cache()
def get_prompt_service():
    return PromptService(
        instruction="""You are a helper, an expert in machine learning and artificial intelligence, designed to help answer questions.
Answer the question using the context provided, without using your knowledge. Ignore any knowledge gained prior to this conversation.
Context is the relevant fragments of documents found by the search that should be used to answer.
The answer should be a word, phrase, or sentence contained in the context.
If the context does not answer the question, answer 'No answer.'""",
        system_instruction=None,
        logger=get_logger().getLogger()
    )

@functools.lru_cache()
def get_chat_service():
    return ChatService()

@functools.lru_cache()
def get_llm_transformer():
    return LLM_transformers(
        CONFIG["model"],
        CONFIG["dir_for_cache_models"],
        "cuda" if torch.cuda.is_available() else "cpu",
        full_model_path=CONFIG["model_full_local_path"],
        local_load=True,
        logger=get_logger().getLogger()
    )
    
@functools.lru_cache()
def get_rag_service():
    return RAGService(
        get_llm_transformer(), 
        get_prompt_service(), 
        get_chat_service(), 
        get_vdb(), 
        logger=get_logger().getLogger()
    )


# >======== SERVICES INIT END ========<




# ======== Models ========

class ServerRequest(BaseModel):
    jwt : str = Field(..., examples="JWT")
    message : Optional[str] = Field(None, examples="This is field for text request for server")

class ServerResponse(BaseModel):
    message : str = Field(..., examples="Response server")
    system_message : Optional[str] = Field(None, examples="This field for system message")

class AuthModelRequest(BaseModel):
    username : str = Field(..., examples='username')
    password : str = Field(..., examples='password')

class AuthModelResponse(BaseModel):
    jwt : str = Field(..., examples='jwt')

class RegModelRequest(BaseModel):
    username : str = Field(..., examples='username')
    email : str = Field(..., examples='email@gmail.com')
    password : str = Field(..., examples='password')

class DocLoadModelRequest(BaseModel):
    jwt : str = Field(..., examples="jwt")
    docs : list[UploadFile] = File(...)


# ======== Routes ========

@app.get("/", status_code=status.HTTP_200_OK)
async def read_root():
    """Эндпоинт для проверки работы API"""
    return {"message":"Hello API"}


@app.post("/reg", response_model=ServerResponse, status_code=status.HTTP_200_OK)
async def reg_func(
    user_info_request : RegModelRequest,
    userService : UserService = Depends(get_user_service)
    ):
    """Эндпоинт для регистрации пользователя
    (Args):
        user_info_request : RegModelRequest - info about user (username, email, password)
    
    return : ServerResponse - info about reg user
    """
    if not user_info_request.username:
        raise HTTPException(status_code=400, detail="username can not is empty") #ПОМЕНЯТЬ НА КОРРЕКТНЫЙ КОД
    if not user_info_request.password:
        raise HTTPException(status_code=400, detail="password can not is empty") #ПОМЕНЯТЬ НА КОРРЕКТНЫЙ КОД
    if not user_info_request.email:
        raise HTTPException(status_code=400, detail="email can not is empty") #ПОМЕНЯТЬ НА КОРРЕКТНЫЙ КОД

    try: 
        #Тут дописать
        if userService.reg(user_info_request.username, user_info_request.email, user_info_request.password):
            return ServerResponse(message="user registory complite")
        raise HTTPException(status_code=400, detail="user no registory") #ПОМЕНЯТЬ НА КОРРЕКТНЫЙ КОД
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) #ПОМЕНЯТЬ НА КОРРЕКТНЫЙ КОД


@app.post("/auth", response_model=AuthModelResponse, status_code=status.HTTP_200_OK)
async def auth_func(
    user_info_request : AuthModelRequest,
    authService : AuthService = Depends(get_auth_service)
    ):
    """Эндпоинт для аутентификации пользователя
    (Args):
        user_info_request : AuthModelRequest - info about user (username, password)
    
    return : str - JWT
    """
    if not user_info_request.username:
        raise HTTPException(status_code=400, detail="username can not is empty") #ПОМЕНЯТЬ НА КОРРЕКТНЫЙ КОД
    if not user_info_request.password:
        raise HTTPException(status_code=400, detail="password can not is empty") #ПОМЕНЯТЬ НА КОРРЕКТНЫЙ КОД
    
    try: 
        jwtoken = authService.auth(user_info_request.username, user_info_request.password)
        return AuthModelResponse(jwt=jwtoken)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) #ПОМЕНЯТЬ НА КОРРЕКТНЫЙ КОД
    except SystemError as e:
        raise HTTPException(status_code=404, detail=str(e)) #ПОМЕНЯТЬ НА КОРРЕКТНЫЙ КОД


@app.post("/prompt", response_model=ServerResponse, status_code=status.HTTP_200_OK)
async def prompt_request(
    request : ServerRequest,
    authService : AuthService = Depends(get_auth_service),
    ragService : RAGService = Depends(get_rag_service)
    ):
    if not request.jwt:
        raise HTTPException(status_code=401, detail="not jwt")
    try:
        #Валидация токена
        payload = authService.valid(request.jwt)
        
        model_response, relevant_docs = ragService.response(
            request.message,
            str(payload['id']),
            max_length=int(CONFIG['max_length']),
            max_new_tokens=int(CONFIG['max_new_tokens']),
            k=CONFIG['vdb_find_k'],
            repetition_penalty=CONFIG["repetition_penalty"],
            no_repeat_ngram_size=CONFIG["no_repeat_ngram_size"],
            do_sample=CONFIG["do_sample"],
            top_k=CONFIG["top_k"],
            top_p=CONFIG["top_p"],
            temperature=CONFIG["temperature"]
        )

        return ServerResponse(message=model_response)
    
    except ExpiredSignatureError as e:
        raise HTTPException(status_code=404, detail=str(e)) #ПОМЕНЯТЬ НА КОРРЕКТНЫЙ КОД 
    except InvalidTokenError as e: 
        raise HTTPException(status_code=404, detail=str(e)) #ПОМЕНЯТЬ НА КОРРЕКТНЫЙ КОД
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) #ПОМЕНЯТЬ НА КОРРЕКТНЫЙ КОД


@app.post("/load", response_model=ServerResponse, status_code=status.HTTP_200_OK)
async def load_func(
    JWToken: str = Form(..., examples=["jwt"]), # Имя поля в multipart-форме
    docs: List[UploadFile] = File(..., examples=["document.pdf"]),
    authService : AuthService = Depends(get_auth_service),
    documentService : DocumentService = Depends(get_document_service)
    ):
    
    try:
        payload = authService.valid(JWToken)
        # payload['dir_for_files']

        # === LOAD FILES ON SERVER ===
        UPLOAD_DIR = f"./TEMP/{payload['dir_for_files']}"
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        cnt_files = len(os.listdir(UPLOAD_DIR))
        if cnt_files >= FILE_LIMIT:
            return HTTPException(status_code=406, detail=f"FILES MANY {FILE_LIMIT} on SERVER")

        diff_cnd_files = FILE_LIMIT - cnt_files
        if diff_cnd_files < len(docs):
            return HTTPException(status_code=406, detail=f"CAN NOT LOAD FILES MORE {diff_cnd_files}")

        # === LOAD FILES ===
        uploaded_file_paths = []
        for doc in docs:
            print(doc.filename)
            file_extension = os.path.splitext(doc.filename)[-1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = f"{UPLOAD_DIR}/{unique_filename}"

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(doc.file, buffer)

            uploaded_file_paths.append(file_path)

        print(f"UPLOAD FILES: {uploaded_file_paths}")

        # === USE DOCUMENT SERVICE ===

        # print(str(payload["id"]))
        documentService.load_docs(str(payload["id"]), uploaded_file_paths)

        return ServerResponse(message="server response")

    except ExpiredSignatureError as e:
        raise HTTPException(status_code=404, detail=str(e)) #ПОМЕНЯТЬ НА КОРРЕКТНЫЙ КОД 
    except InvalidTokenError as e: 
        raise HTTPException(status_code=404, detail=str(e)) #ПОМЕНЯТЬ НА КОРРЕКТНЫЙ КОД
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) #ПОМЕНЯТЬ НА КОРРЕКТНЫЙ КОД




# =============================================================== RUN ===============================================================


if __name__ == "__main__":    
    # ====== FastAPI ======
    uvicorn.run("main:app", host="127.0.0.1", port=8005, reload=False)
    