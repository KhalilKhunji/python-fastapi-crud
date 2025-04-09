# main.py

from fastapi import FastAPI
from controllers.teas import router as TeasRouter
from controllers.comments import router as CommentsRouter

app = FastAPI()
app.include_router(TeasRouter, prefix="/api")
app.include_router(CommentsRouter, prefix="/api")


@app.get('/')
def home():
    # Hello world function
    return {'message': 'Hello World!'}

