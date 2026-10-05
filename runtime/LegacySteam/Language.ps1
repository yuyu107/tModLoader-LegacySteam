# Windows PowerShell 2.0 compatible; use UI culture, not date/number formats.
$LegacySteamLanguage = 'en'
$cultureName = [Globalization.CultureInfo]::CurrentUICulture.Name
if ($cultureName -match '^zh-(CN|SG|Hans)(-|$)') { $LegacySteamLanguage = 'zh-Hans' }
elseif ($cultureName -match '^zh-(TW|HK|MO|Hant)(-|$)') { $LegacySteamLanguage = 'zh-Hant' }
$LegacySteamMessages = @(
 @{ English='Keep LegacySteam-Backups and older backups. Restore-LegacySteam.bat selects the matching version automatically.'; Simplified='请保留 LegacySteam-Backups 和旧备份。Restore-LegacySteam.bat 会自动选择对应版本进行恢复。'; Traditional='請保留 LegacySteam-Backups 和舊備份。Restore-LegacySteam.bat 會自動選擇對應版本進行還原。' },
 @{ English='Legacy interface preflight failed. No DLLs replaced. Send tML-LegacySteam-Check.txt.'; Simplified='旧版接口预检失败，未替换任何 DLL。请反馈 tML-LegacySteam-Check.txt。'; Traditional='舊版介面預檢失敗，未替換任何 DLL。請提供 tML-LegacySteam-Check.txt。' },
 @{ English='Expected API fingerprint must occur in exactly one CLR user-string entry'; Simplified='无法唯一定位 Steam API 校验值，停止修补'; Traditional='無法唯一定位 Steam API 驗證值，停止修補' },
 @{ English='Game fingerprint state does not match regenerated output.'; Simplified='备份校验记录与重新生成的文件不一致。'; Traditional='備份驗證記錄與重新產生的檔案不一致。' },
 @{ English='Unsupported or updated file. Nothing replaced: '; Simplified='文件版本不支持或已更新，未替换任何文件：'; Traditional='檔案版本不支援或已更新，未替換任何檔案：' },
 @{ English='RESTORED: original game and Steamworks files.'; Simplified='已恢复游戏和 Steamworks 原文件。'; Traditional='已還原遊戲和 Steamworks 原始檔案。' },
 @{ English='Matching game backup is missing or damaged.'; Simplified='对应版本的游戏备份缺失或损坏。'; Traditional='對應版本的遊戲備份遺失或損壞。' },
 @{ English='Please run the supplied 64-bit launcher.'; Simplified='请使用补丁附带的 64 位启动脚本。'; Traditional='請使用補丁附帶的 64 位啟動指令碼。' },
 @{ English='Original file or valid backup missing: '; Simplified='缺少原文件或有效备份：'; Traditional='缺少原始檔案或有效備份：' },
 @{ English='Strong named game assembly unsupported'; Simplified='不支持带强名称签名的游戏程序集'; Traditional='不支援具有強式名稱簽章的遊戲組件' },
 @{ English='Use the supplied 64-bit BAT launcher.'; Simplified='请使用补丁附带的 64 位 BAT 启动脚本。'; Traditional='請使用補丁附帶的 64 位 BAT 啟動指令碼。' },
 @{ English='Patched output verification failed: '; Simplified='修补结果校验失败：'; Traditional='修補結果驗證失敗：' },
 @{ English='Full legacy interface list: result='; Simplified='旧版接口完整预检：结果='; Traditional='舊版介面完整預檢：結果=' },
 @{ English='Backup for this game version: '; Simplified='当前游戏版本的备份目录：'; Traditional='目前遊戲版本的備份目錄：' },
 @{ English='Restore verification failed: '; Simplified='恢复后校验失败：'; Traditional='還原後驗證失敗：' },
 @{ English='. Start tModLoader normally.'; Simplified='。现在可以正常启动 tModLoader。'; Traditional='。現在可以正常啟動 tModLoader。' },
 @{ English='Write verification failed: '; Simplified='写入后校验失败：'; Traditional='寫入後驗證失敗：' },
 @{ English='Missing or damaged patch: '; Simplified='补丁缺失或损坏：'; Traditional='補丁遺失或損壞：' },
 @{ English='Duplicate user-string heap'; Simplified='存在重复的用户字符串堆'; Traditional='存在重複的使用者字串堆積' },
 @{ English='Invalid existing backup: '; Simplified='现有备份校验失败：'; Traditional='現有備份驗證失敗：' },
 @{ English='Missing user-string heap'; Simplified='用户字符串堆缺失或无效'; Traditional='使用者字串堆積遺失或無效' },
 @{ English='Close tModLoader first.'; Simplified='请先关闭 tModLoader。'; Traditional='請先關閉 tModLoader。' },
 @{ English='Truncated patch header'; Simplified='差分补丁头不完整'; Traditional='差分補丁標頭不完整' },
 @{ English='Unmapped metadata RVA'; Simplified='无法定位元数据地址'; Traditional='無法定位中繼資料位址' },
 @{ English='Invalid string length'; Simplified='无效的字符串长度'; Traditional='無效的字串長度' },
 @{ English='Invalid CLR metadata'; Simplified='无效的 CLR 元数据'; Traditional='無效的 CLR 中繼資料' },
 @{ English='Invalid patch header'; Simplified='无效的差分补丁头'; Traditional='無效的差分補丁標頭' },
 @{ English='Already installed: '; Simplified='已安装此补丁：'; Traditional='已安裝此補丁：' },
 @{ English='Technical details: '; Simplified='原始诊断信息：'; Traditional='原始診斷資訊：' },
 @{ English='Invalid fingerprint'; Simplified='无效的文件校验值'; Traditional='無效的檔案驗證值' },
 @{ English='Invalid stream name'; Simplified='无效的元数据流名称'; Traditional='無效的中繼資料串流名稱' },
 @{ English='String exceeds heap'; Simplified='字符串超出元数据范围'; Traditional='字串超出中繼資料範圍' },
 @{ English='Invalid patch chunk'; Simplified='无效的差分补丁数据块'; Traditional='無效的差分補丁資料區塊' },
 @{ English='Trailing patch data'; Simplified='差分补丁包含多余数据'; Traditional='差分補丁包含多餘資料' },
 @{ English='LoadLibrary error='; Simplified='加载 DLL 失败，系统错误码='; Traditional='載入 DLL 失敗，系統錯誤碼=' },
 @{ English='Oversized metadata'; Simplified='元数据大小超出支持范围'; Traditional='中繼資料大小超出支援範圍' },
 @{ English='Unknown PE layout'; Simplified='不支持的 PE 文件结构'; Traditional='不支援的 PE 檔案結構' },
 @{ English='Invalid file size'; Simplified='无效的文件大小'; Traditional='無效的檔案大小' },
 @{ English='Target missing: '; Simplified='缺少目标文件：'; Traditional='缺少目標檔案：' },
 @{ English='Truncated string'; Simplified='字符串数据不完整'; Traditional='字串資料不完整' },
 @{ English='Invalid mode.'; Simplified='无效操作模式。'; Traditional='無效操作模式。' },
 @{ English='Not a PE file'; Simplified='不是有效的 PE 文件'; Traditional='不是有效的 PE 檔案' },
 @{ English='INSTALLED: '; Simplified='安装完成：'; Traditional='安裝完成：' },
 @{ English='ERROR: '; Simplified='错误：'; Traditional='錯誤：' }
)
function T([string]$Text) {
 if ($LegacySteamLanguage -eq 'en') { return $Text }
 foreach ($message in $LegacySteamMessages) {
  if ($LegacySteamLanguage -eq 'zh-Hans') { $Text = $Text.Replace($message.English,$message.Simplified) }
  else { $Text = $Text.Replace($message.English,$message.Traditional) }
 }
 return $Text
}
