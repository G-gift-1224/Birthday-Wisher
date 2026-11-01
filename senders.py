import os, time, requests
E = os.getenv
def _tg(method, chat_id, data, files=None):
    return requests.post(f"https://api.telegram.org/bot{E('TELEGRAM_BOT_TOKEN')}/{method}", data={"chat_id": chat_id, **data}, files=files, timeout=180).ok
def telegram(chat_id, text, video=None):
    if video:
        with open(video, "rb") as f: return _tg("sendVideo", chat_id, {"caption": text}, {"video": f})
    return _tg("sendMessage", chat_id, {"text": text})
def telegram_voice(chat_id, ogg):
    with open(ogg, "rb") as f: return _tg("sendVoice", chat_id, {}, {"voice": f})
def whatsapp(number, name, message, video_url=None):
    # Template must be approved in Meta Business Manager: body has 1 variable; add a VIDEO header if you want the video inside.
    comps = [{"type": "body", "parameters": [{"type": "text", "text": f"{name}. {message}"}]}]
    if video_url and E("WA_TEMPLATE_VIDEO") == "true":
        comps.insert(0, {"type": "header", "parameters": [{"type": "video", "video": {"link": video_url}}]})
    body = {"messaging_product": "whatsapp", "to": number, "type": "template",
            "template": {"name": E("WA_TEMPLATE"), "language": {"code": "en"}, "components": comps}}
    return requests.post(f"https://graph.facebook.com/v20.0/{E('WA_PHONE_ID')}/messages", json=body,
                         headers={"Authorization": f"Bearer {E('WA_TOKEN')}"}, timeout=30).ok
def instagram_story(video_url):
    g = f"https://graph.facebook.com/v20.0/{E('IG_USER_ID')}"
    r = requests.post(f"{g}/media", data={"media_type": "STORIES", "video_url": video_url, "access_token": E("IG_TOKEN")}, timeout=60).json()
    if "id" not in r: return False
    time.sleep(30)
    return requests.post(f"{g}/media_publish", data={"creation_id": r["id"], "access_token": E("IG_TOKEN")}, timeout=60).ok
