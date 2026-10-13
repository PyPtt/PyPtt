from typing import Optional, Dict, Any

from fastapi import FastAPI
from pydantic import BaseModel
import logging
from . import __version__
from . import exceptions
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
        logging.exception(f"Error in API call {request.api}")
        response = {"api": request.api, "error": "An internal error has occurred."}
        # PyPtt 自己的例外只回傳類別名稱, 讓 client 可以分辨例如需要兩階段驗證;
        # 不回傳例外訊息與 args, 避免帳密或驗證碼外洩。
        if isinstance(e, exceptions.Error):
            response["error_type"] = type(e).__name__
            if isinstance(e, exceptions.TwoFactorAuthRequired):
                response["reason"] = str(e.reason)
        return response

    if result is None:
        result = 'success without return value'

    return {"api": request.api, "result": result}