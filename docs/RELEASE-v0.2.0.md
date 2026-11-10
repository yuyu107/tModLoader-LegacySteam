# v0.2.0：自动识别兼容版本、多版本备份与三语言提示

旧版 v0.1.0 只支持 tModLoader 2026.8.3.0，游戏更新后可能无法安装。请升级到 v0.2.0。

## 本次更新

- 不再固定 tModLoader 本体整体哈希；沿用支持的 Steamworks 库时，自动定位并更新游戏本体中的 API 校验值。
- 不同游戏文件版本分别保存备份，安装和恢复自动选择，无需删除旧备份。
- 根据系统界面语言自动显示简体中文、繁体中文或英文。
- 保留旧版备份兼容、文件校验、接口预检和恢复功能。

## 安装或升级

1. 关闭 tModLoader，保持 Steam 已登录。
2. 在 Steam 库中右键 tModLoader，选择“管理 → 浏览本地文件”。
3. 下载附件 `tML-Win7-LegacySteam-v0.2.0.zip`，将全部文件解压到该目录，与 `tModLoader.dll` 同级，覆盖旧补丁文件。
4. 运行 `Install-LegacySteam.bat`，看到“安装完成”或 `INSTALLED: 0.2.0` 后正常启动游戏。

无需先恢复原文件，也不要删除 `LegacySteam-Backups`、`LegacySteam-Backup` 或 `LegacySteam-Test1-Backup`。

## Steam 自动更新后

更新或验证文件可能覆盖补丁。关闭游戏，再运行一次新版 `Install-LegacySteam.bat`，脚本会检查并修补支持的文件，自动保留对应版本备份。

三份 Steamworks 库仍严格校验，当前适配 `steamworks.net.anycpu/2025.162.4` 的已知文件。若库本身升级，或本体结构不再符合规则，脚本会停止；请查看新版补丁或反馈日志。自动识别不等于所有未来版本通用。

## 系统、下载与恢复

- Windows 7 SP1 / Windows 8.1 64 位；不支持 32 位系统。Win7 测试环境需要配合 VxKex。
- 模组的 Zstd 下载仍需配合 [SteamLegacyZstd](https://github.com/yuyu107/SteamLegacyZstd)。
- 关闭游戏后运行 `Restore-LegacySteam.bat`，或通过 Steam“验证游戏文件的完整性”恢复官方文件。Steam 验证后可能需要重新修补，额外脚本和备份可能保留。
- 联机、好友邀请、云存档尚未完整验证；尚未逐一验证所有后续 tModLoader 版本。

遇到问题请附系统、Steam、tModLoader 版本及 `tML-LegacySteam-Install.txt`、`tML-LegacySteam-Check.txt`（若生成）。
