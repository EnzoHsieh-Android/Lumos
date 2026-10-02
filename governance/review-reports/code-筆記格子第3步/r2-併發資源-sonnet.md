severity: minor

整份修正差異我逐 hunk 讀完,也實量了,共兩條,都不擋。

實量環境:repo 的 `docs/lumos-toolchain-knowledge`(622 篇)和 16MB 的 `docs/.governance-log.jsonl`。

## 實量結果(併發與資源)

- **S16 改寫後的耗時**:對 622 篇,逐實體行判舊法 0.001s,`_ns_summary_logical` 重組新法 0.013s。整支 `_doctor_stale_rules` 是 0.014s。完整 `lumos doctor` 跑 622 篇總共 29s,沒有因這段變慢。
- **doctor 讀設定檔次數**:沒有變多。`_doctor_cfg_bytes` 只是把三處各抄一份的讀法收成一支,S18 仍然只讀一次。
- **`_metric_gate_off` 不再吞例外**:我用壞 JSON、`[]`、`null`、非物件、非 UTF-8、缺檔等 11 種設定,對六個閘逐一呼叫,都沒有拋例外。所以 S18 外層那層 try 目前不會被觸發。
- **先記帳再印**:`_gate_event` 用單次 `open("a")` 加一次 `write` 寫一行(`scripts/lumos:1226`)。兩個推送同時跑,各自追加一行完整的帳,不會交錯。
- **印到一半被中斷**:KeyboardInterrupt 不是 Exception,不會被吞。blocked 那筆帳已經在,rc 也沒被改。這符合這次修正的意圖。
- **`_drift_retire_quiet`**:只包 `print(…, file=sys.stderr)`,吞的只是 stderr 壞掉的錯。它沒有包住判定,所以不會掩蓋該看到的問題。
- **記帳那段的 `except Exception`**:會把記帳的程式錯誤壓成一句,但訊息帶例外類型名稱,可追查。

## 發現

R2K1 帳增速段改用 `_drift_jsonl_parse` 後,記憶體尖峰約翻倍
severity: minor
blocking: 否 — 受 24MB 檔尾上限封頂,且只在 doctor 瞬間發生。
引句:「for _d in _drift_jsonl_parse(_raw):」
1. 原本逐行 `loads` 後丟掉,現在先把整個檔尾解析成 dict 清單才開始迴圈。
2. 實量(tracemalloc,16MB 實帳、102948 行):舊 58MB,新 124MB。
3. 最壞情況是填滿 24MB 上限的短行(629145 行):新尖峰 246MB。
4. 解析時間沒變(0.23s 對 0.22s)。
5. 同一支 doctor 裡 S18 會再解析一次同一份檔尾,是依序進行,兩次尖峰不會疊加。
6. 修法:帳增速段用只回傳迭代器的版本,或逐行解析。目前不急。
7. 重現:`/tmp/r2k_mem.py`(我在 repo 外的暫存腳本)。

R2K2 S16 的續行接回有二次方成本,S17 到 S19 已有同樣的成本
severity: minor
blocking: 否 — 要單篇 frontmatter 達 MB 級才顯現,正常圖譜 13ms。
引句:「for t in _ns_summary_logical("---\n" + "\n".join(n.fm_lines) + "\n---\n").values():」
1. 原因是 `_ns_summary_logical` 內的 `out[last] += " " + s`,對字典值做字串累加,每接一行就複製整條。
2. 這份修正讓 S16 也走這支,doctor 現在在同一篇上跑四次(S16、S17、S18、S19)。
3. 實量:一條 RULE 後面接 N 行 50 字續行,只算新 S16 一段:
   - N=10000(263KB):0.11s
   - N=40000(1MB):1.43s
   - N=80000(2MB):8.07s(約四倍時間對兩倍輸入)
4. 修法:`_ns_summary_logical` 改成收集片段再 `join`。
5. 重現:`/tmp/r2k_quad.py`(我在 repo 外的暫存腳本)。
6. ⚠ 這個二次方是既有函式本身的問題,不是這份差異新增的。我只把它放大成每次 doctor 多跑一次。

## 圖譜鏡頭

這份差異不破壞任何固定席節點宣稱的行為或合約。我用 `lumos impact --diff 2f9cb94f..384f4574` 實查了影響範圍,並讀了相關節點的 ★INVARIANT★ 和 ★RISK★ 行。

1. `Systems/lumos-cli-read`(家,INVARIANT:search 預設排除 superseded):不影響。改動在 doctor S16 到 S19 和 `_doctor_cfg_bytes`,沒碰 `cmd_search`、`contracts`。該節點的說明行已同步改成新行為,與程式一致。
2. `Systems/存量漂移守衛` 與 `reversibility-governance-ledger`(放行不寫帳):不影響。改後仍是 `if must or unknown:` 才記帳,放行不寫。順序改成先記帳再印,與新寫的說明一致。
3. `guard-kill`(rc 優先序、`--json` 純度)、`測試假綠形態`、`bound-tests-gate`、`design-loop`、`pitfalls-code-loop`、`loop-convergence-recording`:不影響。它們管的是別條路徑,這份差異沒碰。
4. 其餘固定席是 hop1 或 RISK·守衛面,只因為 `scripts/lumos` 與 `scripts/test_lumos.py` 都被改到而列入:不影響。
5. 新增的測試(`t_slots_doctor_reminders_edges`、`t_slots_retire_issue_followups`)我在乾淨 clone 跑過:前者 1.8s,後者 8.8s,共 26 與 8 個通過。

最高嚴重度 minor,blocking 0 條
