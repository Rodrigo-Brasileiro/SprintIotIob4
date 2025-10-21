import os
import cv2
import time
import sqlite3
import numpy as np
import mediapipe as mp
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from numpy.linalg import norm

DATASET_DIR = "data/dataset"
ENC_FILE = "data/encodings/encodings.npz"
EMB_SIZE = 128
THRESH = 0.32            # distance threshold (menor = mais rígido)
MIN_DET_CONF = 0.55
DB_PATH = "data/events.db"

app = FastAPI(title="Face Microservice", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount('/demo', StaticFiles(directory='public', html=True), name='demo')

mp_face = mp.solutions.face_detection

def _ensure_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, user TEXT, score REAL, action TEXT);")
    con.commit(); con.close()

def _log_event(user: str, score: float, action: str):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("INSERT INTO events(ts,user,score,action) VALUES(?,?,?,?)",(time.time(), user, score, action))
    con.commit(); con.close()

def _img_to_embedding(bgr: np.ndarray) -> np.ndarray:
    h, w = bgr.shape[:2]
    with mp_face.FaceDetection(model_selection=1, min_detection_confidence=MIN_DET_CONF) as fd:
        res = fd.process(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        if not res.detections:
            raise ValueError("no_face")
        det = res.detections[0]
        bb = det.location_data.relative_bounding_box
        x = max(0, int(bb.xmin * w)); y = max(0, int(bb.ymin * h))
        ww = max(1, int(bb.width * w)); hh = max(1, int(bb.height * h))
        x2, y2 = min(w, x+ww), min(h, y+hh)
        crop = bgr[y:y2, x:x2]
        if crop.size == 0:
            raise ValueError("bad_crop")
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        emb = cv2.resize(gray, (EMB_SIZE, EMB_SIZE)).astype(np.float32) / 255.0
        emb = emb.flatten()
        return emb / (norm(emb) + 1e-8)

def _read_image_file(file_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(file_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("decode_error")
    return img

def _save_encodings(names: List[str], embs: List[np.ndarray]):
    os.makedirs(os.path.dirname(ENC_FILE), exist_ok=True)
    np.savez_compressed(ENC_FILE, names=np.array(names), embs=np.stack(embs))

def _load_encodings():
    if not os.path.exists(ENC_FILE):
        return [], np.zeros((0, EMB_SIZE*EMB_SIZE), dtype=np.float32)
    data = np.load(ENC_FILE, allow_pickle=True)
    return list(data["names"]), data["embs"].astype(np.float32)

@app.on_event("startup")
def startup():
    _ensure_db()
    if not os.path.exists(ENC_FILE) and os.path.exists(DATASET_DIR):
        names, embs = [], []
        for person in sorted(os.listdir(DATASET_DIR)):
            pdir = os.path.join(DATASET_DIR, person)
            if not os.path.isdir(pdir): continue
            for fn in os.listdir(pdir):
                if fn.lower().endswith((".jpg",".jpeg",".png")):
                    path = os.path.join(pdir, fn)
                    img = cv2.imread(path)
                    if img is None: continue
                    try:
                        emb = _img_to_embedding(img)
                        names.append(person)
                        embs.append(emb)
                    except Exception:
                        continue
        if embs:
            _save_encodings(names, embs)

class VerifyResult(BaseModel):
    matched: bool
    user: Optional[str] = None
    score: Optional[float] = None

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/enroll")
async def enroll(name: str = Form(...), image: UploadFile = File(...)):
    img = _read_image_file(await image.read())
    try:
        emb = _img_to_embedding(img)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Face not found: {e}")
    names, embs = _load_encodings()
    names.append(name)
    embs = list(embs) if isinstance(embs, np.ndarray) else embs
    embs.append(emb)
    _save_encodings(names, embs)
    return {"ok": True, "count": len(names)}

@app.post("/verify", response_model=VerifyResult)
async def verify(image: UploadFile = File(...), action: str = Form("login")):
    img = _read_image_file(await image.read())
    try:
        q = _img_to_embedding(img)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Face not found: {e}")
    names, embs = _load_encodings()
    if len(embs) == 0:
        raise HTTPException(status_code=400, detail="No enrolled faces.")
    if isinstance(embs, list):
        import numpy as _np
        embs = _np.stack(embs)
    sims = embs @ q / (norm(embs, axis=1) * (norm(q)+1e-8) + 1e-8)
    dists = (1 - sims) * 0.5
    idx = int(np.argmin(dists))
    best = float(dists[idx])
    matched = best < THRESH
    user = names[idx] if matched else None
    if matched:
        _log_event(user, best, action)
    return VerifyResult(matched=matched, user=user, score=best)

@app.get("/events")
def events(limit: int = 50):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT ts,user,score,action FROM events ORDER BY id DESC LIMIT ?", (limit,))
    rows = [{"ts": r[0], "user": r[1], "score": r[2], "action": r[3]} for r in cur.fetchall()]
    con.close()
    return {"events": rows}
