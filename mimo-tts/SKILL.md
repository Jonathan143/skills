---
name: mimo-tts
description: 用于通过小米 MiMo TTS API 执行流式文本转语音（stream=true, pcm16）。当用户提到 MiMoTTS、mimo-v2-tts、流式语音合成、风格控制（<style>）、音频标签细粒度控制、或需要脚本直接生成语音文件时，优先使用本技能。
---

# MiMo TTS Skill (Streaming Only)

## 目标
帮助用户通过脚本完成 MiMo 流式语音合成，并输出可播放的音频文件（支持 wav/ogg/mp3 等格式, 默认 ogg）。

## 脚本文件
- `scripts/mimo_tts_stream.py`

## 先做检查
- API Base URL: `https://api.xiaomimimo.com/v1`
- Model: `mimo-v2-tts`
- Auth Env: `MIMO_API_KEY`
- Audio Format: `pcm16`
- Stream: `true`

## 核心约束
1. 待合成文本必须放在 `messages` 的 `role="assistant"` 中。
2. 流式请求必须使用 `audio.format="pcm16"`。
3. 当前仅支持模型 `mimo-v2-tts`。
4. 当前不支持音色克隆。

## 音色映射
- `mimo_default`
- `default_zh`
- `default_en`

## 风格控制

### 语音整体风格控制
1. 格式规则：将 `<style>style</style>` 置于转换目标文本开头，`style` 为需要生成的音频风格；如需设置多种风格，将多个风格名称置于同一个 `<style>` 标签内，分隔符不限。
2. 格式示例：`<style>风格1 风格2</style>待合成内容`
3. 推荐风格列表（支持使用不在列表中的风格）：

| 风格类型 | 风格示例 |
| ---- | ---- |
| 语速控制 | 变快/变慢 |
| 情绪变化 | 开心/悲伤/生气 |
| 角色扮演 | 孙悟空/林黛玉 |
| 风格变化 | 悄悄话/夹子音/台湾腔 |
| 方言 | 东北话/四川话/河南话/粤语 |

4. 实际使用样例：
`<style>开心</style>明天就是周五了，真开心！`
`<style>东北话</style>哎呀妈呀，这天儿也忒冷了吧！你说这风，嗖嗖的，跟刀子似的，割脸啊！`
`<style>粤语</style>呢个真係好正啊！食过一次就唔会忘记！`
`<style>唱歌</style>原谅我这一生不羁放纵爱自由，也会怕有一天会跌倒，Oh no。背弃了理想，谁人都可以，哪会怕有一天只你共我。`

### 音频标签细粒度控制
通过音频标签可对声音进行细粒度控制，精准调节语气、情绪和表达风格，也可灵活插入呼吸声、停顿、咳嗽等音效，语速也能灵活调整。

使用样例：
`（紧张，深呼吸）呼……冷静，冷静。不就是一个面试吗……（语速加快，碎碎念）自我介绍已经背了五十遍了，应该没问题的。加油，你可以的……（小声）哎呀，领带歪没歪？`
`（极其疲惫，有气无力）师傅……到地方了叫我一声……（长叹一口气）我先眯一会儿，这班加得我魂儿都要散了。`
`如果我当时……（沉默片刻）哪怕再坚持一秒钟，结果是不是就不一样了？（苦笑）呵，没如果了。`
`（寒冷导致的急促呼吸）呼——呼——这、这大兴安岭的雪……（咳嗽）简直能把人骨头冻透了……别、别停下，走，快走。`
`（提高音量喊话）大姐！这鱼新鲜着呢！早上刚捞上来的！哎！那个谁，别乱翻，压坏了你赔啊？！`

## 脚本调用示例（仅流式）
先安装依赖：
```bash
pip install openai numpy soundfile
```

### 1) 单个整体风格
```bash
export MIMO_API_KEY="<your_key>"
python scripts/mimo_tts_stream.py \
  --text "明天就是周五了，真开心！" \
  --style 开心 \
  --voice default_zh \
  --output happy_style.wav
```

### 2) 一个 `<style>` 标签内多个风格
```bash
python scripts/mimo_tts_stream.py \
  --text "今天状态非常在线。" \
  --styles 开心 变快 \
  --voice mimo_default \
  --output multi_styles_one_tag.ogg
```

### 3) 一段文本包含多个 `<style>` 分段
当文本里已经写好多个 `<style>` 标签时，直接传原文，不要再叠加 `--style/--styles`：
```bash
python scripts/mimo_tts_stream.py \
  --text "<style>开心</style>明天就是周五了，真开心！<style>东北话</style>哎呀妈呀，这天儿也忒冷了吧！<style>粤语</style>呢个真係好正啊！" \
  --voice mimo_default \
  --output mixed_style_segments.ogg
```

### 4) 细粒度音频标签长文本（推荐 text file）
将文本写入 `input.txt` 后调用（同时指定输出 mp3 格式）：
```bash
python scripts/mimo_tts_stream.py \
  --text-file input.txt \
  --voice mimo_default \
  --format mp3 \
  --output fine_grained_tags.mp3
```

## 结果保存与验证
- 可通过 `--format` 参数指定音频格式（支持 wav/ogg/mp3，默认 ogg）。
- 输出文件名可通过 `--output` 自定义，未指定时默认为 `stream_output.<format>`。
- 生成后可直接播放对应格式文件以验证。

## 易错点
- 未设置 `MIMO_API_KEY`。
- 文本已包含 `<style>` 时又传 `--style/--styles`（脚本会报错）。
- 流式场景误用非 `pcm16` 格式。
- 合成文本未放在 `assistant` 角色（脚本内部已固定为 `assistant`）。

## 失败恢复策略
1. 检查 `MIMO_API_KEY` 是否存在。
2. 检查 `model` 是否为 `mimo-v2-tts`。
3. 检查是否使用 `stream=true` 且 `pcm16`。
4. 检查 Base URL 是否为 `https://api.xiaomimimo.com/v1`。
5. 如需多段风格，优先在文本中显式写 `<style>...</style>` 标签。

## 边界说明
- 不输出非流式请求方案。
- 不编造未声明的模型或音色。
- 用户要求不受支持能力时，先说明限制再给替代方案。
