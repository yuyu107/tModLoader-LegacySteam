# tModLoader-LegacySteam

为旧版 Steam 客户端适配 tModLoader 的 Steamworks 接口。v0.1.0 正式版已发布，并通过 Windows 7 / 8.1 64 位实测，使用差分补丁修改本地原文件，不分发完整游戏 DLL。

## 下一版测试：自动识别游戏本体

`v0.2.0-test1` 允许 tModLoader 本体 SHA-256 变化，但三份 Steamworks 库仍必须与 v0.1.0 支持的原文件或补丁文件逐字节一致。安装器解析 PE / CLR 的 `#US` 用户字符串堆，要求原生库的预期 MD5 恰好出现一次，只替换这一条字符串；不关闭完整性或授权检查。新版 Steamworks 库、签名游戏程序集或未知元数据会停止安装。

这只是兼容识别规则，不保证未来游戏逻辑或第三方模组兼容。测试版尚未完成 Windows 实机验证，正式 Release 仍为 v0.1.0。请先在当前版本测试安装、重复安装、启动及恢复。

备份中新增 `GameFingerprint-state.txt`，记录本次游戏原文件和修改结果的 SHA-256；恢复时校验备份。游戏更新后如备份属于旧版本，安装器会停止并提示保留旧备份后移出游戏目录，避免覆盖旧版本备份。

## 当前状态

| 项目 | 已验证范围 |
| --- | --- |
| 系统 | Windows 7 SP1 64 位、Windows 8.1 64 位 |
| Steam | `1730853000`，2024 年 11 月客户端 |
| tModLoader | `2026.8.3.0`，日志显示 `1.4.4.9+2026.08.3.0` |
| Steamworks.NET.AnyCPU | `2025.162.4` |
| 启动 | 已在 Windows 7 / 8.1 64 位成功启动 |
| 创意工坊模组下载 | 配合 [SteamLegacyZstd](https://github.com/yuyu107/SteamLegacyZstd) 成功下载 |
| 模组加载和使用 | 已通过实测 |
| Steam 联机、好友邀请、云存档 | 尚未验证 |
| 本仓库差分安装器 | 输出与已实测 Test2 逐字节一致；v0.1.0 已通过 Windows 7 / 8.1 实测 |

tModLoader 不支持 32 位 Windows，本补丁也不提供 32 位系统支持。Win7 测试环境需要配合 VxKex；本补丁不替代系统兼容层。

目前只针对上述文件版本。安装器通过 SHA-256 识别输入和输出，不会强行修改未知版本。

## 下载与安装

前往 [v0.1.0 正式版 Release](https://github.com/yuyu107/tModLoader-LegacySteam/releases/tag/v0.1.0)，下载 Assets 中的 [安装包 ZIP](https://github.com/yuyu107/tModLoader-LegacySteam/releases/download/v0.1.0/tML-Win7-LegacySteam-v0.1.0.zip)（[SHA-256 校验文件](packages/tML-Win7-LegacySteam-v0.1.0.sha256.txt)）。请下载安装包，而非 GitHub 自动生成的 Source code 压缩包。

1. 关闭 tModLoader，保持 Steam 登录。
2. 在 Steam 库中右键 tModLoader，选择“管理 → 浏览本地文件”，打开安装目录。
3. 将安装包全部解压到 tModLoader 根目录，与 `tModLoader.dll` 同级。
4. 双击 `Install-LegacySteam.bat`，看到 `INSTALLED` 后正常启动游戏。
5. 先验证主菜单和模组加载，再测试创意工坊。

只安装本补丁不会增加 Zstd 下载支持。下载使用 Zstd 压缩的模组时，还需按 [SteamLegacyZstd](https://github.com/yuyu107/SteamLegacyZstd) 的说明使用下载补丁。

从 Test1 / Test1-r2 / Test2 升级时，保留原来的 `LegacySteam-Test1-Backup`。安装器可从该备份读取原文件，不必先恢复。新安装生成 `LegacySteam-Backup`，请保留。

脚本兼容 Win7 默认的 Windows PowerShell 2.0 / .NET Framework 环境，用户端不需要 Python。运行时请与 Steam 保持相同权限。本补丁不安装或修改 tModLoader 的 .NET 运行时。

## 恢复与反馈

关闭游戏，运行本包的 `Restore-LegacySteam.bat`，恢复原来的四个文件。Steam 验证文件或更新游戏可能覆盖补丁；不同版本需重新适配。

安装阶段失败请提交：

- `tML-LegacySteam-Install.txt`
- `tML-LegacySteam-Check.txt`（若已生成）

启动或游戏内出错，请提交新生成的 `tModLoader-Logs` 和错误截图，同时说明 Steam、系统、tModLoader 版本。公开日志前请检查其中的账号名、路径和 Steam ID。

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
