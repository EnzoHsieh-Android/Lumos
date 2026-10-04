# design-背景快取命中清鎖 r1 前掃

preflight-4: ran

唯讀前掃逐查未定義詞、引用、範圍一致性與程式行為語意。`refcheck --json` 無缺檔與越界；`prose-lint` 無命中；`pitfalls --check` 找到實務隱患節；計劃 lint 0 問題。新測試名尚未在程式樹，屬待寫的紅燈而非既有證據。

| 類別 | 原句與程式核對 | 前掃處置 |
|---|---|---|
| 所有權用詞 | 原說「背景程序持有本次鎖」；`_lens_wait_or_warm` 由派工端建鎖，背景只繼承標記與 PID 副本。 | 改為「派工端建立、背景端負責清理」，S1 主體仍以背景進場條件驗。 |
| 現況語意 | 原說「保留既有鎖格式與驗證方式：背景程序須帶 `_LENS_WARM_ENV`」；原尾端清理只驗 `LUMOS_LENS_LOCK_OWNER` 與鎖內 PID。 | 明寫暖機標記是新增守衛，鎖格式及 PID 比對才是沿用。 |
| 範圍一致性 | 原說「已知兩個出口」；快取未命中後的 impact、JSON、base 樹失敗仍可能提前返回，均跳過尾端清理。 | 改為 `try…finally` 包住快取路徑算出後的整段鏡頭工作；加 S4 錯誤提前返回測試，不靠逐點補刪鎖。 |
| 引用 | 兩個 Issue、前計劃、落點 Systems 與回退父提交均存在。 | 無修改。 |

前掃沒有改寫「本次只修背景清理、啟動失敗另案」的核心裁定；機械語意缺口已寫在計劃正文，交正式審查席再挑。

## 六席收貨與處置

六席均唯讀凍結的 `r1-snapshot.md`，收齊前未改審材。正確性、邊界、整合、回退四席報出 7 條，資源與架構席為 clean。報告原文在同目錄；有 finding 的四席經 `report-normalize`、`quote-check`、`refcheck` 驗證，clean 席無引句可供 quote-check，報告仍保存。新問題均可由程式路徑或隔離注入核對，未以文句偏好降級。

| id | 重現與判讀 | 處置 |
|---|---|---|
| C1 | HIT：派工端 A/B 可同 PID；原背景用移動後 ref 重算時，`_lens_cache_path` 對兩組 SHA 實算為不同名稱，原提案用重算路徑清理會漏 A 或刪 B。 | folded：傳固定完整 SHA 範圍與原鎖名稱，S2/S5 用同 PID ref 移動屏障驗。 |
| B1 | HIT：在隔離 Python 3.14 程序移除 `os.getuid` 後，`_lens_cache_read` 對合法快取拋 `AttributeError`；官方文件也列 `getuid` 僅 Unix。 | folded：沿用 `_trusted_private_dir` 的平台分支，S6 故障注入；原生 Windows 仍須人工重驗。 |
| I1 | HIT：`lands_in` 只列 `Systems/lumos-cli-write`，漏了派工鏡頭落點 `Systems/codex-harness` 與 `Systems/hook逾時預算`。架構席認為前者可承接鎖原語；兩種落點兼存。 | folded：補兩篇 Systems，不刪原檔案之家。 |
| I2 | HIT：原 Issue 要求 TTL 後可再暖機，凍結 S1–S4 無此端到端斷言。 | folded：新增 S7。 |
| R1 | HIT：凍結 S4 只驗 impact，JSON、base 樹、未預期例外沒有對應測試，局部補丁可假綠。 | folded：S4 擴成多出口故障注入，清理掛工作入口 `finally`。 |
| R2 | HIT：父提交沒有 pause/disable 暖機專用開關；只回退會恢復已知 F1/F2。 | folded：先在 hook 環境設現有 `LUMOS_DISPATCH_LENS_NO_CACHE=1`，停舊背景並查鎖後才退到父提交。 |
| R3 | HIT：原驗證節未限定 Python 3.14、來源 repo、本地主線與零 skip；既有整合測試可跳過。 | folded：驗證順序列前提並要求核實零 skip。 |

## 資源席替補與辯方

原資源席報告只寫 clean、未逐一核對派工材料；`seat-check` 顯示 unreported 3，故原報告留檔但不計為有效資源席。替補席 `r1-resources-reshoot.md` 經 `report-normalize`、`quote-check`、`refcheck` 與 `seat-check`，後者 unreported 0。替補的三條現象均可重現；F1 與 C1 是同一個 ref 漂移缺口。F2/F3 的換檔實驗本身 HIT，但「同版正常流程可換入」這個前提經唯讀辯方核對不成立，見 `r1-defense.md`。原報告的 major/blocking 宣告保留；以下 accepted 是本案限縮適用範圍後的處置，不改報告。

| id | 重現與判讀 | 處置 |
|---|---|---|
| RF1 | HIT：派工端傳符號 ref，移動或刪除 ref 後，背景會算到不同快取路徑或在算路徑前返回，留原鎖；與 C1 同因。 | folded：S5 改傳已解析完整 SHA 與原鎖名稱；入口 `finally` 覆蓋前置錯誤。 |
| RF2 | HIT：人工以相同 PID、不同 inode 換入同名鎖後，現行尾端會刪新鎖。辯方查 `_excl_lock_try` 的 `O_EXCL`、等待端不清鎖、啟動失敗時無舊背景，證明同版正常流程無合法同名換入者。 | accepted：只承諾同版且無人工換鎖；實作須以唯一清理出口取代舊出口，S8 驗證不會二次誤刪。若切換安裝時仍有舊版工作或人工移鎖，須依原案 [[Projects/過期鎖安全接手_計劃]] S6 重新驗證，不沿用此降級。 |
| RF3 | HIT：mock 在 `read_text` 後 `unlink` 前換入不同 PID 鎖，現碼會刪換入者。辯方核對同版流程無合法同名換入者；Python `os.unlink` 依名稱刪除，單加 inode 複查不會讓兩步原子化。 | accepted：維持同版無外部換鎖界線，不宣稱抵抗舊版、人工或同 UID 外部修改；如需跨版本並行，另訂取得與釋放協議。S8 保證本次修復不新增雙出口競爭。 |

本輪共 10 條原始 finding（正確性 1、邊界 1、整合 2、回退 3、資源替補 3），其中 9 條原報告標 major/blocking，1 條 minor。8 條折入，2 條附證據及回頭事件接受；沒有機械重現不到而拒收的項目。外家否決席未取得，這一輪的結論限於同家族審查與實際測試。
