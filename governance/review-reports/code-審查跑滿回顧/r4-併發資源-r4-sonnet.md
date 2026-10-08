severity: major

席:併發資源-r4-sonnet(鏡頭:檔案描述符、先查再開競態、部分寫入殘檔、帳本追加原子性)。
實測範圍:在臨時目錄造帳(沿用 test_lumos 的 `_cr_repo`、`_cr_loop`),沒碰真帳、沒改 repo 檔。
先講沒問題的部分(都實跑過):
- 12 個行程同時 `cap-decision`(含 100K 字元大 note,單行 300KB 以上)追加治理帳:12 行全部完整可解析,追加本身是原子的。
- `_regular_own_fd`、`_ledger_tail_needs_newline`、`_retro_read_bytes` 的開檔與關檔路徑無代號外洩;`--template --write` 的 O_EXCL 建檔加短寫收殘檔邏輯成立。
- 19MB 的真治理帳(唯讀載入)`_retro_gov_events` 約 0.15 秒;`_json_text_escaped` 2MB 輸入約 0.3 秒,效能與記憶體沒有新問題。
- 約 20 處讀者改走 `_ledger_lines` 後,尾端多出來的空字串在每一處都被 `strip()` 後略過或被 ValueError 吞掉,沒有誤計壞行。
下面三條都是「前幾輪修補只接了一部分寫入器」的同一類缺口。

### F1 治理帳的 code-loop 兩支寫入器沒接帳尾補換行與編碼例外(修補引起,上兩輪修補不完整)
severity: major
blocking: 是 — 上一次寫一半的治理帳,下一次 `code-loop pass/skip` 會報「已留痕」但事件被黏進壞行、CI 讀不到,等於成功訊息與落帳脫鉤。
- 輸入:`docs/.governance-log.jsonl` 檔尾缺換行(上次寫到一半被中斷),接著跑 `_codeloop_gov_log`(`code-loop pass` / `skip` 的落帳)。
- 走到哪:`_codeloop_gov_log` 直接 `open(path, "a")` 寫一行,沒有呼叫 `_ledger_tail_needs_newline`。
- 壞在哪:新事件黏在半行後面,整行不是合法 JSON。`_codeloop_read_from_ledger` 讀不到它(回 None);`code-loop pass` 照樣印「✅ 審查通過,已留痕」。本機 pre-push 看的是 marker 檔(過),CI 的乾淨 checkout 只能讀治理帳(擋)。這正是 `_gate_event`、`_append_governance_log` 在 r1 修掉的同一個黏行問題。
- 第二個缺口:`_codeloop_dispositions_gov_log` 與 `_codeloop_gov_log` 只接 `except OSError`,帶孤立代理字元的字串(表態 JSON 裡的 `\udcff`)會丟 UnicodeEncodeError 堆疊,r3 只在 `_gate_event`、`_append_governance_log` 補了這條。(`code-loop pass --note` 路徑上 `_codeloop_write` 的 marker `write_text` 會先丟同一個例外,所以 note 那條走不到治理帳這一段;表態路徑是先寫治理帳,直接炸。)
- 文件說法與事實不符:新 docstring 稱帳尾檢查「治理帳兩支寫入器與 _drift_ledger_append 都呼叫它」,實際追加治理帳的路徑至少有四支。
引句:「★帳尾檢查只有這一支★:治理帳兩支寫入器與 _drift_ledger_append 都呼叫它(r2 架構對齊席)。」
- 佐證行:file: `scripts/lumos:44351`(`_codeloop_gov_log` 的 `open(path, "a")`,前面沒有帳尾檢查)
- 佐證行:file: `scripts/lumos:45172`(`_codeloop_dispositions_gov_log`,同樣直接追加、只接 OSError)
- 重現(臨時目錄,輸出為實跑):
  ```
  gl.write_bytes(b'{"gate": "ci", "kind": "ha')
  m._codeloop_gov_log(root,"feat","passed","ok","a"*40,"2026-10-06T00:00:00+08:00")
  -> 檔尾: ...ha{"ts": ..."gate": "code-loop", "kind": "passed"...}\n   (黏成一行)
  -> 可解析行數 0;m._codeloop_read_from_ledger(root,"feat") 回 None
  對照 m._gate_event(root,"canary","blocked","n",hard=True) 同一個殘檔 -> 新事件自成一行
  m._codeloop_dispositions_gov_log(root,"feat",sha,ts,{"q":{"chosen":"x\udcff"}}) -> UnicodeEncodeError
  ```
- 統一做法:把「補換行加追加加編碼例外」收成一支治理帳追加函式,讓四支寫入器都走它(同一個根因:寫入器各自 `open(path, "a")`)。

### F2 審查帳的寫入器沒有帳尾補換行,一次殘尾就留下永久壞行並擋住處置閘
severity: minor
blocking: 否 — 要先有殘尾才觸發,訊息有指路;但每個殘尾都要人手修一行才能讓處置閘再判。
- 輸入:`docs/.canary-log.jsonl` 檔尾缺換行(寫一半被中斷),接著 `canary record` 任一席。
- 走到哪:`_jsonl_append_verified` 以 `open(path, "a")` 追加,沒有帳尾檢查。
- 壞在哪:新列黏在殘列後面,自驗讀不回該 token,第一次回 2「落盤自驗失敗」;黏出來的那一行永久留在帳上,第二次重記成功,但 `loop status --disposal` 回 2「審查記錄檔有 1 行讀不懂…先不判」,直到人手改帳。審查帳是回顧功能數輪次、判上限的依據。
引句:「治理帳兩支寫入器與 _drift_ledger_append 都呼叫它」
- 佐證行:file: `scripts/lumos:9721`(`_jsonl_append_verified` 的追加)
- 重現(實跑):造殘尾後 `canary record none --loop crx --round r1 ...` 回 2;再記一次回 0;`loop status crx --disposal` 回 2 並印「審查記錄檔有 1 行讀不懂」。
- 與 F1 同根因(寫入器各自追加),可一併由統一追加函式處理。

### F3 治理帳「讀得到但打不開」時的出口指令叫人換檔,而真因是權限(修補引起)
severity: minor
blocking: 否 — 只是照提示做不會好;canary 擋下有指向治理帳,人看得出要查它。
- 輸入:人裁已記、帳上到上限、有卷證;`docs/.governance-log.jsonl` 權限被改成 000(或別的帳號建立而目前帳號沒有讀權限)。
- 走到哪:`_retro_gov_events` 讀檔失敗回 gerr「讀不到(不存在、是資料夾、捷徑或管線,或打不開)」,`_cap_retro_status` 判 gov-bad,`_cap_retro_fix_cmd('gov-bad')` 印出口。
- 壞在哪:出口只說「換回 repo 裡的一般檔(不是符號連結、管線、資料夾,也沒有別的硬連結…)」,沒提權限;檔本來就是一般檔,照做換不出差別。另外「帳修好之前跳過也寫不進去」在這個成因下也不準確(根因是讀權限,不是路徑種類)。
引句:「換回 repo 裡的一般檔(不是符號連結、管線、資料夾,也沒有別的硬連結;」
- 佐證行:file: `scripts/lumos:13458`(gov-bad 的出口句)
- 佐證行:file: `scripts/lumos:13125`(讀不動時 gerr 的來源)
- 重現(實跑):`_cr_decide` 後 `os.chmod(gl, 0)`,`canary record none --loop crx --round r4 ...` 回 2,stderr 末行出口即上述句子,沒有一個字提到權限。

總結:最嚴重 major,blocking 1 條
