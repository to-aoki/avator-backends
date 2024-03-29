# origin: https://github.com/morioka/tiny-openai-whisper-api

import os
import shutil
from typing import Optional
from functools import lru_cache

from fastapi import FastAPI, Form, UploadFile, File, APIRouter
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from faster_whisper import WhisperModel

# curl https://api.openai.com/v1/audio/transcriptions \
#  -H "Authorization: Bearer $OPENAI_API_KEY" \
#  -H "Content-Type: multipart/form-data" \
#  -F model="whisper-1" \
#  -F file="@/path/to/file/openai.mp3"

# {
#  "text": "Imagine the wildest idea that you've ever had, and you're curious about how it might scale to something that's a 100, a 1,000 times bigger..."
# }

# -----
# copied from https://github.com/hayabhay/whisper-ui

# Whisper transcription functions
# ----------------


model_size = "tiny"

# or run on CPU with INT8


@lru_cache(maxsize=1)
def get_whisper_model(whisper_model: str, device="cpu", compute_type="int8"):
    """Get a whisper model from the cache or download it if it doesn't exist"""
    model = WhisperModel(whisper_model, device=device, compute_type=compute_type)
    return model


def transcribe(audio_path: str, whisper_model: WhisperModel, temperature=0.0):
    """Transcribe the audio file using whisper"""

    model = get_whisper_model(whisper_model)
    transcript = model.transcribe(
        audio_path,
        beam_size=1,
        language='ja',
        vad_filter=True,
        vad_parameters=dict(
            min_silence_duration_ms=400, threshold=0.1, min_speech_duration_ms=50
        ),
        temperature=temperature
    )
    return transcript


UPLOAD_DIR = "./tmp"
router = APIRouter()
router.model_size=model_size


@router.api_route('/v1/audio/transcriptions', methods=["POST"])
async def transcriptions(
        file: UploadFile = File(...),
        model: str = Form('tiny'),
        response_format: Optional[str] = Form(None),
        prompt: Optional[str] = Form(None),
        temperature: Optional[float] = Form(None),
        language: Optional[str] = Form(None)):

    if file is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bad Request, bad file"
        )
    if response_format is None:
        response_format = 'json'
    if response_format not in ['json',
                               'text',
                               'srt',
                               'verbose_json',
                               'vtt']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bad Request, bad response_format"
        )
    if temperature is None:
        temperature = 0.0
    if temperature < 0.0 or temperature > 1.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bad Request, bad temperature"
        )

    filename = file.filename
    fileobj = file.file
    upload_name = os.path.join(UPLOAD_DIR, filename)
    upload_file = open(upload_name, 'wb+')
    shutil.copyfileobj(fileobj, upload_file)
    upload_file.close()

    segments, info = transcribe(
        audio_path=upload_name,
        whisper_model=router.model_size,
        temperature=temperature
    )

    concat_text = "".join([s.text for s in segments])
    print(concat_text)

    # other response no-care
    return JSONResponse(
        content={
            "text": concat_text
        },
        status_code=status.HTTP_200_OK
    )


if __name__ == "__main__":

    import argparse
    import uvicorn
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_size", '-s', type=str, default='tiny')
    parser.add_argument('--port', '-p', type=int, default=8082)

    args = parser.parse_args()
    app = FastAPI()
    router.model_size = args.model_size
    app.include_router(router)

    uvicorn.run(
        app, port=args.port, host="0.0.0.0", log_level="debug"
    )
