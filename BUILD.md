# Build / 构建说明

本仓库的 `.usm` 静态背景是这样生成的（脚本未包含在仓库内，流程可复现）：

1. **取图**：从游戏选歌素材（曲绘 `SONG_BG` / 封面 `SONG_JK`）解出每首歌的图片；解不出时用灰底 + 歌名卡片兜底
2. **合成**：曲绘铺满 1920×1080 + 封面竖条 + 歌名/署名（PIL 绘制），整体压暗到 YAVG≈45
3. **转视频**：用 ffmpeg 把 PNG 做成 **6 帧 / 30fps 静音 mp4**
   ```
   ffmpeg -loop 1 -i cover.png -f lavfi -i anullsrc=r=44100:cl=stereo \
          -frames:v 6 -r 30 -shortest -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 128k out.mp4
   ```
4. **转 USM**：用 [WannaCri GUI](https://github.com/hiki8man/Wannacri_GUI) 的命令行（**必须从工具目录启动**，它按相对路径找 ffmpeg）：
   ```
   cd <WannaCri 工具目录>
   convert_GUI.exe out.mp4 -vp9 -vol 60 -crf 16 -brightness 100 -output <输出目录>
   ```
   得到与游戏原厂文件同结构的 CRI USM（`CRID + @SFV×4 + 大块 + 尾部帧块 + CONTENTS END`）
5. **落位**：把产物重命名为 `pv_XXXXX.usm`，覆盖到 `mods/DarkMV/rom/movie/`

## 为什么不能手搓 USM

实测（大量对比）：把 ffmpeg 自编的 VP9 帧手工拼进原厂容器，游戏**一律拒绝**——大块布局黑屏、逐帧布局卡加载；只有 CRI 原厂编码或 WannaCri 转换出来的流才能正常播放。所以必须经过第 4 步。

## 备注

- 游戏对静态视频的时长没有要求：6 帧（167ms）的静态图能整首显示
- 曲绘贴图解析存在限制：部分素材只能拿到单通道信息，合成图会偏绿（见 README 已知问题）
