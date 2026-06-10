#!/usr/bin/env python3
"""AI 陪伴助手 PWA - 后端服务"""
import asyncio
import json
import os
import signal
import sys
import time
import uuid
import yaml
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from core import Brain, Memory, TTSService


# ====== 加载配置 ======
BASE_DIR = Path(__file__).parent
with open(BASE_DIR / "config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

brain = Brain(config)
memory = Memory(str(BASE_DIR / "data"), config)
tts = TTSService(config)

# ====== 自主判断 ======
autonomy_running = True


async def autonomy_loop():
    """后台自主判断循环"""
    if not config["autonomy"]["enabled"]:
        return
    interval = config["autonomy"]["think_interval"]
    min_proactive = config["autonomy"]["proactive_min_interval"]

    while autonomy_running:
        await asyncio.sleep(interval)
        if not autonomy_running:
            break
        try:
            if time.time() - memory.last_proactive_time < min_proactive:
                continue
            context = memory.get_context_messages()
            profile = memory.get_profile_summary()
            mem_summary = memory.get_memory_summary()
            result = brain.autonomous_think(context, profile, mem_summary)
            if result.get("should_act") and result.get("message"):
                msg = result["message"]
                memory.add_message("assistant", f"[主动-{result.get('action_type','chat')}] {msg}")
                memory.last_proactive_time = time.time()
                # 推送给所有连接的WebSocket客户端
                for ws in list(active_websockets):
                    try:
                        await ws.send_json({"type": "proactive", "message": msg, "action": result.get("action_type")})
                    except:
                        pass
        except Exception as e:
            print(f"自主思考出错: {e}")


# ====== FastAPI ======
app = FastAPI(title="小超 AI 陪伴助手")

active_websockets: set[WebSocket] = set()


class ChatRequest(BaseModel):
    message: str


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """对话接口"""
    user_msg = req.message
    memory.add_message("user", user_msg)

    # 异步提取记忆（不阻塞回复）
    try:
        facts = brain.extract_memory(user_msg)
        if facts:
            memory.add_facts(facts)
    except:
        pass

    # 生成回复
    context = memory.get_context_messages()
    profile = memory.get_profile_summary()
    mem_summary = memory.get_memory_summary()
    reply = brain.chat(context, profile, mem_summary)
    memory.add_message("assistant", reply)

    # 生成语音
    audio_url = None
    try:
        audio_path = await tts.synthesize(reply)
        if audio_path:
            audio_url = f"/api/tts/{os.path.basename(audio_path)}"
    except:
        pass

    return {"reply": reply, "audio_url": audio_url}


@app.get("/api/tts/{filename}")
async def get_tts(filename: str):
    """获取TTS音频文件"""
    import tempfile
    path = os.path.join(tempfile.gettempdir(), filename)
    if os.path.exists(path):
        return FileResponse(path, media_type="audio/mpeg", filename=filename)
    return JSONResponse({"error": "not found"}, 404)


@app.get("/api/memory")
async def get_memory():
    """查看记忆"""
    return {
        "profile": memory.user_profile,
        "long_term": memory.long_term[-20:],
    }


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """WebSocket 长连接（推送主动消息）"""
    await ws.accept()
    active_websockets.add(ws)
    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "chat":
                user_msg = msg.get("message", "")
                memory.add_message("user", user_msg)
                try:
                    facts = brain.extract_memory(user_msg)
                    if facts:
                        memory.add_facts(facts)
                except:
                    pass
                context = memory.get_context_messages()
                reply = brain.chat(context, memory.get_profile_summary(), memory.get_memory_summary())
                memory.add_message("assistant", reply)
                await ws.send_json({"type": "reply", "message": reply})
    except WebSocketDisconnect:
        pass
    finally:
        active_websockets.discard(ws)


# 挂载静态文件
app.mount("/", StaticFiles(directory=str(BASE_DIR / "static"), html=True), name="static")


@app.on_event("startup")
async def startup():
    asyncio.create_task(autonomy_loop())


@app.on_event("shutdown")
async def shutdown():
    global autonomy_running
    autonomy_running = False
    memory.save_all()


if __name__ == "__main__":
    import uvicorn
    host = config["server"]["host"]
    port = config["server"]["port"]
    print(f"\n🤖 小超启动中... http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)
