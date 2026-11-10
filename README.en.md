# tModLoader-LegacySteam

[简体中文](README.md) | English

Steamworks compatibility patches for running tModLoader with older Steam clients. **Stable release v0.2.0** provides automatic detection of compatible game assemblies, separate backups for each game file version, and Simplified Chinese / Traditional Chinese / English prompts. Sparse patches modify your local files; complete game DLLs are not distributed.

v0.1.0 supports only tModLoader 2026.8.3.0. If a game update prevents the old installer from working, upgrade to v0.2.0.

## Download and install

Open the [release page](https://github.com/yuyu107/tModLoader-LegacySteam/releases) and download `tML-Win7-LegacySteam-v0.2.0.zip` from the v0.2.0 **Assets** section. Use the installer ZIP, not GitHub's automatically generated Source code archives.

1. Close tModLoader and keep Steam signed in.
2. In your Steam Library, right-click tModLoader and select **Manage → Browse local files**.
3. Extract every file from the ZIP into that folder, alongside `tModLoader.dll`. Replace old patch files when prompted.
4. Run `Install-LegacySteam.bat`. Once it reports `INSTALLED` or the equivalent localized success message, start tModLoader normally.

When upgrading from v0.1.0 or a 0.2 test build, you do not need to restore the original files first. Keep your backup folders.

## After Steam updates the game

Updating tModLoader or verifying its files can overwrite the patch. Close the game, keep Steam signed in, and run `Install-LegacySteam.bat` again to check and patch supported files.

Backups are stored under `LegacySteam-Backups/<original-game-file-SHA-256>/`, separately for each game file version. Installation and restoration automatically select the matching backup. There is no need to delete or move older backups. The legacy folders `LegacySteam-Backup` and `LegacySteam-Test1-Backup` are also supported and should be kept.

If the installer reports an unsupported file or cannot locate the expected fingerprint, check the release page for an updated patch and report the installation log and your tModLoader version. Updated Steamworks libraries require additional adaptation.

## Compatibility

- Windows 7 SP1 / Windows 8.1 **64-bit**. tModLoader does not support 32-bit Windows.
- v0.2.0 no longer requires one fixed SHA-256 for the entire `tModLoader.dll`. When the game assembly changes but the three Steamworks libraries remain supported, it locates the expected native API MD5 in CLR user-string metadata and updates that value.
- The three Steamworks libraries still require exact SHA-256 matches. Current patches target known files under `steamworks.net.anycpu/2025.162.4`; the folder version alone is insufficient. Unknown libraries, strong-name-signed game assemblies, and structures without one unique matching fingerprint are rejected.
- The original compatibility adaptation has been tested for startup, mod loading, and gameplay on Win7 / Win8.1. Successful installation with automatic game detection has also been reported. Not every later tModLoader version has been tested. Multiplayer, friend invitations, and cloud saves have not been fully verified.
- This patch does not add Zstd download support. For mods using Zstd compression, also follow the instructions for [SteamLegacyZstd](https://github.com/yuyu107/SteamLegacyZstd).

Prompts follow the Windows display language: Simplified Chinese for zh-CN / zh-SG / zh-Hans, Traditional Chinese for zh-TW / zh-HK / zh-MO / zh-Hant, and English for other languages. Logs preserve original Steam output and exception details.

## Restore and report problems

Close the game and run `Restore-LegacySteam.bat` from the current patch package. It automatically selects the matching original-file backup.

Alternatively, in Steam, open **Properties → Installed Files** (called **Local Files** in some older clients) and select **Verify integrity of game files** to retrieve the official files for your current branch. Verification can remove the patch and may update the game. Extra patch scripts and backups may remain. Run the current installer again if you still need the compatibility patch.

For installation failures, include `tML-LegacySteam-Install.txt` and `tML-LegacySteam-Check.txt` if generated. For startup or in-game failures, include newly generated `tModLoader-Logs`, screenshots, and your Windows, Steam, and tModLoader versions. Check logs for account names, paths, and Steam IDs before posting them publicly.

End users do not need Python. Scripts are written for Windows PowerShell 2.0 on Win7. Run them at the same privilege level as Steam.

## Changes made by the patch

- **Friends:** uses `SteamFriends017`. SDK 1.62's `SteamFriends018` removes two functions from the older interface. The patch remaps exported wrappers to the legacy virtual-function slots while preserving originally merged function bodies.
- **Workshop UGC:** uses `STEAMUGC_INTERFACE_VERSION020`. Existing function positions match SDK 1.62; newer local-disable and subscription-order functions return unavailable.
- **Remote Play:** uses `STEAMREMOTEPLAY_INTERFACE_VERSION002`, adapts the older UI call, and reports newer direct-input functionality as unavailable.
- **Timeline:** tolerates a missing timeline interface; affected exports return zero or do nothing. Recording timeline functionality is unavailable.
- **File integrity:** updates one expected MD5 in `tModLoader.dll` to match the patched `steam_api64.dll`. `HashMatchesFile`, `CheckSteam`, Terraria installation checks, and Steam ownership checks remain intact.

These adaptations do not establish compatibility for untested features or every third-party mod that calls newer Steam APIs directly.

## Source and build

Developer builds require modern Python. End users running the installer do not need it.

```sh
python -m pip install -r requirements.txt
python tools/build.py --game-dir /path/to/pristine/tModLoader --output build
python tools/verify.py --game-dir /path/to/pristine/tModLoader --build-dir build
```

The build tool requires original files for the supported source version: `tModLoader.dll`, the two managed DLLs under `Libraries/steamworks.net.anycpu/2025.162.4`, and the Windows x64 native DLL. If already patched, use the preserved original backups with the same directory layout.

To repackage the checked-in sparse patches without supplying game DLLs:

```sh
python tools/package.py --output build/release
```

Build outputs include modified files, sparse patches, change records, and a ZIP. Complete original or modified DLLs stay in the local build directory and are not committed.

| Path | Purpose |
| --- | --- |
| `tools/build.py` | Managed metadata / IL changes, native export adaptation, and precise game fingerprint update |
| `tools/interface_layouts.json` | Function-order comparison for SDK 1.60 / 1.62 |
| `tools/delta.py` | Sparse-patch encoding and decoding |
| `tools/package.py` | Installer ZIP and checksum generation |
| `tools/verify.py` | Sparse reconstruction, export mapping, and file validation |
| `runtime/` | PowerShell 2.0 installer, restoration, preflight, and C# patch sources |
| `patches/2026.8.3.0/` | Source-version sparse patches and SHA-256 manifests |
| `packages/` | Installer packages without complete DLLs |

## References and license

Interface layouts reference [SteamworksSDK 1.60](https://github.com/rlabrecque/SteamworksSDK/tree/e7bb839178fc/public/steam) and [1.62](https://github.com/rlabrecque/SteamworksSDK/tree/34d9338aa892/public/steam). Related projects:

- [tModLoader](https://github.com/tModLoader/tModLoader)
- [Steamworks.NET](https://github.com/rlabrecque/Steamworks.NET)
- [SteamLegacyZstd](https://github.com/yuyu107/SteamLegacyZstd)

Original scripts, tools, and documentation are licensed under the [MIT License](LICENSE), `Copyright (c) 2026 yuyu107`.

Third-party games, Steamworks libraries, SDKs, and other third-party material are outside this project's MIT license and remain subject to their respective rights and terms. Third-party content involved in sparse patches is not relicensed under MIT.

This repository does not contain complete SDK headers, complete game DLLs, account data, or Steam client files.
