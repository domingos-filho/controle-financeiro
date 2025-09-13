from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API de Controle Financeiro funcionando com domínio configurado!"}
