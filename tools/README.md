# 工具说明（tools/）

本目录是**生成工具**：用自己的游戏/曲包环境，生成自己专属的静态背景 Mod。
仓库里不再包含现成的 `.usm` 素材。

## 依赖

- Python 3.9+
- [Pillow](https://pypi.org/project/Pillow/)（`pip install pillow`）
- ffmpeg（WannaCri GUI 自带，在 `<工具目录>/ffmpeg/ffmpeg.exe`；也可用系统 ffmpeg）
- [WannaCri GUI](https://github.com/hiki8man/Wannacri_GUI)（hiki8man）—— 负责把视频转成游戏认的 CRI USM

## 流程一：用自己准备的图片

1. 准备图片，按 `pv_编号.png` 命名（例如 `pv_6167.png`；编号即游戏里的 PV 编号）
   - 不知道编号？游戏内选歌时按 `F2`？不行的话：用 DivaModManager 看歌曲列表，或在 `mods/*/rom/mod_pv_db.txt` 里搜歌名，`pv_XXXXX.song_name=` 前面就是编号
2. 生成：
```bat
python tools\build_from_images.py ^
  --images D:\my_covers ^
  --wannacri C:\path\to\wannacri_qt ^
  --out  mods\DarkMV\rom\movie ^
  --gray --dim 0.85 ^
  --font  C:\Windows\Fonts\YuGothM.ttc ^
  --title-csv titles.csv
```
   - `titles.csv` 可选，格式：`pv,标题,署名`（例如 `6167,おじゃま虫,DECO*27`）
   - `--gray` 去色、`--dim 0.85` 压暗 15%；不加则保留原色
3. 生成的 `mods/DarkMV/rom/movie/pv_*.usm` 就是背景文件；配合 `mods/BgToggle`（F10 开关）即可

## 流程二：从已有 USM 反导出图片再修改

```bat
python tools\usm_to_images.py --usm "F:\SteamLibrary\...\mods\DarkMV\rom\movie" --out D:\exported
```
得到每首歌的关键帧 PNG，改完再用流程一生成回去。

## 写进 / 写出 MOD 的目录结构

```
mods/
  DarkMV/
    config.toml
    rom/movie/pv_*.usm
  BgToggle/
    config.toml
    BgToggle.dll
```

## 注意

- `convert_GUI.exe` 必须**从它自己的目录启动**（按相对路径找 ffmpeg），脚本已处理
- 转换是逐首调用，单首约 3–10 秒；建议串行跑，避免窗口/内存压力
- 一张图 = 6 帧（167ms）就够：游戏会持续显示，不需要长视频
- 素材来自你自己的游戏/曲包，**不要二次分发**
