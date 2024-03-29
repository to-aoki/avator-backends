参考: https://qiita.com/ueponx/items/186a7c859b49d996785f

```
wget https://github.com/VOICEVOX/voicevox_core/releases/download/0.15.2/voicevox_core-0.15.2+cpu-cp38-abi3-linux_aarch64.wh
pip install voicevox_core-0.15.2+cpu-cp38-abi3-linux_aarch64.whl 

# pydantic が 1.xに下がるので上げる。バージョン依存はしてなさそう？
pip install pydantic -U

# onnx1.13.1依存は変わってない
wget https://github.com/microsoft/onnxruntime/releases/download/v1.13.1/onnxruntime-linux-aarch64-1.13.1.tgz
tar xvzf onnxruntime-linux-aarch64-1.13.1.tgz 
ln -s onnxruntime-linux-aarch64-1.13.1/lib/libonnxruntime.so.1.13.1 

wget https://jaist.dl.sourceforge.net/project/open-jtalk/Dictionary/open_jtalk_dic-1.11/open_jtalk_dic_utf_8-1.11.tar.gz
tar xzvf open_jtalk_dic_utf_8-1.11.tar.gz
```

```
$ cat voicevox_test.py 
from pathlib import Path
from voicevox_core import VoicevoxCore, METAS
import sys, os

core = VoicevoxCore(open_jtalk_dict_dir=Path("./open_jtalk_dic_utf_8-1.11"))
speaker_id = 2 # 1:ずんだもん,2:四国めたん

text = sys.argv[1]

import time
start = time.time()
if not core.is_model_loaded(speaker_id):
    core.load_model(speaker_id)
print('load: ', time.time() -start)

start = time.time()
wave_bytes = core.tts(text, speaker_id)
print('tts:', time.time() -start)
start = time.time()
with open("./" + text + ".wav", "wb") as f:
    f.write(wave_bytes)
print('write:', time.time() -start)
$ python voicevox_test.py おはようございます
load:  2.777759075164795
tts: 2.4518849849700928
write: 0.00024318695068359375
```

```
$ uname -a
Linux raspberrypi 6.6.20+rpt-rpi-2712 #1 SMP PREEMPT Debian 1:6.6.20-1+rpt1 (2024-03-07) aarch64 GNU/Linux
$ python --version
Python 3.11.2
$ pip list
Package            Version
------------------ --------------
annotated-types    0.6.0
anyio              4.3.0
av                 11.0.0
certifi            2024.2.2
charset-normalizer 3.3.2
click              8.1.7
coloredlogs        15.0.1
ctranslate2        4.1.0
diskcache          5.6.3
fastapi            0.110.0
faster-whisper     1.0.1
filelock           3.13.1
flatbuffers        20181003210633
fsspec             2024.3.1
h11                0.14.0
huggingface_hub    0.21.4
humanfriendly      10.0
idna               3.6
Jinja2             3.1.3
llama_cpp_python   0.2.57
MarkupSafe         2.1.5
mpmath             1.3.0
numpy              1.26.4
onnxruntime        1.17.1
packaging          24.0
pip                23.0.1
protobuf           5.26.0
pydantic           2.6.4
pydantic_core      2.16.3
pydantic-settings  2.2.1
pyopenjtalk        0.3.3
python-dotenv      1.0.1
PyYAML             6.0.1
requests           2.31.0
scipy              1.12.0
setuptools         66.1.1
six                1.16.0
sniffio            1.3.1
sse-starlette      2.0.0
starlette          0.36.3
starlette-context  0.3.6
sympy              1.12
tokenizers         0.15.2
tqdm               4.66.2
typing_extensions  4.10.0
urllib3            2.2.1
uvicorn            0.29.0
voicevox_core      0.15.2+cpu
```