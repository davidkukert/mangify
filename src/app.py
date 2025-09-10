from fastapi import FastAPI

from src.routers import users
from src.schemas.base import MessageResponse

app = FastAPI(
    title='Mangify',
    description='Descubra, leia e viva histórias incríveis em um só app',
    version='0.1.0',
)


@app.get('/', response_model=MessageResponse)
async def root():
    return dict(message='Bem vindo ao Mangify!')


app.include_router(users.router)
