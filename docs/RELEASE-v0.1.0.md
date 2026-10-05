# tModLoader-LegacySteam v0.1.0

为旧版 Steam 适配 tModLoader 的 Steamworks 接口，支持本次实测环境：Windows 7 SP1 64 位、Steam 1730853000（2024 年 11 月）、tModLoader 2026.8.3.0。

## 下载与安装

下载 `tML-Win7-LegacySteam-v0.1.0.zip`，完整解压到 tModLoader 根目录，与 `tModLoader.dll` 同级。关闭游戏、保持 Steam 登录，运行 `Install-LegacySteam.bat`，看到 `INSTALLED: 0.1.0` 后正常启动游戏。已安装相同补丁的环境会提示 `Already installed: 0.1.0`。

安装器校验文件版本并备份原文件；请保留 `LegacySteam-Backup`。关闭游戏后运行 `Restore-LegacySteam.bat` 可恢复。旧 Test1 / Test2 用户请保留 `LegacySteam-Test1-Backup`。

## 功能与验证范围

- 适配旧版好友、UGC、Remote Play 接口，允许缺失时间线接口。
- 沿用已成功启动、下载及使用模组的 Test2 修改结果。
- 使用差分补丁，不包含完整游戏或 Steamworks DLL。
- 模组的 Zstd 下载需配合 [SteamLegacyZstd](https://github.com/yuyu107/SteamLegacyZstd)。
- 新差分安装器尚待 Win7 实机验证；Steam 联机、好友邀请和云存档尚未验证。
- 仅支持清单中的文件版本，游戏更新后可能需要重新适配。

原创代码及文档采用 MIT；第三方内容的授权范围见 README。
