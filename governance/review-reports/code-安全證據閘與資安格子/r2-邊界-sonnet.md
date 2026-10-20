severity: minor

我在 7655a12d 的 detached worktree 載入 `scripts/lumos`,用 python3.14 -B 逐函式實跑。下面有兩條 finding,都是 minor。

## 1. 確認碼提示的指令沒有引號,路徑帶空白或中文空格時貼上就壞
severity: minor
blocking: 否

引句:「f"    lumos code-loop security-approval-add {payload_path} --repo {root}")」

重現:執行 `_secapr_confirm_human("/tmp/my dir/付 款 payload.json", "/tmp/my repo")`。stdin 不是互動終端,所以回傳擋下訊息,印出:

```
    lumos code-loop security-approval-add /tmp/my dir/付 款 payload.json --repo /tmp/my repo
```

使用者照這行貼到自己的終端機,shell 會把路徑拆成多個參數。`{out or ...}` 那兩行提示(`security approvals payload` 末尾)也一樣沒加引號。

歸因:有證據的修復新增。這個非互動提示是這輪才加的,修前沒有這個函式。這條沒有跑修前版。

## 2. 單一證據項的 vulndb_fetched_at 時間極端時,整道閘變成 evaluation_error,和「單項壞只讓那一項 invalid」不符
severity: minor
blocking: 否

引句:「# ★單項壞只讓那一項 invalid★:外來檔案的欄位型別怪到讀法沒預料到(各讀法已先驗型別,這是兜底),」

重現:`_secev_item_dates` 吃 `observed_at="2026-10-19T00:00:00Z"`、`vulndb_fetched_at="0001-01-01T00:00:00+05:00"`、`kind="dependency_scan"`,會丟 `OverflowError('date value out of range')`。原因是 `vf.astimezone(_dt.timezone.utc)` 溢位。

這個呼叫在 `_secev_judge_item` 的 try 之外,新加的 except 也只接 `TypeError`、`AttributeError`、`KeyError`、`IndexError`、`ValueError`,不含 `OverflowError`。例外會一路往上,落到 `_secev_evaluate` 的 `except Exception`,整道轉成 `gate_code=evaluation_error`,其他護欄的判定一起丟掉。這是失敗時擋下,不是放行。

我沒有跑完整的端到端推送,只在單函式層重現。對照組:同一函式用 `9999-12-31T23:59:59-05:00` 回 `['vulndb_after_observed']`,用 `2026-10-05T23:59:59Z` 回 `['vulndb_stale']`,都正常。

歸因:有證據的原有漏查。修前版(b99f52c8)有同一行 `vf.astimezone(_dt.timezone.utc)`,未被這輪修補改動。這輪的兜底沒有收到這一類例外。

## 三問的回答

**①原問題的修復效果,有行為證據的部分:**
- `_secev_target_host` 改用 `urlsplit`,實跑 37 種輸入,方向全是「判不出來就擋」。
  - 大小寫 scheme、`[::1]`、帶埠、帶帳密、`localhost@evil.com`(取 `evil.com`)、`evil.com#@localhost`、`evil.com?@localhost` 都解對。
  - 反斜線、`%6c` 百分比編碼、空主機、`//`、`:8080`、埠 99999、埠 abc、`[::1` 缺括號、`http://::1/` 都回 None。
  - 沒有 scheme 但路徑或 query 裡含 `://` 的字串回 None(擋)。
  - `localhost.` 與 `127.1` 判成非回環(擋)。
  - 全形 `ＬＯＣＡＬＨＯＳＴ` 判成非回環(擋)。
  - `None` 與空字串回 None。
- 例外型別閘 `_secev_exception`:實跑 12 種 `covers_kinds` 與 `compensating` 組合。
  - 這些全部判 `exception_fields_missing`:空陣列、重複、巢狀 list、bool、空字串、None、全空白、字串型 `covers_kinds`。
  - v1 形狀判 `exception_unapproved`。
  - `expires_on` 為 None 時不丟例外。
- `_jsonl_append_line_verified`:實跑檔尾沒換行、中文帶空格、U+2028、U+0085、`\r`、NUL、50 字元以上的值,讀回自驗都回 0,換行補得對。
- `_secev_backing_rows` 的三元回傳與 `cmd_codeloop_security_backing` 的解包一致。
- `_secev_consideration_counted` 改回傳字串原因,`_seccell_cons_index` 用 `v is True` 判斷,字串不會被當成「算數」。
- `_secapr_add_read` 對空檔、BOM、結尾多換行、10 萬層深巢狀、非 UTF-8、非物件都回擋下訊息,沒有崩潰。
- `_TEST_QUALITY_BUNDLE_DIGESTS` 裡的 `test_quality.py` 雜湊與檔案實際 sha256 一致。
- 外來 JSON 型別閘:工具清單的 `min_requests` 用 `type(v) is int`,bool 不會當數字;`bindings` 的 blob 在讀進來時已驗成字串,所以 `[:12]` 不會崩。

**②修補處的正常、錯誤與相鄰呼叫路徑:**
- 到期日恰在今天:`exp < today` 仍有效,實跑沒有炸。
- backing 單行恰在上限:寫入端用 `>`、讀取端用 `>`,兩端一致。
- 工具被刪或改名那條新路徑,我只讀了碼,沒有構造完整 repo 實跑。

**③新發現的同一案例修前、修後:**
- Finding 1:修前沒有這個提示,未判定。
- Finding 2:修前修後同樣丟 `OverflowError`,是原有漏查。

## 未驗範圍
- 核可鏈的 30 天、180 天剛好卡上限與超過一天,需要完整 ssh-keygen 簽章鏈,沒有實跑。
- `_secev_orphans` 對大量 Verification 的效能(大型輸入、單項證據數超過上限一筆)沒有實測。
- 讀不出主線工具清單時,凍結比對是拿空清單比,凍結形同沒做。這條是讀碼推論,沒有實跑,也不在本輪修補範圍。

最嚴重 severity:minor,blocking 共 0 條。
