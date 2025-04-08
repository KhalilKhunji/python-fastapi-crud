# main.py

from fastapi import FastAPI

app = FastAPI()


@app.get('/')
def home():
    # Hello world function
    return {'message': 'Hello World!'}
