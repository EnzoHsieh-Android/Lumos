severity: minor

審查範圍:`/tmp/code3-r3.patch` 全文讀完。實量在 rw 工作樹(HEAD 1685194c)上跑,沒改 repo 任何檔。圖譜鏡頭說的尾端固定席筆記沒有附上,所以只就 diff 內動到的三篇筆記判。

## 實量結果

1. 帳增速段與度量段改成逐筆後,尖峰記憶體下降但沒到「不留整份」。
   - 16.4MB 的 `docs/.governance-log.jsonl`,102951 筆。
   - 舊的 `_drift_jsonl_parse`:尖峰 124MB。
   - 新的 `_drift_jsonl_iter`:尖峰 58MB。
   - 度量段 `_gov_metric_events` 會留下事件清單:尖峰 75MB,留存 30MB。
2. `_ns_summary_logical` 已是線性。
   - 單條續行 4MB 約 0.065 秒。
   - 20 萬條條目 3.5MB 約 0.18 秒。
   - 下游 `slot_parse` 與 `parse_rule_fields` 處理 1.9MB 的單條,各約 0.11 秒,也是線性。
3. doctor 在 622 篇圖譜上,S16 到 S19 重組全文的成本可忽略。
   - 只重組一次全部筆記:0.06 秒。
   - S16:0.055 秒。S17:0.42 秒(主要是決策查找)。S18 取列:0.07 秒。S19:0.09 秒。
   - 這四段尖峰共 4.3MB。完整 `lumos doctor` 總共 29 秒,主要在別段。
4. generator 在呼叫端中途 break 或拋例外時沒有資源要放,它不開檔、不持有 handle。壞行與 RecursionError 在 generator 內就吃掉。
5. 推送那支先印後記:印到一半被硬中斷(SIGKILL、停電),當次不會有帳。這跟 m1 與 c1 到 c5 同序,依你的口徑可接受。

## Findings

**R3K1** 印出出錯的兜底句沒有自己的保護,stderr 壞掉時會整支冒出去,帳也沒寫
引句:「print(f"存量漂移檢查:RULE 撤除條件的清單印到一半出錯({type(ex).__name__}),判定照舊", file=sys.stderr)」
- 這是 r1 併發席提過的失敗,這輪改回先印後記、同時拿掉 `_drift_retire_quiet`,又回來了。
- 重現(`/tmp/r3k_rep.py`):stderr 換成寫入就拋 `BrokenPipeError` 的物件,呼叫 `_drift_retire_report(root, "warn", "b", "t", [], ["判不了一項"], [])`。實測結果是例外冒出到呼叫端,`_drift_retire_ledger` 呼叫 0 次,rc 沒回,程序以非 0 結束。
- 影響:warn 模式下本來只列出不擋的推送,會被當成失敗結束碼;`handle`/`listed` 這筆帳也沒了。
- 但 c1 到 c5 的印出同樣不包 stderr,所以只在「核心判定沒東西可印、只有撤除條件有東西」時才暴露,比鄰居窄。筆記宣稱的「記帳與印出出錯各自只講一句」在此情境不成立,筆記該加限定語,或把兜底句的 print 包 try。
- file: `scripts/lumos:32401`(`_drift_retire_guarded`),以及 `_drift_retire_report` 的兩個 except。
severity: minor
blocking: 否 — 只在 stderr 管線已壞時發生,且跟同一道閘 c1 到 c5 同樣不防,不改判定的主路徑都成立

**R3K2** 逐筆 generator 只省掉 dict 清單,整份解碼字串與切行清單仍同時在記憶體,計劃筆記的說法偏滿
引句:「for ln in (raw or b"").decode("utf-8", errors="replace").split("\n"):」
- 實測見上:124MB 降到 58MB,約一半,沒有降到與資料量無關。
- 剩下的 58MB 是 16MB 位元組加整份解碼字串加整份行清單。帳檔尾上限是 24MB(`_GOV_TAIL_CAP`),滿載時估計約 90MB。度量段再留下事件清單,滿載估計約 45MB。
- 改法:先 `raw.split(b"\n")`,逐行才解碼。UTF-8 的 `\n` 不會落在多位元組字元中間,所以結果與現在相同;這樣尖峰只剩位元組本身加一份行清單。
- 筆記「逐筆解析、不留整份清單」描述的是 dict 清單,事實成立,但看不出字串與切行仍整份在。要不要改看你,不改的話筆記補半句。
- file: `scripts/lumos:31262`(`_drift_jsonl_iter`)
severity: minor
blocking: 否 — 有 24MB 上限封頂,滿載尖峰在百 MB 內,doctor 是人工偶爾跑的

## 圖譜鏡頭(逐篇判,都不影響)

- `Systems/lumos-cli-read.md`:S16 到 S19 共用 `_note_summary_entries`、`_lint_new_config` 加 `from_snapshot` 的敘述與程式一致,各 `[test:]` 綁定在 diff 內存在。不破壞該篇宣稱的「S17、S18 不跑 `--ci`、S19 照跑」,因為 `--ci` 分支沒動。
- `Systems/存量漂移守衛.md`:「先印後記(同 m1 與 c1 到 c5)」與 `_drift_retire_report` 一致,rc 判完就定也成立。唯一例外是 R3K1,「各自只講一句」在 stderr 壞掉時不成立。
- `Issues/撤除條件檢查末輪遺留四項.md` 與 `Projects/筆記格子寫法與過期檢查_計劃.md`:只改文字,沒碰合約行或 `[test:]`;第 13 項補的「度量式另由 S18 判」跟程式相符。

最高嚴重度 minor,blocking 0 條
