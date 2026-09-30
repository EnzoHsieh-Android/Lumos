severity: minor

## F1 留痕檔自己開檔追加,沒有沿用既有帳本追加寫法的滿寫檢查
severity: minor
blocking: 否
引句:「fst = os.fstat(fd)」
佐證行:file: `scripts/lumos:15876`(`_ledger_append`:O_APPEND + O_NOFOLLOW + 單次 os.write 後驗滿寫,短寫丟 RuntimeError)
佐證行:file: `scripts/lumos:29413`(`_drift_m1_ledger_miss` 開檔處;跟 `_ledger_append` 同一族寫法,差在要 O_CREAT 與不設 4KB 上限,所以不能直接呼叫)
1. 留痕檔的開檔骨架(O_APPEND|O_NOFOLLOW、單次 os.write 整行)沿用了既有帳本追加的寫法,方向對;r2 新加的 O_NONBLOCK 與 S_ISREG/uid 檢查是它自己需要的補強,不算第二套。
2. 但既有寫法特地驗 `os.write` 回傳長度(磁碟滿短寫會留半行,`_ledger_append` 註解 B1);這支 `os.write(fd, line.encode("utf-8"))` 不驗長度就 `return True`。留痕檔的用途正是「帳寫不進去(常見原因就是磁碟滿)」時的替身,短寫時回報成功、留下殘行,REVISIT 讀檔算樣本會讀到壞行。
3. 判斷:同族寫法缺了既有守衛,不是第二套機制、也沒跨層直呼,所以停在 minor。未能重現(需要 ENOSPC 環境)。

## 架構對齊逐項結論(無 finding 的項目)
- `_mkdir_private_layer` 抽出:`scripts/lumos` 裡所有「家目錄底下逐層建」的鄰居都走 `_mkdir_trusted_under_home` → `_mkdir_private_layer`:vault-lock(`scripts/lumos:15053`)、drift-defs(`:28944`)、drift-m1(`:29402`)、`_home_cache_write`(`:34543`)、dispatch-lens armed(`:35060`)、bound-filter(`:36175`)。沒有另一套家目錄建層寫法;其餘 `mkdir(parents=True)` 都是 repo 內或非家目錄快取路徑(例:`:14606` 是 scripts/vendor),不在這條共用守衛範圍。
- `_chmod_no_follow` 沿用:`_mkdir_private_layer` 建完層呼叫既有的 `_chmod_no_follow`(`scripts/lumos:34984`,O_NOFOLLOW|O_DIRECTORY 開再 fchmod),跟 dispatch-lens armed 的用法(`:35067`)同一支,沒有手抄第二份。
- 嚴格判準一套:`group_ok` 已從 `_trusted_private_dir`、`_mkdir_trusted_under_home`、`_home_cache_write`、drift-defs、drift-m1 全部拿掉,全 repo 已無殘留參數。
- `_drift_config_parts` / `_drift_config_text_parts`:`_drift_config` 保留原四元組回傳給既有呼叫端(`scripts/lumos:28553`),doctor 改拿分開的 parts;兩者從同一個 `_drift_config_text_parts` 解析,沒有第二支讀 drift_check 鍵的路徑。
- 跳脫:終端出口走 `_drift_c4_show_name`(`scripts/lumos:28185`,既有),寫帳走既有 `_drift_m1_show`(`:28711`);兩個出口各有各的既有函式,沒有新造第三套。
- 截止時間:`_DRIFT_M1_TICK_EVERY` 計數器包 `run.check_time`,與 `_drift_m1_scan_note` 每行看一次(`scripts/lumos:29012` 起)是同一個檢查點,沒有另設時鐘。

## 圖譜鏡頭逐條判定
- lumos-cli-read(★INVARIANT★ search 排除 superseded):diff 不碰 search 路徑,不影響。
- bound-tests-gate(code-loop check 綁定測試逐支跑):diff 只加測試與 m1 程式,不動閘判定邏輯,不影響。
- guard-kill(kill rc 優先序、--json 純度):不碰 guard kill,不影響。
- 授權與歸屬(授權檔不入 _VENDORED_TOOLKIT、檔頭 SPDX):diff 不動 _VENDORED_TOOLKIT 與檔頭,不影響。
- 測試假綠形態(還原翻紅釘要配前置斷言):新增測試帶翻紅釘與前置檢查的描述(patch 內測試註解),未見違反,不影響。
- lumos-cli-lifecycle(re-inject 保留 sentinel 外內容)、design-loop(處置閘第五步):不碰,不影響。
- pitfalls-code-loop(★RISK★):風險分級邏輯未動,不影響。

最高等級:minor
