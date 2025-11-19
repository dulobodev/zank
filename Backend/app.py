from http import HTTPStatus

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models.Mensages import Message
from .routers import (
    auth,
    bot,
    categorias,
    gastos,
    metas,
    users,
    stripe,
    webhook,
    
)

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins= ["*"],      
    allow_credentials=True,    
    allow_methods=["*"],         
    allow_headers=["*"],          
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(categorias.router)
app.include_router(gastos.router)
app.include_router(metas.router)
app.include_router(webhook.router)
app.include_router(bot.router)
app.include_router(stripe.router)


@app.get('/', response_model=Message, status_code=HTTPStatus.OK)
def read_root():
    return {'message': 'Hello World'}
