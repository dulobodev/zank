from http import HTTPStatus

from fastapi import FastAPI
from fastapi_profiler import PyInstrumentProfilerMiddleware

from backend.models.Mensages import Message
from backend.routers import (
    auth,
    bot,
    categorias,
    gastos,
    metas,
    users,
    webhook,
)

app = FastAPI()


app.include_router(users.router)
app.include_router(auth.router)
app.include_router(categorias.router)
app.include_router(gastos.router)
app.include_router(metas.router)
app.include_router(webhook.router)
app.include_router(bot.router)


@app.get('/', response_model=Message, status_code=HTTPStatus.OK)
def read_root():
    return {'message': 'Hello World'}
