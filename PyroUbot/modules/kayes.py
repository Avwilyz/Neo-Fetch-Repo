import random
from PyroUbot import *

__MODULE__ = "ᴋᴀʏᴇs"
__HELP__ = """
<blockquote><b>Bantuan Random Kayes</b>

Perintah:
<code>{0}kayes</code> → Kirim foto Kayes random (SFW)
</blockquote>
"""

# FOTO KAYES (Pinterest)
KAYES_PHOTO = [
    "https://i.pinimg.com/736x/dd/f4/52/ddf45202d850bbcbf23db2fd3aa425bc.jpg",
    "https://i.pinimg.com/originals/a0/77/70/a0777027eca8763eb35a4555ab6bc6ba.jpg",
    "https://i.pinimg.com/736x/9e/56/98/9e5698539df9cbd72035f4220d214c48.jpg",
    "https://i.pinimg.com/originals/97/f8/4f/97f84fecc8164443f9e4de641cece672.jpg",
    "https://i.pinimg.com/originals/0f/5e/8f/0f5e8fb610d4f783792df3ccca409de7.jpg",
    "https://i.pinimg.com/originals/af/cd/1b/afcd1b675a659513a00fa464edfb3309.jpg",
    "https://i.pinimg.com/originals/f1/8d/5b/f18d5b91e3cbb5d600765a5010c2e2e2.jpg",
    "https://i.pinimg.com/736x/08/aa/0f/08aa0f966a9f87d0d41ce32702966665.jpg",
    "https://i.pinimg.com/736x/69/63/cf/6963cf8b90b1d5680721bdba5de6c18a.jpg",
    "https://i.pinimg.com/736x/c5/02/f6/c502f6f12b0e2e972ed3f676a8129f5e.jpg",
    # (dipotong biar rapi — sisanya aman langsung tempel)
]

# VIDEO KAYES (kosong dulu, Pinterest bukan mp4)
KAYES_VIDEO = []

CAPTION = "💖 <b>Random Kayes</b>\nBiar harimu makin adem ✨"

@PY.UBOT("kayes")
async def kayes_cmd(client, message):
    try:
        media = random.choice(KAYES_PHOTO)
        await message.reply_photo(
            photo=media,
            caption=CAPTION
        )

        await message.react("🔥")

    except Exception as e:
        await message.reply_text(f"❌ Gagal mengambil Kayes!\n{e}")
        