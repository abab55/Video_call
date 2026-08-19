"""联机视频通话信令服务器（Python + aiohttp）。

特性:
    - 多人同大厅，实时成员列表
    - 定向呼叫 / 接听 / 拒绝 / 忙 / 挂断
    - offer/answer/candidate 定向转发

部署:
    pip install aiohttp
    python videocall_server.py

访问:
    打开页面 ?name=昵称 进入大厅，点击成员发起视频通话。
    摄像头需要 https 或 localhost 环境。
"""
import asyncio
import json
import uuid

from aiohttp import web

PEERS = {}     # ws -> {id, name}
PEER_WS = {}   # id -> ws


async def index(request):
    return web.FileResponse("./index.html")


def peer_list():
    return [{"id": p["id"], "name": p["name"]} for p in PEERS.values()]


async def broadcast_peers():
    payload = json.dumps({"type": "peers", "peers": peer_list()})
    for ws in list(PEERS):
        try:
            await ws.send_str(payload)
        except Exception:
            pass


async def ws_handler(request):
    ws = web.WebSocketResponse(max_msg_size=1 << 20)
    await ws.prepare(request)
    pid = uuid.uuid4().hex[:8]
    name = (request.rel_url.query.get("name") or "").strip()[:20] or ("用户" + pid[:4])
    PEERS[ws] = {"id": pid, "name": name}
    PEER_WS[pid] = ws
    try:
        await ws.send_json({"type": "hello", "id": pid, "name": name})
        await broadcast_peers()
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                await route(ws, json.loads(msg.data))
            elif msg.type == web.WSMsgType.ERROR:
                break
    finally:
        PEERS.pop(ws, None)
        PEER_WS.pop(pid, None)
        await broadcast_peers()
    return ws


async def route(ws, data):
    mtype = data.get("type")
    to = data.get("to")
    print(f"[route] type={mtype} to={to}")
    if not to:
        return
    target = PEER_WS.get(to)
    if not target or target is ws:
        return
    data["from"] = PEERS[ws]["id"]
    data.setdefault("name", PEERS[ws]["name"])
    await target.send_json(data)


async def main():
    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/ws", ws_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=8080)
    await site.start()
    print("视频通话服务器已启动: http://0.0.0.0:8080/?name=昵称")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
