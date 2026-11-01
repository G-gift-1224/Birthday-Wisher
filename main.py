import os, sqlite3, uuid, shutil, datetime as dt
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, UploadFile, Form, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from apscheduler.schedulers.background import BackgroundScheduler
from . import senders, video

TZ = ZoneInfo(os.getenv("TZ_NAME", "Asia/Kolkata"))
for d in ("uploads", "media", "songs"): os.makedirs(d, exist_ok=True)
db = sqlite3.connect("wishes.db", check_same_thread=False); db.row_factory = sqlite3.Row
db.execute("""create table if not exists wishes(id text primary key, name text, message text, photo text, video text, voice text,
  song text, template text, send_at text, tg_chat text, wa_number text, ig_story int, status text)""")
app = FastAPI()

@app.get("/")
def home(): return FileResponse("static/index.html")
@app.get("/api/songs")
def songs(): return [f for f in os.listdir("songs") if f.endswith(".mp3")]
@app.get("/api/wishes")
def wishes(): return [dict(r) for r in db.execute("select id,name,send_at,status from wishes order by send_at desc")]

def keep(f, path):
    if f and f.filename:
        with open(path, "wb") as o: shutil.copyfileobj(f.file, o)
        return path
    return ""

@app.post("/api/wishes")
def create(name: str = Form(...), message: str = Form(""), send_at: str = Form(...), template: str = Form("party"),
           song: str = Form(""), tg_chat: str = Form(""), wa_number: str = Form(""), ig_story: int = Form(0),
           photo: UploadFile = File(None), video_file: UploadFile = File(None), voice: UploadFile = File(None)):
    wid = str(uuid.uuid4())[:8]
    p, v, a = keep(photo, f"uploads/{wid}.jpg"), keep(video_file, f"uploads/{wid}.vid"), keep(voice, f"uploads/{wid}.voice")
    if not p and not v: return JSONResponse({"error": "Add a photo or upload a ready video"}, 400)
    db.execute("insert into wishes values(?,?,?,?,?,?,?,?,?,?,?,?,?)", (wid, name, message, p, v, a, song, template, send_at, tg_chat, wa_number, ig_story, "scheduled"))
    db.commit()
    return {"id": wid, "status": "scheduled"}

def process(w):
    out, res = f"media/{w['id']}.mp4", []
    if w["video"]: video.to_mp4(w["video"], out)
    else: video.make_video(w["photo"], w["name"], w["message"], w["template"], f"songs/{w['song']}" if w["song"] else None, out)
    text = f"🎂 Happy Birthday {w['name']}! {w['message']}"
    url = f"{os.getenv('PUBLIC_URL', '')}/media/{w['id']}.mp4"
    if w["tg_chat"]:
        res.append(("Telegram", senders.telegram(w["tg_chat"], text, out)))
        if w["voice"]: res.append(("Telegram voice", senders.telegram_voice(w["tg_chat"], video.to_ogg(w["voice"]))))
    if w["wa_number"]: res.append(("WhatsApp", senders.whatsapp(w["wa_number"], w["name"], w["message"], url)))
    if w["ig_story"]: res.append(("IG Story", senders.instagram_story(url)))
    status = ", ".join(f"{n}: {'sent' if ok else 'FAILED'}" for n, ok in res) or "nothing to send"
    db.execute("update wishes set status=? where id=?", (status, w["id"])); db.commit()
    if os.getenv("OWNER_TELEGRAM_CHAT_ID"):
        senders.telegram(os.getenv("OWNER_TELEGRAM_CHAT_ID"), f"✅ Wish for {w['name']} -> {status}")

def tick():
    now = dt.datetime.now(TZ).replace(tzinfo=None).isoformat(timespec="minutes")
    for w in db.execute("select * from wishes where status='scheduled' and send_at<=?", (now,)).fetchall():
        db.execute("update wishes set status='running' where id=?", (w["id"],)); db.commit()
        try: process(dict(w))
        except Exception as e:
            db.execute("update wishes set status=? where id=?", (f"error: {e}", w["id"])); db.commit()

sched = BackgroundScheduler(timezone=TZ); sched.add_job(tick, "interval", seconds=20); sched.start()
app.mount("/media", StaticFiles(directory="media"), name="media")
