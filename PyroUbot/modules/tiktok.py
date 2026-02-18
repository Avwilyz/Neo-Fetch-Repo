import os
import asyncio
import requests
from pyrogram import filters
from PyroUbot import PY

# ---------------- TikTok & TTSlide ---------------- #
import base64
import json
from urllib.parse import urlencode

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Cookie": "current_language=en"
}

# TikTok download via Tikwm API
async def get_tiktok(url):
    try:
        data = {"url": url, "hd": "1"}
        res = requests.post("https://tikwm.com/api/", data=urlencode(data), headers=HEADERS, timeout=15).json()
        video = res.get("data")
        if not video:
            return None
        return {
            "title": video.get("title"),
            "no_watermark": video.get("play"),
            "watermark": video.get("wmplay"),
            "cover": video.get("cover"),
            "music": video.get("music")
        }
    except Exception:
        return None

# TikTok search via Tikwm
async def search_tiktok(keywords):
    try:
        data = {"keywords": keywords, "count": 50, "cursor": 0, "HD": 1}
        res = requests.post("https://tikwm.com/api/feed/search", data=urlencode(data), headers=HEADERS, timeout=15).json()
        videos = res.get("data", {}).get("videos")
        if not videos:
            return None
        video = videos[asyncio.randrange(len(videos))]
        return {
            "title": video.get("title"),
            "no_watermark": video.get("play"),
            "watermark": video.get("wmplay"),
            "cover": video.get("cover"),
            "music": video.get("music")
        }
    except Exception:
        return None

# TTSlide download via DLPanda
import bs4
def get_ttslide(url):
    try:
        resp = requests.get(f"https://dlpanda.com/id?url={url}&token=G7eRpMaa", headers={"User-Agent": HEADERS["User-Agent"]}, timeout=15)
        soup = bs4.BeautifulSoup(resp.text, "html.parser")
        images = []
        for img in soup.select("div.col-md-12 > img"):
            src = img.get("src")
            if src:
                images.append(src)
        return images
    except Exception:
        return []

# ---------------- PyroUbot Commands ---------------- #

@PY.UBOT("tiktok")
async def tiktok_download(client, message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply_text("⚠️ Harap masukkan URL TikTok.\nContoh: `.tiktok https://vt.tiktok.com/...`")
    url = args[1]
    data = await get_tiktok(url)
    if not data:
        return await message.reply_text("🚫 Gagal mengambil video TikTok.")
    # Kirim video
    await message.reply_video(data["no_watermark"], caption=f"🎬 {data['title']}\n🎵 {data['music']}")

@PY.UBOT("tts")
async def tiktok_search(client, message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply_text("⚠️ Harap masukkan kata kunci.\nContoh: `.tts lucu`")
    keywords = args[1]
    data = await search_tiktok(keywords)
    if not data:
        return await message.reply_text("🚫 Tidak ada video ditemukan.")
    await message.reply_video(data["no_watermark"], caption=f"🎬 {data['title']}\n🎵 {data['music']}")

@PY.UBOT("ttslide")
async def ttslide_cmd(client, message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        return await message.reply_text("⚠️ Harap masukkan URL TTSlide.\nContoh: `.ttslide https://www.tiktok.com/...`")
    url = args[1]
    images = get_ttslide(url)
    if not images:
        return await message.reply_text("🚫 Gagal mengambil slide.")
    # Kirim semua gambar
    for img in images:
        await message.reply_photo(img)
        