from fastapi import Request

async def RedisConnect(request: Request):
    return request.app.state.redis
