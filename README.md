# DIVA Background Swap — MM+ 2D 背景替换

《初音未来 歌姬计划 MEGA39's+ / Mega Mix+》（Steam）用 Mod：把**视频类（2D）歌曲的 MV 替换成每首歌自己的静态背景图**——曲绘铺满全屏 + 封面竖条 + 歌名/署名，整体压暗，接近练习模式那种"暗背景但音符清晰"的观感。

> ⚠️ **免责声明 / 使用须知**
> 本 Mod 仅供**个人练习/观赏**使用，请勿商用或把素材二次分发。
> 背景图由游戏内选歌素材（曲绘/封面）生成，版权归原厂与各曲绘师所有；本仓库仅作同好交流，请勿用于任何商业用途。
> 使用本 Mod 产生的成绩**请勿上传排行榜**或作为真实力展示。

---

## 内容

| 模组 | 作用 |
|---|---|
| `mods/DarkMV` | 覆盖全部视频类（2D）歌曲的 `rom/movie/pv_*.usm`，换成该曲的静态合成图 |
| `mods/BgToggle` | **F10** 游戏内面板：一键开关 DarkMV（重启后生效），免去进 DivaModManager |

> 📦 **开箱即用下载**：[Releases](https://github.com/FlourishingBlossoms/PJDV_CoverBackground/releases)（`DIVA-BackgroundSwap-mods.zip`，含两个模组文件夹，解压后放进 `mods/` 即可）
> 仓库内 `.usm` 走 Git LFS，直接 clone 会消耗 LFS 流量，**建议优先下 Release**。

- 3D 歌曲（实时渲染舞台）**不受影响**，本 Mod 只处理视频类 MV
- 原版 MV 随时可恢复：BgToggle 里关掉，或在 DivaModManager 停用 DarkMV

## 安装

1. 安装 [DivaModLoader](https://github.com/blueskythlikesclouds/DivaModLoader)（`dinput8.dll` 放游戏根目录），或用 [DivaModManager](https://gamebanana.com/tools/9712) 管理
2. 把本仓库 `mods/` 下的 `DarkMV` 和 `BgToggle` 两个文件夹复制到游戏的 `mods/` 目录
3. 启动游戏

Steam Deck / Linux 启动项需加：`WINEDLLOVERRIDES='dinput8.dll=n,b' %command%`

**卸载**：删除 `mods/DarkMV`、`mods/BgToggle` 即可完全恢复原版 MV。

## 使用

- **F10**：BgToggle 面板，切换 DarkMV 开/关（**重启游戏生效**）
- 进入任意 2D 歌：背景就是该曲的静态合成图（整首保持在）
- 想换回原版 MV：F10 关掉 DarkMV 后重启

## 已知问题

- 约 9 个**非歌曲**视频文件（OP/Logo/广告片/舞台预览）没有替换，属正常
- 3 首歌（白雪 / 下弦の月 / 阿吽のビーツ）使用"灰底 + 歌名"卡片（曲绘素材解析失败）
- 曲绘贴图仅能提取到单通道信息，合成图呈**绿色调**（后续版本可能改进）
- 不是所有歌都 100% 完美：个别歌曲的曲绘可能取到的是封面而非插画

## 构建说明

见 [BUILD.md](BUILD.md)（图片 → 6 帧静音 mp4 → WannaCri GUI 转 CRI USM → 覆盖 `rom/movie/pv_*.usm`）。

## 致谢

- [DivaModLoader](https://github.com/blueskythlikesclouds/DivaModLoader)（blueskythlikesclouds）
- [DivaModManager](https://gamebanana.com/tools/9712)（TekkaGB）
- [WannaCri GUI](https://github.com/hiki8man/Wannacri_GUI)（hiki8man）—— USM 转换
- hiki8man 的 USM Tool 相关经验、社区逆向资料

## 许可

MIT（见 [LICENSE](LICENSE)）。注意：仓库内 `.usm` 素材来自游戏本体，不在 MIT 授权范围内，仅供个人使用。
