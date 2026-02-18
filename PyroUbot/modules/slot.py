import os, json, random, time, asyncio
from PyroUbot import *

__MODULE__ = "🎰 Slot Game"
__HELP__ = """
<blockquote><b>Slot Game

Perintah:
• slot → main slot
• slot <bet> → slot taruhan
• autoslot on/off → auto slot
• double → double or nothing
• daily → bonus harian
• rank → leaderboard
• saldo → cek saldo</b></blockquote>
"""

DATA_FILE = "slot_data.json"

# ================= CONFIG =================
SLOT_SYMBOL = ["🍒", "🍋", "🍇", "🔔", "💎", "7️⃣"]
SLOT_CD = 6
AUTO_DELAY = 8

WIN = 2
BIG_WIN = 5
JACKPOT = 15

DAILY_REWARD = 50
DAILY_CD = 86400
MIN_SALDO = 5

# ================= RUNTIME =================
AUTO_SLOT = {}
COOLDOWN = {}
LAST_DAILY = {}
LAST_WIN = {}

# ================= DATABASE =================
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    return json.load(open(DATA_FILE))

def save_data(data):
    json.dump(data, open(DATA_FILE, "w"), indent=2)

def get_user(uid):
    data = load_data()
    uid = str(uid)
    if uid not in data:
        data[uid] = {"saldo": 100, "win": 0}
    return data, uid

def add_saldo(uid, amount):
    data, uid = get_user(uid)
    data[uid]["saldo"] += amount
    save_data(data)

def add_win(uid):
    data, uid = get_user(uid)
    data[uid]["win"] += 1
    save_data(data)

def is_cooldown(uid, delay):
    now = time.time()
    last = COOLDOWN.get(uid, 0)
    if now - last < delay:
        return True, int(delay - (now - last))
    COOLDOWN[uid] = now
    return False, 0

# ================= SLOT CORE =================
async def play_slot(uid, bet, msg):
    data, sid = get_user(uid)

    if data[sid]["saldo"] < bet or data[sid]["saldo"] <= MIN_SALDO:
        return await msg.edit_text("❌ Saldo terlalu kecil, ambil daily")

    data[sid]["saldo"] -= bet
    save_data(data)

    await asyncio.sleep(1.5)

    s1, s2, s3 = random.choice(SLOT_SYMBOL), random.choice(SLOT_SYMBOL), random.choice(SLOT_SYMBOL)
    text = f"🎰 | {s1} | {s2} | {s3} |\n\n"

    if s1 == s2 == s3:
        reward = bet * JACKPOT
        add_saldo(uid, reward)
        add_win(uid)
        LAST_WIN[uid] = reward
        text += f"🔥 JACKPOT!\n+{reward} saldo"
    elif s1 == s2 or s2 == s3 or s1 == s3:
        reward = bet * random.choice([WIN, BIG_WIN])
        add_saldo(uid, reward)
        add_win(uid)
        LAST_WIN[uid] = reward
        text += f"✨ MENANG!\n+{reward} saldo"
    else:
        text += "❌ KALAH"

    await msg.edit_text(text)

# ================= COMMAND =================
@PY.UBOT("slot")
async def slot_cmd(_, m):
    uid = m.from_user.id
    cd, left = is_cooldown(uid, SLOT_CD)
    if cd:
        return await m.reply_text(f"⏳ {left}s")

    args = m.text.split()
    bet = int(args[1]) if len(args) > 1 and args[1].isdigit() else 10

    msg = await m.reply_text("🎰 Memutar slot...")
    await play_slot(uid, bet, msg)

# ================= AUTO SLOT =================
@PY.UBOT("autoslot")
async def autoslot_cmd(_, m):
    uid = m.from_user.id
    args = m.text.split()

    if len(args) == 1:
        return await m.reply_text(f"🤖 AutoSlot: {'ON' if AUTO_SLOT.get(uid) else 'OFF'}")

    if args[1] == "on":
        AUTO_SLOT[uid] = True
        msg = await m.reply_text("🤖 Auto slot aktif")
        while AUTO_SLOT.get(uid):
            await play_slot(uid, 10, msg)
            await asyncio.sleep(AUTO_DELAY)

    elif args[1] == "off":
        AUTO_SLOT[uid] = False
        await m.reply_text("⛔ Auto slot OFF")

# ================= DAILY =================
@PY.UBOT("daily")
async def daily_cmd(_, m):
    uid = m.from_user.id
    now = time.time()
    last = LAST_DAILY.get(uid, 0)

    if now - last < DAILY_CD:
        sisa = int((DAILY_CD - (now - last)) / 3600)
        return await m.reply_text(f"⏳ Daily tersedia {sisa} jam lagi")

    add_saldo(uid, DAILY_REWARD)
    LAST_DAILY[uid] = now
    await m.reply_text(f"🎁 Daily bonus +{DAILY_REWARD} saldo")

# ================= DOUBLE =================
@PY.UBOT("double")
async def double_cmd(_, m):
    uid = m.from_user.id
    reward = LAST_WIN.get(uid)

    if not reward:
        return await m.reply_text("❌ Tidak ada win")

    if random.choice([True, False]):
        add_saldo(uid, reward)
        LAST_WIN.pop(uid, None)
        await m.reply_text(f"🔥 BERHASIL!\n+{reward} saldo")
    else:
        data, sid = get_user(uid)
        data[sid]["saldo"] -= reward
        save_data(data)
        LAST_WIN.pop(uid, None)
        await m.reply_text("💀 GAGAL! Saldo hangus")

# ================= RANK =================
@PY.UBOT("rank")
async def rank_cmd(_, m):
    data = load_data()
    top = sorted(data.items(), key=lambda x: x[1]["saldo"], reverse=True)[:10]

    text = "🏆 RANK SLOT\n\n"
    for i, (uid, v) in enumerate(top, 1):
        text += f"{i}. {uid}\n💰 {v['saldo']} | 🏆 {v['win']}\n\n"

    await m.reply_text(text)

# ================= SALDO =================
@PY.UBOT("saldo")
async def saldo_cmd(_, m):
    data, uid = get_user(m.from_user.id)
    await m.reply_text(
        f"💰 Saldo: {data[uid]['saldo']}\n"
        f"🏆 Menang: {data[uid]['win']}x"
    )
    