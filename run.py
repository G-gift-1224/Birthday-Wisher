import threading, time, webbrowser, uvicorn
threading.Thread(target=lambda: (time.sleep(2), webbrowser.open("http://localhost:8000")), daemon=True).start()
uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
