from pathlib import Path
from io import BytesIO

from pydub import AudioSegment
from fastapi import FastAPI, Query, Request, status
from fastapi.responses import Response, FileResponse, JSONResponse


class AudioResponse(Response):
    media_type = "audio/wav"


if __name__ == "__main__":

    import argparse
    import tempfile
    import os
    import uvicorn

    parser = argparse.ArgumentParser()
    parser.add_argument("--use_jtalk", '-jtalk', type=bool, default=False)
    parser.add_argument('--tempdir', '-tmp', type=str, default='./tmp')
    parser.add_argument('--jtalk_dic_path', '-jdic', type=str, default='./open_jtalk_dic_utf_8-1.11')
    parser.add_argument('--speaker_id', '-s', type=int, default=2)
    parser.add_argument('--port', '-p', type=int, default=8081)

    args = parser.parse_args()

    temp_dir = os.path.join('./tmp/')
    os.makedirs(temp_dir, exist_ok=True)

    if args.use_jtalk:
        import numpy as np
        from scipy.io import wavfile
        import pyopenjtalk
    else:
        from voicevox_core import VoicevoxCore
        speaker_id = args.speaker_id  # 1:ずんだもん,2:四国めたん
        model = VoicevoxCore(open_jtalk_dict_dir=Path(args.jtalk_dic_path))
        if not model.is_model_loaded(speaker_id):
            model.load_model(speaker_id)

    app = FastAPI()

    @app.api_route("/voice", methods=["GET", "POST"], response_class=AudioResponse)
    async def voice(
        request: Request,
        text: str = Query(..., description="合成音声テキスト"),
    ):
        # 直接出力用
        if not args.use_jtalk:
            return AudioResponse(content=model.tts(text, speaker_id))
        else:
            voice, sr = pyopenjtalk.tts(text)
            with BytesIO() as web_audio:
                wavfile.write(web_audio, sr, voice.astype(np.int16))
                return AudioResponse(content=web_audio.getvalue())


    @app.api_route("/v3/voicevox/synthesis", methods=["POST"])
    async def synthesis(
        request: Request,
    ):
        data = await request.json()
        text = data.get("text")
        print(text)
        if not args.use_jtalk:
            voice = model.tts(text, speaker_id)
            audio_segment = AudioSegment.from_file(BytesIO(voice))
        else:
            voice, sr = pyopenjtalk.tts(text)
            voice = voice.astype(np.int16)
            audio_segment = AudioSegment(
                voice.tobytes(),
                frame_rate=sr,
                sample_width=voice.dtype.itemsize,
                channels=1  # モノラル
            )

        with tempfile.NamedTemporaryFile(dir=temp_dir, delete=False, suffix='.mp3') as temp:
            audio_segment.export(temp.name, format='mp3')
            file_name = temp.name
            print(file_name)

        host = request.headers.get("host")
        base_name = os.path.basename(file_name)
        download_uri = f"{request.url.scheme}://{host}/download/{base_name}"

        return JSONResponse(
            content={
                "success": True,
                "isApiKeyValid": False,
                "speakerName": str(speaker_id),
                "mp3StreamingUrl": download_uri,
                "audioStatusUrl": "",
                "wavDownloadUrl": "",
                "mp3DownloadUrl": "",
            },
            status_code=status.HTTP_200_OK
        )


    @app.get("/download/{file_name}")
    async def download_file(file_name: str, request: Request):
        current = Path()
        file_path = current / temp_dir / file_name
        if not os.path.exists(file_path):
            return JSONResponse(content={"not found": str(request.url)}, status_code=404)
        file_response = FileResponse(file_path)
        file_response.headers["Content-Disposition"] = f"attachment; filename={file_name}"
        return file_response

    uvicorn.run(
        app, port=args.port, host="0.0.0.0", log_level="debug"
    )