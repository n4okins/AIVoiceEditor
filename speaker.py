import api
from pathlib import Path
import requests
import json
from tqdm import trange
import time
from bs4 import BeautifulSoup

SAVE_DIR = Path("__file__").parent.resolve() / "なろう"

def get_narou_text(ncode):
    endpoint = f"https://api.syosetu.com/novelapi/api/?out=json&ncode={ncode}&of=t-w-ga"
    req = requests.get(endpoint)
    result = json.loads(req.text)
    title = result[1]["title"]
    target_dir = SAVE_DIR / title
    parts = result[1]["general_all_no"]
    target_dir.mkdir(exist_ok=True, parents=True)

    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0"}

    for part in trange(1, parts+1):
        textfile = target_dir / f"{part}.txt"
        if textfile.exists():
            continue
        else:
            with open(textfile, "w", encoding="utf-8") as f:
                # 作品本文ページのURL
                url = f"https://ncode.syosetu.com/{ncode}/{part}/"
                res = requests.get(url, headers=headers)
                soup = BeautifulSoup(res.content, "html.parser")
                content = soup.select_one("#novel_honbun").text
                # 保存
                f.write(content)
            time.sleep(1)


def read_narou_text(ncode, skip=0):
    endpoint = f"https://api.syosetu.com/novelapi/api/?out=json&ncode={ncode}&of=t-w-ga"
    req = requests.get(endpoint)
    result = json.loads(req.text)
    title = result[1]["title"]
    parts = result[1]["general_all_no"]
    target_dir = SAVE_DIR / title

    print(f"小説名: {title}")

    actor = api.AIVoiceActor()
    actor.master_control = api.MasterControl(Speed=1.75, Pitch=1.1, PitchRange=1.2)
    for part in range(1 + skip, parts + 1):
        target = target_dir / f"{part}.txt"
        with open(target, "r", encoding="utf-8") as f:
            print(f"Loading ", target.name)
            actor.text = f.read()
            actor.play()

    actor.disconnect()


if __name__ == "__main__":
    ncode = "n9736dt"
    read_narou_text(ncode, skip=1)
