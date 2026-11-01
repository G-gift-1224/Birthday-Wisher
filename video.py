import subprocess, os
from PIL import Image, ImageDraw, ImageFont, ImageOps
TEMPLATES = {"party": ((255, 94, 98), (255, 195, 113)), "night": ((15, 32, 80), (110, 60, 160)), "mint": ((17, 153, 142), (56, 239, 125))}
def make_video(photo, name, message, template, song, out):
    c1, c2 = TEMPLATES.get(template, TEMPLATES["party"])
    W, H = 1080, 1920
    bg = Image.new("RGB", (W, H), c1)
    d = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)))
    img = ImageOps.fit(Image.open(photo).convert("RGB"), (800, 800))
    mask = Image.new("L", (800, 800), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 800, 800), fill=255)
    bg.paste(img, (140, 380), mask)
    try:
        big = ImageFont.truetype("DejaVuSans-Bold.ttf", 90); small = ImageFont.truetype("DejaVuSans.ttf", 50)
    except OSError:
        big = small = ImageFont.load_default()
    d.text((W // 2, 260), "Happy Birthday!", font=big, fill="white", anchor="mm")
    d.text((W // 2, 1320), name, font=big, fill="white", anchor="mm")
    d.text((W // 2, 1460), message[:60], font=small, fill="white", anchor="mm")
    frame = out + ".png"; bg.save(frame)
    cmd = ["ffmpeg", "-y", "-loop", "1", "-i", frame]
    if song and os.path.exists(song): cmd += ["-i", song, "-shortest"]
    cmd += ["-t", "15", "-vf", "zoompan=z='min(zoom+0.0008,1.15)':d=375:s=1080x1920,format=yuv420p", "-r", "25", "-c:v", "libx264", out]
    subprocess.run(cmd, check=True, capture_output=True)
    return out

def to_mp4(src, dst):
    subprocess.run(["ffmpeg", "-y", "-i", src, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart", dst], check=True, capture_output=True)
    return dst

def to_ogg(src):
    dst = src + ".ogg"
    subprocess.run(["ffmpeg", "-y", "-i", src, "-c:a", "libopus", dst], check=True, capture_output=True)
    return dst
