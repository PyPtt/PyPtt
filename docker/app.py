from typing import Optional

import PyPtt
from fastapi import FastAPI

app = FastAPI()

service = PyPtt.Service()

import json


def object_decode(s: str):
    # convert base64 string to object using json
    if s is None:
        return None
    return json.loads(s)


@app.get("/")
def root():
    return {"pyptt_version": PyPtt.version}


@app.get("/api")
def api_func(api, args: Optional[str] = None):
    global service

    try:
        args = object_decode(args)
        result = service.call(api, args)

        # raise Exception('test')
    except Exception as e:
        # print(traceback.format_exc())
        return {"api": api, "args": args, "error": str(e)}

    if result is None:
        result = 'success without return value'

    return {"api": api, "result": result}