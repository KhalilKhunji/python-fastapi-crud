# main.py

from fastapi import FastAPI
from controllers.teas import router as TeasRouter

app = FastAPI()
app.include_router(TeasRouter, prefix="/api")


@app.get('/')
def home():
    # Hello world function
    return {'message': 'Hello World!'}

