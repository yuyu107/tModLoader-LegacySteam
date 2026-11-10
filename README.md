# tModLoader-LegacySteam

为旧版 Steam 客户端适配 tModLoader 的 Steamworks 接口。**v0.2.0 正式版**支持自动识别兼容的 tModLoader 本体版本、多版本备份及简体中文 / 繁体中文 / 英文提示。使用差分补丁修改本地原文件，不分发完整游戏 DLL。

v0.1.0 仅支持 tModLoader 2026.8.3.0，游戏更新后请升级到 v0.2.0，不要继续使用旧安装包。

## 下载与安装

前往 [正式版发布页面](https://github.com/yuyu107/tModLoader-LegacySteam/releases)，下载 v0.2.0 的 `tML-Win7-LegacySteam-v0.2.0.zip`。请下载 Assets 中的安装包，不要下载自动生成的 Source code 压缩包。

1. 关闭 tModLoader，保持 Steam 已登录。
2. 在 Steam 库中右键 tModLoader，选择“管理 → 浏览本地文件”。
3. 将安装包内全部文件解压到该目录，与 `tModLoader.dll` 同级，覆盖旧补丁文件。
4. 运行 `Install-LegacySteam.bat`，看到“安装完成”或 `INSTALLED` 后正常启动游戏。

从 v0.1.0 或 0.2 测试版升级时，不必先恢复原文件，也不要删除备份目录。

## 游戏自动更新后怎么办

Steam 更新 tModLoader 或验证游戏文件，可能会覆盖补丁。关闭游戏、保持 Steam 登录，再运行一次 `Install-LegacySteam.bat` 即可重新检查并修补支持的文件。

新备份保存在 `LegacySteam-Backups/<原游戏文件SHA-256>/`，不同游戏文件版本分别保存。安装与恢复会自动选择对应备份，无需删除或移动旧备份。旧目录 `LegacySteam-Backup`、`LegacySteam-Test1-Backup` 仍可读取，请一并保留。

若提示“不支持的文件”或无法定位校验值，请到发布页面查看新版补丁，并反馈安装日志和 tModLoader 版本。新版 Steamworks 库需要另行适配。

## 兼容范围

- 支持 Windows 7 SP1 / Windows 8.1 **64 位**；tModLoader 不支持 32 位系统。
- Win7 测试环境需要配合 VxKex，本补丁不代替系统兼容层，也不修改 .NET 运行时。
- v0.2.0 不再固定 tModLoader 本体的整体 SHA-256；本体更新但三份 Steamworks 库仍为支持文件时，可按 CLR 用户字符串记录定位原生 API 的预期 MD5 并更新它。
- 三份 Steamworks 库仍严格按 SHA-256 校验，当前适配 `steamworks.net.anycpu/2025.162.4` 的已知文件。不是仅凭目录版本号就允许修补；未知库、强名称签名本体或无法唯一定位的结构会停止。
- 旧版基础适配已在 Win7 / Win8.1 验证启动、模组加载与使用；自动识别安装流程已有成功反馈。尚未逐一验证所有后续 tModLoader 版本，联机、好友邀请、云存档也未完整验证。
- 本补丁不增加 Zstd 下载支持。下载使用 Zstd 压缩的模组时，还需配合 [SteamLegacyZstd](https://github.com/yuyu107/SteamLegacyZstd)。

系统界面语言为简体中文（zh-CN / zh-SG / zh-Hans）时显示简体，繁体中文（zh-TW / zh-HK / zh-MO / zh-Hant）时显示繁体，其余语言显示英文。日志保留 Steam 原始输出和异常信息。

## 恢复与反馈

关闭游戏，运行当前包的 `Restore-LegacySteam.bat`，自动选择对应备份恢复原文件。

也可以在 Steam 的“属性 → 已安装文件”（旧版客户端可能叫“本地文件”）中选择“验证游戏文件的完整性”，重新获取当前分支的官方文件。验证可能移除补丁，也可能更新游戏；补丁脚本和备份等额外文件可能仍会保留。若仍需修补，再运行新版安装脚本。

安装失败请提交 `tML-LegacySteam-Install.txt` 和 `tML-LegacySteam-Check.txt`（若生成）。启动或游戏内出错，请附新生成的 `tModLoader-Logs`、错误截图，以及系统、Steam 和 tModLoader 版本。公开日志前检查账号名、路径和 Steam ID。

用户端不需要 Python；脚本按 Win7 Windows PowerShell 2.0 编写。运行时请与 Steam 保持相同权限。

## 修改内容

- **好友接口**：使用 `SteamFriends017`。SDK 1.62 的 `SteamFriends018` 删除了旧接口中的两个函数，补丁为新导出的好友函数重新映射旧虚函数位置，保留原来被链接器合并的函数体。
- **创意工坊 UGC**：使用 `STEAMUGC_INTERFACE_VERSION020`。现有函数位置与 SDK 1.62 一致；旧客户端没有的本地禁用、订阅排序功能返回不可用。
- **Remote Play**：使用 `STEAMREMOTEPLAY_INTERFACE_VERSION002`，适配旧版 UI 调用；新版直接输入功能返回不可用。
- **时间线**：允许时间线接口缺失，对应导出返回零或不执行操作。录像时间线功能不可用。
- **文件完整性**：更新 `tModLoader.dll` 中的一个预期 MD5 常量，使其精确匹配补丁版 `steam_api64.dll`。`HashMatchesFile`、`CheckSteam` 方法和泰拉瑞亚安装、Steam 授权检查保持原样。

改动不代表上述尚未实测功能已兼容，也不保证所有第三方模组对新版 Steam API 的直接调用可用。

## 源码与构建

构建环境使用现代 Python；这是开发者要求，用户运行安装包不需要它。

```sh
python -m pip install -r requirements.txt
python tools/build.py --game-dir /path/to/pristine/tModLoader --output build
python tools/verify.py --game-dir /path/to/pristine/tModLoader --build-dir build
```

输入需为本次支持版本的原文件。构建需要 `tModLoader.dll` 和 `Libraries/steamworks.net.anycpu/2025.162.4` 中两个托管 DLL 及 Windows x64 原生 DLL。若已安装补丁，可以使用保留的原文件备份构建，目录结构需保持一致。

仅重新打包仓库内已校验的差分数据，无需提供游戏 DLL：

```sh
python tools/package.py --output build/release
```

输出包括修改后的文件、差分数据、改动记录和 ZIP。完整原文件及修改后的 DLL 只存在于本地构建目录，不提交到仓库。

| 路径 | 内容 |
| --- | --- |
| `tools/build.py` | 托管元数据/IL 与原生导出适配、精确游戏哈希更新 |
| `tools/interface_layouts.json` | 对照 SDK 1.60 / 1.62 的函数顺序 |
| `tools/delta.py` | 差分数据编码与解码 |
| `tools/package.py` | 生成校验清单和可分发 ZIP |
| `tools/verify.py` | 验证差分重建、导出映射和文件校验 |
| `runtime/` | PowerShell 2.0 安装、恢复、接口预检与 C# 差分应用源码 |
| `patches/2026.8.3.0/` | 本次支持版本的差分数据与 SHA-256 清单 |
| `packages/` | 不包含完整 DLL 的差分安装包 |

## 参考与许可证

接口顺序参考 [SteamworksSDK 1.60](https://github.com/rlabrecque/SteamworksSDK/tree/e7bb839178fc/public/steam) 与 [1.62](https://github.com/rlabrecque/SteamworksSDK/tree/34d9338aa892/public/steam)。相关项目：

- [tModLoader](https://github.com/tModLoader/tModLoader)
- [Steamworks.NET](https://github.com/rlabrecque/Steamworks.NET)
- [SteamLegacyZstd](https://github.com/yuyu107/SteamLegacyZstd)

本项目原创脚本、工具代码及文档采用 [MIT 许可证](LICENSE)，版权署名为 `Copyright (c) 2026 yuyu107`。

第三方游戏、Steamworks 库、SDK 及其他第三方内容不在本项目的 MIT 授权范围内，其权利和使用条件由原权利人规定。差分补丁中涉及的第三方内容也不因本项目采用 MIT 而获得重新授权。

本仓库未包含完整 SDK 头文件、完整游戏 DLL、账号数据或 Steam 客户端文件。
