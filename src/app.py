from fastapi import FastAPI

app = FastAPI(
    title="Mangify",
    description="Descubra, leia e viva histórias incríveis em um só app",
    version="0.1.0",
)


@app.get("/")
async def root():
    return {"message": "Bem vindo ao Mangify!"}
