import json
import random
import asyncio
from PyroUbot import *

__MODULE__ = "ғɪsʜɪɴɢ"
__HELP__ = """
<blockquote><b>Fishing / Mancing Game</b>

Perintah:
<code>.fish</code> - Mancing sekali
<code>.inv</code> - Cek inventory ikan
<code>.sell [nama ikan] [jumlah]</code> - Jual ikan
<code>.sell all</code> - Jual semua ikan
<code>.shop</code> - Lihat toko & beli rod
<code>.buy [item]</code> - Beli item
<code>.profile</code> - Cek level, coin, rod
<code>.leaderboard</code> - Lihat ranking pemain</blockquote>
"""

DATA_FILE = "fishing_data.json"

# Data user {chat_id: {...}}
DATA = {}

# Daftar ikan dan rarity
FISH_LIST = {
    "Common": ["Ikan Teri", "Ikan Lele", "Ikan Mas"],
    "Rare": ["Ikan Tuna", "Ikan Salmon"],
    "Epic": ["Ikan Paus Mini"],
    "Legendary": ["Ikan Naga"]
}

# Harga jual ikan
FISH_PRICE = {
    "Ikan Teri": 5,
    "Ikan Lele": 10,
    "Ikan Mas": 15,
    "Ikan Tuna": 50,
    "Ikan Salmon": 70,
    "Ikan Paus Mini": 200,
    "Ikan Naga": 500
}

# Shop items
SHOP = {
    "Wooden Rod": {"price": 100, "multiplier": 1},
    "Iron Rod": {"price": 500, "multiplier": 1.5},
    "Golden Rod": {"price": 2000, "multiplier": 2}
}

# Fishing cooldown per user
COOLDOWN = {}

FISH_COOLDOWN = 5  # detik

# --- Helper Functions ---
def load_data():
    global DATA
    try:
        with open(DATA_FILE, "r") as f:
            DATA = json.load(f)
    except:
        DATA = {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(DATA, f, indent=2)

def get_user(chat_id):
    if str(chat_id) not in DATA:
        DATA[str(chat_id)] = {
            "level": 1,
            "xp": 0,
            "coin": 100,  # 💰 Coin awal gratis
            "rod": "Wooden Rod",  # 🎣 Rod gratis awal
            "inventory": {}
        }
    return DATA[str(chat_id)]
    
    

def add_xp(user, amount):
    user["xp"] += amount
    leveled_up = False
    while user["xp"] >= user["level"] * 100:
        user["xp"] -= user["level"] * 100
        user["level"] += 1
        leveled_up = True
    return leveled_up  # kembalikan True jika naik level
    

# --- Commands ---
@PY.UBOT("fish")
async def fish_cmd(client, message):
    chat_id = message.chat.id
    now = asyncio.get_event_loop().time()
    if COOLDOWN.get(chat_id, 0) > now:
        await message.reply_text("⏳ Tunggu beberapa detik sebelum memancing lagi.")
        return
    user = get_user(chat_id)
    if not user["rod"]:
        await message.reply_text("❌ Kamu belum punya rod. Beli dulu di .shop")
        return

    # Pilih ikan
    rarity_roll = random.randint(1,100)
    if rarity_roll <= 60:
        rarity = "Common"
    elif rarity_roll <= 85:
        rarity = "Rare"
    elif rarity_roll <= 97:
        rarity = "Epic"
    else:
        rarity = "Legendary"
    fish = random.choice(FISH_LIST[rarity])

    # Coin reward = harga ikan * rod multiplier
    rod = user["rod"]
    multiplier = SHOP[rod]["multiplier"] if rod in SHOP else 1
    coin_reward = int(FISH_PRICE.get(fish,0) * multiplier)

    # Tambah XP & cek level up
    leveled_up = add_xp(user, random.randint(5,15))

    # Tambah ikan ke inventory
    user["inventory"][fish] = user["inventory"].get(fish,0) +1
    # Tambah coin
    user["coin"] += coin_reward

    save_data()
    COOLDOWN[chat_id] = now + FISH_COOLDOWN

    # Kirim pesan
    msg_text = f"🎣 Kamu memancing dan mendapatkan **{fish}** ({rarity})!\n💰 Coin didapat: {coin_reward}"
    if leveled_up:
        msg_text += f"\n🎉 Selamat! Kamu naik ke **Level {user['level']}**!"
    await message.reply_text(msg_text)
        

@PY.UBOT("inv")
async def inv_cmd(client, message):
    user = get_user(message.chat.id)
    inv = user["inventory"]
    if not inv:
        return await message.reply_text("📦 Inventory kosong")
    txt = "📦 Inventory kamu:\n"
    for fish, qty in inv.items():
        txt += f"{fish} x{qty}\n"
    await message.reply_text(txt)

@PY.UBOT("sell")
async def sell_cmd(client, message):
    args = message.text.split(" ")
    user = get_user(message.chat.id)

    if len(args) < 2:
        return await message.reply_text("Gunakan: .sell [nama ikan] [jumlah/all]")

    # Cek jika jual semua
    if args[-1].lower() == "all":
        total = 0
        for fish, qty in list(user["inventory"].items()):
            rod = user["rod"]
            multiplier = SHOP[rod]["multiplier"] if rod in SHOP else 1
            total += int(FISH_PRICE.get(fish,0) * multiplier * qty)
        user["inventory"] = {}
        user["coin"] += total
        save_data()
        return await message.reply_text(f"💰 Kamu menjual semua ikan dan mendapatkan {total} coin")

    # Nama ikan = semua kata kecuali arg terakhir (jumlah)
    if not args[-1].isdigit():
        return await message.reply_text("Gunakan: .sell [nama ikan] [jumlah]")
    
    qty = int(args[-1])
    fish_name = " ".join(args[1:-1])  # ambil semua kata kecuali jumlah

    if fish_name not in user["inventory"] or user["inventory"][fish_name] < qty:
        return await message.reply_text("❌ Ikan tidak cukup atau tidak ada di inventory")

    # Hitung coin = harga ikan x qty x rod multiplier
    rod = user["rod"]
    multiplier = SHOP[rod]["multiplier"] if rod in SHOP else 1
    total = int(FISH_PRICE.get(fish_name,0) * qty * multiplier)

    # Kurangi inventory
    user["inventory"][fish_name] -= qty
    if user["inventory"][fish_name]==0:
        del user["inventory"][fish_name]

    user["coin"] += total
    save_data()
    await message.reply_text(f"💰 Kamu menjual {qty} {fish_name} dan mendapatkan {total} coin")
    

@PY.UBOT("shop")
async def shop_cmd(client, message):
    txt = "🛒 Shop:\n"
    for item, data in SHOP.items():
        txt += f"{item} - Harga: {data['price']} coin, Multiplier: {data['multiplier']}\n"
    await message.reply_text(txt)

@PY.UBOT("buy")
async def buy_cmd(client, message):
    args = message.text.split(" ",1)
    if len(args)<2:
        return await message.reply_text("Gunakan: .buy [item]")
    item = args[1]
    if item not in SHOP:
        return await message.reply_text("❌ Item tidak ada di shop")
    user = get_user(message.chat.id)
    price = SHOP[item]["price"]
    if user["coin"]<price:
        return await message.reply_text("❌ Coin kamu tidak cukup")
    user["coin"] -= price
    user["rod"] = item
    save_data()
    await message.reply_text(f"✅ Kamu membeli {item}!")
    
@PY.UBOT("profile")
async def profile_cmd(client, message):
    user = get_user(message.chat.id)
    txt = f"""📊 Profil {message.from_user.first_name}:
Level: {user['level']}
XP: {user['xp']}/{user['level']*100}
Coin: {user['coin']}
Rod: {user['rod'] if user['rod'] else 'Belum punya'}"""
    await message.reply_text(txt)

@PY.UBOT("leaderboard")
async def leaderboard_cmd(client, message):
    # Ranking by coin
    ranking = sorted(DATA.items(), key=lambda x: x[1].get("coin",0), reverse=True)
    txt = "🏆 Leaderboard:\n"
    for i, (uid, info) in enumerate(ranking[:10], start=1):
        txt += f"{i}. User ID: {uid} | Coin: {info.get('coin',0)} | Level: {info.get('level',1)}\n"
    await message.reply_text(txt)

# Load data saat bot start
load_data()
