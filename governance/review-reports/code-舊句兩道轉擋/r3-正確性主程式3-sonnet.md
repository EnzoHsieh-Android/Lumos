severity: clean

## 結論

這份修補我沒找到會失敗的輸入,零 finding。

修補只動 scripts/lumos。我跑了 `-k reread`(256 條)、`-k gate_event`(5 條)、`-k command_index`(14 條)和 `-k m1`,全綠。另外在 `repo`(59f8f92b)與 `repo_before`(88322e46)兩份 `--shared` clone 上各跑同一份重現腳本。

## 三問

**① 原問題的修復效果有何行為證據?**

| claim | input | expected | case_source | before | after |
|---|---|---|---|---|---|
| 深層巢狀的未提交紀錄不再讓 prepare 崩 | 工作目錄放一份 `"["*125000 + "]"*125000`(約 250 KB,在單份上限內),呼叫 `_note_reread_uncommitted` | 回空,不丟例外 | r3-behavior-cases「紀錄讀取守門」 | `RecursionError` | 回 `{}` |
| `drift ack --kind reread` 碰到同樣的檔照樣處理 | 同一個資料夾放一份好紀錄、一份 13 萬層檔、一份 800 層但形狀對的檔,呼叫 `_drift_ack_reread_verdicts` | 13 萬層檔略過,其餘兩份算 | r3-behavior-cases「紀錄讀取守門」 | `RecursionError: Stack overflow` | `['aaaa…','cccc…']` |
| 帳整行含 commit 與 head_sha 後的長度 | 掃 n(0 到 200)× 路徑長度(10、60、150、240),呼叫 `_note_reread_ledger_found` | n=30、路徑 60 以內不超過 4096 | r3-behavior-cases「帳長度」 | n=5 且路徑 150 就 4352,n=30 且路徑 10 就 4280 | 路徑 60 以內全數 ≤4096;路徑 150 以上超過,見下 |
| 超過上限 1 位元組的訊息不再自相矛盾 | `_note_audit_write_verdict` 餵 MAX-1、MAX、MAX+1、MAX+1023、MAX+1024 | 剛好等於上限照寫,多 1 就拒;訊息印位元組 | r3-behavior-cases「訊息」 | 未跑修前版本,未判定 | MAX 與 MAX-1 照寫;MAX+1 起都拒,訊息為「262145 位元組…262144 位元組(256 KB)」 |

- **改壞驗證:** 把 `except RecursionError` 換成別的例外,`t_reread_wt_records_guarded` 紅 3 條。把 `head_sha=tip` 拿掉,`t_reread_block_ledger_fits_4k` 紅 3 條(量到 4144 和 4102)。

**② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**

- **正常路徑:** 好的未提交紀錄(`provenance_ok` 為真、形狀對)仍算 wip,回傳 `{指紋: [檔名]}`,`git add` 列具體檔名。
- **各種壞檔:** 非 UTF-8、`null`、`provenance_ok` 為 1、符號連結、深層巢狀的檔都被略過。`rows` 不是清單的檔經 `_note_reread_wt_verdicts` 後會回到呼叫端,再由 `_note_reread_doc_err` 擋掉。
- **相鄰呼叫者:**
  - `_note_reread_config` 現在改走共用的 `_note_reread_json`,`_metric_gate_off` 也經過它,讀法與失敗口徑一致。
  - `res["wip"]` 從 set 變 dict,只剩 `if res["wip"]`、`len()`、`.values()` 三處用,都相容。
  - `-k m1` 與 `-k gate_event` 綠,舊句檢查帳、筆記形狀擋放寬帳的截法沒變。
- **新帳讀舊帳:** 新舊互讀沒有程式讀 `note` 裡的「路徑=指紋」清單,多出 `layer1_fps` 欄沒有讀者受影響。
- **head_sha 改記被推頂端:** `res.get("tip")` 只在 judge 掃描後才有,更早失敗時為 None,由 `_gate_event` 補 HEAD,所以舊的 undecidable 與 param 路徑不受影響。
- **效能:** 二分最多 50 筆。工作目錄 200 份 230 KB 的紀錄走訪約 0.8 秒。

**③ 新發現的同一案例修前、修後各是什麼結果?** 沒有新發現。

## 已驗但不列為 finding

- 路徑很長(單條約 150 位元組以上,30 篇以上沒對照)時,整行仍有 4572 位元組。原因是 `nodes` 只截到 20 條就停。`_gate_event_fit` 的說明已明寫「再超過照寫」,文件的說法也只到「超過 4 KB 從尾端截」,而且寫入端沒有硬上限,所以只算政策值被超過,不算失敗。修前同一輸入更長(n=30 路徑 150 是 15480),不是回歸。
- 工作目錄走訪沒有總量上限也沒有逾時,只有單份 256 KB 上限。這是修前就有的,歸因為有證據的原有漏查,但我給不出會超時的具體輸入,所以不報。

## 未驗範圍

- `r3-repair-tests.patch` 和 `r3-repair-docs.patch` 的內容,只用跑測試與 grep 側面確認。
- 在實機 pre-push 掛鉤端到端跑一次,沒做。
- 全套測試,依規定沒跑。

## 圖譜固定席

- `Systems/存量漂移守衛`、`Systems/reversibility-governance-ledger`(★RISK★)、`Systems/筆記內容閘`:兩個節點都寫 `_gate_event_fit` 是跨閘共用的 4 KB 裁法。字串 `list_key` 的行為沒變,`t_drift_m1_events_and_budget` 綠,不影響。
- `Systems/guard-kill`(★INVARIANT★ rc 優先序與 JSON 純度):沒碰 guard kill,不影響。
- `Systems/lumos-cli-read`(★INVARIANT★ search 排除 superseded):沒碰 search,不影響。
- `Systems/lumos-cli-lifecycle`(★INVARIANT★ re-inject 只覆蓋 sentinel 之間):沒碰 re-inject,不影響。
- `Systems/pitfalls-code-loop`(★RISK★):修補沒碰 pitfalls 分級,不影響。
- `Issues/code-loop守衛main-direct盲區`:涉及 pre-push 範圍演算,修補未動 pre-push,不影響。

## 角色鏡頭

- **be-api-compat:** 帳多出 `layer1_fps` 欄,`note` 欄少了清單。查過沒有讀取端依賴舊格式,舊讀新、新讀舊都不受影響。
- **be-authz:** 這份修補沒有新增或改動端點,不適用。

最高等級:clean

重現腳本在 `/tmp/lumos-seat-work/code-舊句兩道轉擋/正確性主程式3-sonnet/exp/`(`e1.py` 到 `e6.py`)。
