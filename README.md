# PJDV_CoverBackground — MM+ 背景替换工具

《初音未来 歌姬计划 MEGA39's+ / Mega Mix+》（Steam）用**背景替换工具**：
把任意图片批量转成游戏认的静态背景 USM，覆盖视频类（2D）歌曲的 MV。
配合附带的 `BgToggle`，游戏内 **F10** 一键开关。

> 本仓库**不附带任何现成素材**（曲绘版权归原厂/绘师）。你需要用自己的图片或从自己的游戏环境导出。
> 仅供个人使用，请勿分发从游戏提取的素材，成绩请勿上传排行榜。

## 它能做什么

- 视频类（2D）歌曲：MV 换成你给的静态图（铺满 16:9，可压暗/去色/加标题署名）
- 动态效果没有，整首显示同一张图（游戏会持续显示，不需要长视频）
- 3D 歌曲不受影响
- 随时可关：`BgToggle` 的 F10 面板，或 DivaModManager 停用 `DarkMV`

## 快速开始

1. 安装 [DivaModLoader](https://github.com/blueskythlikesclouds/DivaModLoader)（`dinput8.dll` 放游戏根目录）或 [DivaModManager](https://gamebanana.com/tools/9712)
2. 下载 [WannaCri GUI](https://github.com/hiki8man/Wannacri_GUI)（Releases 里的 `wannacri_qt_zh_cn.7z`，解压到任意目录）
3. `pip install pillow`
4. 准备图片：`pv_编号.png`（编号查法见 [tools/README.md](tools/README.md)）
5. 生成：
```bat
python tools\build_from_images.py ^
  --images D:\my_covers ^
  --wannacri C:\path\to\wannacri_qt ^
  --out  mods\DarkMV\rom\movie ^
  --gray --dim 0.85 --font C:\Windows\Fonts\YuGothM.ttc --title-csv titles.csv
```
6. 把 `mods\DarkMV` 和 `mods\BgToggle` 复制进游戏的 `mods/` 目录，启动游戏

## 目录

```
tools/
  build_from_images.py   图片 → 6 帧静音 mp4 → WannaCri 转 USM（批量）
  usm_to_images.py       已有 USM → 导出关键帧 PNG（二次修改用）
  README.md              详细用法
mods/
  DarkMV/                config.toml（rom/movie 下放生成的 pv_*.usm）
  BgToggle/              F10 开关插件（dll + config）
src/                     BgToggle 源码（C++，DivaModLoader 插件模板写法）
```

## 原理 & 已知限制

游戏只认 CRI 原厂编码的 USM：用 ffmpeg 自己拼帧塞进容器，游戏会黑屏或卡加载。
所以必须走 WannaCri 转换（细节见 [tools/README.md](tools/README.md)）。

- 静态图 6 帧（167ms）即可，游戏会整首保持显示
- 转换逐首进行，单首约 3–10 秒
- 生成的 USM 只在你自己的曲包环境下有效（pv 编号对应你安装的曲包）

## 致谢

- [DivaModLoader](https://github.com/blueskythlikesclouds/DivaModLoader)
- [DivaModManager](https://gamebanana.com/tools/9712)
- [WannaCri GUI](https://github.com/hiki8man/Wannacri_GUI)（hiki8man）

## 让 AI 帮你做（推荐）

本仓库的整套流程就是和 AI 助手（DSH,ZCODE）一起做出来的。
你不需要懂脚本，把下面这段**整段复制**给 AI，填好开头的三个路径即可：

```text
你是一个 Windows 上的 Mod 制作助手。目标：为《初音未来 歌姬计划 Mega Mix+》做"每首歌专属静态背景"DLC（DarkMV mod）。

先读这两个文件再动手：
- https://github.com/FlourishingBlossoms/PJDV_CoverBackground 的 README.md
- 同仓库 tools/README.md

环境：
- 游戏目录：<例如 F:\SteamLibrary\steamapps\common\Hatsune Miku Project DIVA Mega Mix Plus>
- WannaCri GUI 目录：<例如 C:\Users\你\Downloads\wannacri_qt_zh_cn>（内含 convert_GUI.exe 和 ffmpeg\ 文件夹）
- 图片来源：<A. 我提供图片文件夹  B. 从我的游戏素材导出  C. 让我逐首给你截图>

请按步骤执行，每步完成告诉我结果：
1. 建索引：扫描 游戏目录\mods\*\rom\mod_pv_db*.txt，解析 "pv_XXXX.song_name=" 行，生成"歌名 → pv 编号 → 所属曲包"的 CSV/表格
2. 准备图片：按 pv_编号.png 命名，铺满 1920x1080（图片方案 B 时，用 tools/usm_to_images.py 从已有 DarkMV usm 导出，或从曲包素材解析）
3. 生成：调用 tools/build_from_images.py，参数按需（--gray 去色、--dim 0.9 压暗、--title-csv 加歌名/署名、--font 指定中文字体）
4. 安装：把生成的 pv_*.usm 放进 游戏目录\mods\DarkMV\rom\movie\；确认 DarkMV\config.toml 里 enabled=true；如缺 BgToggle 就从仓库复制 mods\BgToggle 过去
5. 校验：逐个检查 usm 大小 >2KB、可解析、帧数 ≤10；输出成功/失败清单（失败的单独重跑）
6. 汇报：告诉我进哪几首歌验收、怎么回滚（删 mods\DarkMV 或 F10 关闭）

硬性约束：
- 只改 游戏目录\mods\ 下的文件，绝不碰游戏本体 exe/cpk/存档
- convert_GUI.exe 必须从它自己的目录启动（它按相对路径找 ffmpeg）
- 转换串行跑（单首 3-10 秒），不要同时开多个转换窗口
- 游戏在运行时先让我退出，再写 mods
- 素材只在我本机使用，不上传
```

AI 做不到或写错时，按 [tools/README.md](tools/README.md) 手动执行同样的步骤即可。

## 许可

MIT（见 [LICENSE](LICENSE)）。生成的 `.usm` 素材来自你自己的游戏环境，不在 MIT 授权范围内。
