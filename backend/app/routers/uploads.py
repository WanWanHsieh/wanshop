import os
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from ..utils.paths import ensure_dir, public_url_for

router = APIRouter()

@router.post("/fabrics/{fabric_id}")
async def upload_fabric_images(fabric_id: int, kind: str = "image", files: List[UploadFile] = File(...)):
    if kind not in ("image", "work"):
        raise HTTPException(400, "kind must be 'image' or 'work'")
    sub = "images" if kind == "image" else "works"
    saved = []
    base_dir = ensure_dir(f"fabrics/{fabric_id}/{sub}")
    for idx, f in enumerate(files):
        ext = os.path.splitext(f.filename)[1].lower() or ".jpg"
        filename = f"{idx}_{abs(hash(f.filename))}{ext}"
        path = os.path.join(base_dir, filename)
        with open(path, "wb") as out:
            out.write(await f.read())
        saved.append(public_url_for(path))
    return {"saved": saved}

@router.post("/products/{product_id}")
async def upload_product_images(product_id: int, files: List[UploadFile] = File(...)):
    saved = []
    base_dir = ensure_dir(f"products/{product_id}/images")
    for idx, f in enumerate(files):
        ext = os.path.splitext(f.filename)[1].lower() or ".jpg"
        filename = f"{idx}_{abs(hash(f.filename))}{ext}"
        path = os.path.join(base_dir, filename)
        with open(path, "wb") as out:
            out.write(await f.read())
        saved.append(public_url_for(path))
    return {"saved": saved}
