severity: minor

我把輪次規則、集合 none、`--regression-set`、表態型別各 hunk 用具體輸入走過。另外在臨時帳上實跑了「舊設計審補 `--tier`」「帳含壞位元組」「folded/accepted/findings 的 none 組合」。新增的 `canary_record` 子集 117 條全綠(`python3.14 scripts/test_lumos.py -k canary_record`)。找到兩條 minor,沒有 major。

## 發現

1. 擋下訊息自相矛盾:舊帳沒定錨又全無輪次的迴圈,兩道擋下互相叫對方的做法
severity: minor
   - blocking: 否
   - 位置:`_round_format_write_block` 的 `first-no-round` 分支與 `mixed` 分支的 `nxt` 文案。
   - 輸入:帳上已有一筆 `{"loop":"prose-old","severity":"minor"}`(沒輪次、沒分級的舊設計審),編排者補記 `canary record … --loop prose-old --tier standard`,不帶 `--round`。
   - 預期:告訴編排者唯一可行的出路。
   - 實際(我實跑):
     - 第一道擋下說「接下來:補上輪次再記,例如 … --round r1 --tier standard」。
     - 照做後第二道擋下說「既有 1 筆裡 0 筆帶輪次…接下來:拿掉 --round 再記(既有的都不帶)」。
     - 兩句互相打架。實際可行的只有「換新編號」,或「不帶 `--tier` 也不帶 `--round`」。
   - 這就是 S8 已為處置帳修過的來回形狀,`first-no-round` 在 `rows` 非空且全無輪次時沒套同樣處理。S12 只斷言訊息含「定錨」,沒斷言出路正確。
   - 修法:`first-no-round` 在 `rows` 非空且 `cur == "none"` 時,改講「這個編號既有的都不帶輪次,換新編號」。
   - 引句:「接下來:補上輪次再記,例如 lumos canary record none --loop {q} --round r1 --tier {eff} …」

2. 帳裡任何位置有壞位元組,所有帶 `--loop` 的記帳全被擋,訊息卻說是「這個審查編號」
severity: minor
   - blocking: 否
   - 位置:新增的 `_lrows, _lerr = _loop_records_checked(env, loop) if (loop and outcome is None)`。
   - 輸入:帳尾附一行 `\xff\xfe junk`,再記一個全新的 `prose-new`,不帶輪次。
   - 預期:與壞行無關的新編號照舊寫得進(改動前如此)。
   - 實際:rc=2,印「這個審查編號的帳讀不懂(審查帳不是 UTF-8…)」。
   - 讀側(`_canary_ledger_scan`)對整本帳本來也只有一個 `decode_exc`,所以擋是一致的。但寫側現在連不帶 `--round` 的舊式記帳也受牽連,而且訊息指錯了範圍。
   - 修法:把「這個審查編號」改成「審查帳」。
   - 引句:「print(f"擋下:這個審查編號的帳讀不懂({lerr}),沒辦法確認輪次格式", file=sys.stderr)」只是我對 `bad-ledger` 訊息的轉述,逐字原文是:「擋下:這個審查編號的帳讀不懂({lerr}),沒辦法確認輪次格式」

## 走過、判定沒問題的路徑

- **結局帳列(S15)**
  - 寫側 `_loop_round_format` 與讀側 `loop next` 同一個數法,不會放行讀側判不了的帳。
  - `--outcome` 寫入整段跳過。
- **light 迴圈**
  - 第一筆帶不帶輪次都放行。
  - 之後換格式會被 `mixed` 擋。
  - light 的載體是單席自己,不會在 light 流程裡被誤擋。
- **舊循序代碼審**:`rows and cur == "none" and eff == "standard" and is_code` 放行,出口正確。
- **`--folded-set none` / `--accepted-set none`**
  - `--folded-set none` 與 `--accepted-set NONE` 都存成空清單。
  - `--findings-set none` 加 `--folded-set none` 照字面存 `["none"]`。
  - `"a1,none"` 被擋。
  - 另外 `accepted-set` 與 `regression-set` 的並列 none 不加這道檢查,也會被「id 不在發現清單」擋下,所以這段只是把訊息講得更清楚,放寬或收緊都沒有讓該擋的漏過。
- **`--regression-set`**
  - `"none,"` 走原本的「id 不在發現清單」擋下。
  - `" , "` 走新增的空值擋下。
  - 非 `code-` 開頭(含 `codex19`)被擋。
  - `skills/lumos-design-loop/templates.md` 第 3.1 節標明「僅供 code-loop」,沒有手冊教設計審帶這欄。
- **`cmd_loop_next` 的 `seq` 改成 `bool(rounds)`**:全新 `code-` standard 的範本改帶 `--round r1`,舊循序迴圈不變。
- **表態型別**
  - 寫側 `_dispositions_validate`、tension 的 `existing` 與 `evidence`、讀側 `_dispositions_verdict` 都用同一支 `_disp_type_err`。
  - `[]`、`{}`、`0`、`False` 都會被當型別錯。
  - `None` 與字串維持原本行為。
- **留痕指紋提醒**:印在 `_jsonl_append_verified` 成功之後、只寫 stderr、不改回傳碼。
- **測試**
  - 把「同編號混用」的既有測試改成直寫舊帳,是為了保留讀側守衛的驗證,並加了前置斷言證明寫側先擋,合理。
  - S6 確實隔離了「只有輪次檢查會擋」。
  - S10、S12、S15 都是行為斷言。

## 圖譜固定席

- `Systems/loop-convergence-recording.md`(RISK)與 `Issues/canary-record未落盤事件.md`
  - 新增的寫側擋下只減少帳上出現判不了的形狀。
  - `_jsonl_append_verified` 的寫入加讀回自驗沒動。
  - 提醒與擋下都在它之外,不影響「成功即已落盤」。
- `Systems/design-loop.md`(INVARIANT:處置閘第五步)
  - 處置閘、`.md` 計劃檢查都沒改。
  - 受影響的只有記帳入口與 `loop next` 的範本,不影響該合約。
- `Systems/pitfalls-code-loop.md`
  - `pitfalls` 只在人可讀輸出多印兩行,`--json` 不變,分級算法不變。
- `lumos-cli-read`、`guard-kill`、`bound-tests-gate`、`lumos-cli-lifecycle`
  - 這份 diff 沒碰 `search`、`guard kill`、`code-loop check`、`re-inject`,判不影響。
  - 測試檔有改,但是調整夾具而不是改合約斷言。

最嚴重 severity:minor;blocking 共 0 條。
