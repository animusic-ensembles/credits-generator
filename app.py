from __future__ import annotations

import csv
import re
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from generator import build_archive
from parser import ParseError


ROOT = Path(__file__).resolve().parent
app = FastAPI(title='Credit Image Generator')
app.mount('/static', StaticFiles(directory=ROOT / 'static'), name='static')
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


@app.get('/', response_class=HTMLResponse)
def index() -> str:
    return (ROOT / 'index.html').read_text(encoding='utf-8')


@app.post('/generate')
async def generate(file: UploadFile = File(...)) -> StreamingResponse:
    filename = file.filename or ''
    if Path(filename).suffix.lower() != '.csv':
        raise HTTPException(status_code=415, detail='Please upload a .csv file.')

    contents = await file.read(MAX_UPLOAD_BYTES + 1)
    await file.close()
    if not contents:
        raise HTTPException(status_code=400, detail='The uploaded CSV is empty.')
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail='The CSV must be 10 MB or smaller.')

    try:
        contents.decode('utf-8')
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=400, detail='The CSV must be UTF-8 encoded.'
        ) from exc

    try:
        archive = build_archive(contents)
    except ParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except csv.Error as exc:
        raise HTTPException(status_code=422, detail=f'Invalid CSV: {exc}') from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f'Image generation failed: {exc}',
        ) from exc

    stem = re.sub(r'[^A-Za-z0-9_-]+', '-', Path(filename).stem).strip('-') or 'credits'
    headers = {'Content-Disposition': f'attachment; filename="{stem}-images.zip"'}
    return StreamingResponse(archive, media_type='application/zip', headers=headers)
