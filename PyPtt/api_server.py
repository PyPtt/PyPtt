from typing import Optional, Dict, Any

from fastapi import FastAPI
from pydantic import BaseModel

from . import __version__
from . import service

app = FastAPI()

pyptt_service = service.Service()


class ApiRequest(BaseModel):
    api: str
    args: Optional[Dict[str, Any]] = None


@app.get("/")
def root():
    return {"pyptt_version": __version__}


@app.post("/api")
def api_func(request: ApiRequest):
    try:
        api = request.api
        args = request.args
        result = pyptt_service.call(api, args)

    except Exception as e:
        return {"api": request.api, "args": request.args, "error": str(e)}

    if result is None:
        result = 'success without return value'

    return {"api": request.api, "result": result}