# avator-backends

## これは

2023-2024に流行っている任意のアバター向け ASR-LLM-TTS 3点セットになります。

https://github.com/to-aoki/M5Stack_Stack-chan_another_dimension 用のバックエンドプログラムです。ｽﾀｯｸﾁｬﾝｶﾜｲｲ

## 動作環境
Raspberry PI 5 v1.0で動作確認しています（試してないですがどれでも動くと思います）。

## LLM？

OpenAI Chat API v1 Compatible なものを利用するものが多いと思います(mlc-llmやvllm）。

llama.cpp pythonの場合は、以下のようになります（例えばgemma2b-it）。

```bash
python3 -m llama_cpp.server --chat_format=gemma --model models/gemma-2b-it.Q2_K.gguf --host=0.0.0.0
```



