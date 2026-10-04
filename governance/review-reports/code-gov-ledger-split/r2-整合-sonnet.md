severity: minor

## F1 計劃筆記〈做法〉3、5、6 仍是修補前的說法,與程式現況三處對不上
severity: minor
blocking: 否
引句:「整份經 _write_lf 原子替換,不就地追加」
file: `docs/lumos-toolchain-knowledge/Projects/治理帳例行紀錄分流_計劃.md:68`
file: `docs/lumos-toolchain-knowledge/Projects/治理帳例行紀錄分流_計劃.md:73`
file: `docs/lumos-toolchain-knowledge/Projects/治理帳例行紀錄分流_計劃.md:75`
失敗場景:三個月後的人照計劃〈做法〉動手,會撞三面牆。
(a) 第 68 行寫「取路徑只用一支 `_docs_local_log_path(docs_dir, name)`」。grep 全 repo,這個名字只剩在這篇筆記和舊的 .pyc,程式裡已改名 `_docs_ledger_path`,照筆記 grep 找不到函式。
(b) 第 73 行寫補忽略規則「缺的用二進位追加到尾端……不整檔改寫」。程式現況是 `_write_lf(gi, (raw + chunk).decode("utf-8"))` 整份原子替換,且非 UTF-8 的檔不動。筆記沒講原子替換、捷徑被換掉、非 UTF-8 不動這三件事。
(c) 第 75 行寫 S18「暖機護欄用的最舊一筆照舊只看版控帳(避免本機帳的時間讓護欄提早放行)」。程式現況正相反:走 `_GOV_LOCAL_PAIRS` 的組合看本機帳最舊一筆,本機帳不在就不判。這條與同篇「實作紀錄」r1 條、與 reversibility-governance-ledger.md 的 PITFALL 互相矛盾。
第 75 行的 doctor 提醒說明也沒寫「已被版控追蹤」這一支。
修法方向:把這幾句改成現況或標明已被 r1 取代。

## F2 spec-gate 段改走合讀後只看檔尾 24MB,最近一次紀錄可能被靜默截掉
severity: minor
blocking: 否
引句:「讀法同 doctor 其他讀治理帳的段落:各讀檔尾(_gov_tail_bytes)、只在 \\n 切行」
file: `scripts/lumos:2989`
file: `scripts/lumos:3806`
失敗場景:`_gov_ledger_rows_by_time` 改成檔尾讀法後,doctor 的 spec-gate 段(`for _d in _gov_ledger_rows_by_time(...)` 取後寫者勝)與測試輔助 `_gov_events_all` 不再讀到全部歷史。目前 docs/.governance-log.jsonl 約 19 MB、上限 24 MB。帳過 24 MB 後,只在檔尾之前跑過規格閘的計劃,「最近一次紅綠弱證據」那列會消失。這一段不像成長觀測有「只讀得到最近一段」的提示,使用者只會看到少一列。呼叫端 docstring 與函式註解都沒提這個限制。⚠ 影響是少一列提醒,不影響判定類讀者。

## 已走過沒問題的範圍
- 舊名 `_docs_local_log_path`:scripts/lumos、scripts/test_lumos.py、scripts/hooks、其他 scripts/*.py 都已無殘留,只剩 F1 的筆記與 .pyc。
- `_gov_ts` 由度量段與合讀共用;`_gov_metric_events` 與 `_gov_ledger_rows_by_time` 的例外類別一致,排序鍵另接 OverflowError、OSError、ValueError,對照 diff 沒有漏。
- `_ensure_docs_gitignore`:`_write_lf` 以 bytes 寫入,CRLF 與 BOM 原樣保留;docstring 已改成「原內容一個位元組都不改」,與程式一致。
- 測試輔助 `_gov_events_all`、`_m1_events` 改成合讀後,fixture 很小,不受檔尾截斷影響。
- `cmd_gov` 的 `load` 仍整檔 `read_bytes`,兩本都讀,沒受檔尾改動影響。
- 本機帳是捷徑時兩支寫入器都不寫(`_gate_event`、`_append_governance_log`),判定類讀者仍只讀版控帳。
- reversibility-governance-ledger.md 的 PITFALL/WHY/KEY(count=7)與程式現況一致。
- 圖譜鏡頭:尾端沒有固定席筆記,不必逐條答。

總結:程式側的改名與抽共用函式都跟上了,只剩計劃筆記三處講舊行為,以及合讀改讀檔尾後 spec-gate 段的歷史範圍收窄。
