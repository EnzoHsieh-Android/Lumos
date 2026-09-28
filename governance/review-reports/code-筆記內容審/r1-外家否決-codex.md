severity: major

## F1 同一內容編號的多處原文被壓成一處，輕判定可錯放另一處

severity: major  
blocking: 是 — 規格要求清單列出每一處並取最重語境；目前只送第一處給判定者，CONTEXT 可涵蓋未審的 CODE 語境。

引句:「uniq.setdefault(it["id"], it)」

file: `scripts/lumos:24619`

具體失敗場景：同一篇、同一小標題下兩次出現完全相同的文字，但上下文不同。第一處是決策理由，第二處是程式現況。兩處共用內容編號後，`setdefault` 只保留第一處；清單解析及 record 的 `cur_ctx` 也各自只保留一個指紋。判定者若依第一處判為 CONTEXT，第二處便被同一判定放行。

最小重現：

```text
$ python3 -c '<建立兩個相同 id、不同 line/context 的 item，照 prepare 的 uniq/setdefault 後呼叫 _note_audit_render_list>'
input_occurrences= 2
rendered_entries= 1
contains_second_context= False
```

這直接違反 S5 及設計第 2 節「清單列出每一處」。資料結構應保留 `id -> occurrences[]`，CONTEXT 的上下文檢查也必須覆蓋所有 occurrence。

## F2 git 範圍無法解析或是淺層 clone 時，block gate 直接成功放行

severity: major  
blocking: 是 — S10 要求未涵蓋行擋下；CI 設錯 revision 或採預設 shallow checkout 時，整道檢查回 rc0。

引句:「print(f"{gate_word}:範圍 {diff_range} 的終點在本機找不到,跳過(fail-open)", file=sys.stderr)」

file: `scripts/lumos:24395`

具體失敗場景：CI typo、force-push 後找不到 endpoint，或 GitHub Actions 使用常見的 shallow checkout。`_note_audit_resolve` 對前兩種解析失敗及 shallow clone 都回 `(None, 0, None)`；`check` 隨即回 0，完全不檢查判定涵蓋。

最小重現：

```text
$ python3 scripts/lumos note-audit check \
    --diff definitely-missing-base..definitely-missing-tip
筆記內容審:範圍 definitely-missing-base..definitely-missing-tip 的終點在本機找不到,跳過(fail-open)
$ echo $?
0
```

shallow 分支亦明文執行 `return None, 0, None`。block 模式下應 fail-closed；至少 endpoint 不存在應回 rc2，淺層 CI 應回非零並要求 `fetch-depth: 0`。

## F3 `LUMOS_SKIP_NOTE_AUDIT=0` 也會略過全部檢查

severity: major  
blocking: 是 — S11 只授權值 `1` 略過；目前任何非空值都能使本應 rc1 的範圍變成 rc0。

引句:「if os.environ.get("LUMOS_SKIP_NOTE_AUDIT"):」

file: `scripts/lumos:24759`

具體失敗場景：CI 或共用環境以 `LUMOS_SKIP_NOTE_AUDIT=0` 表示關閉 bypass。Python 將 `"0"` 視為真，函式在讀範圍、設定與判定檔前就放行。

最小重現；同一個範圍正常會擋 34 行：

```text
$ python3 scripts/lumos note-audit check --diff HEAD~1..HEAD
擋下:這次推送有 34 行新寫的筆記還沒被判定涵蓋...
RC=1

$ LUMOS_SKIP_NOTE_AUDIT=0 python3 scripts/lumos note-audit check --diff HEAD~1..HEAD
筆記內容審:LUMOS_SKIP_NOTE_AUDIT 設了,這次跳過...
RC=0
```

應與鄰近 gate 一致，嚴格判斷 `os.environ.get(...) == "1"`。

## F4 `decision-amend` 看不到尚未提交的改名，會改寫已推送決策

severity: major  
blocking: 是 — S12 規定遠端已有同編號就必須拒絕；未提交 `git mv` 可繞過這項保護。

引句:「ns = _ns_git(root, "diff", "--name-status", "-z", "-M", ref, "HEAD", "--", vrel)」

file: `scripts/lumos:24866`

具體失敗場景：遠端已有 `Systems/Old.md#d1`；本機執行 `git mv Old.md New.md`，尚未提交，接著對 `Systems/New.md#d1` 執行 `decision-amend`。遠端比對只看 `ref..HEAD`，而 HEAD 尚未含改名，因此查詢錯誤的 `ref:Systems/New.md`，讀不到後便宣稱決策尚未推送。

不寫檔的 git 邊界模擬結果：

```text
WRITE_CALLED
✓ decision-amend Systems/New.md d1.context 改好了(這條決策還沒推上去)
remote_old_contains_d1=True
queried_specs= ['refs/remotes/origin/main:docs/lumos-toolchain-knowledge/Systems/New.md']
rc= 0
```

應以遠端 ref 對工作樹／索引做改名偵測，或先拒絕含未提交改名的節點；不能固定拿 HEAD 當新版。

## F5 `decision-amend` 可把決策的清單欄靜默改成純量並刪掉全部項目

severity: major  
blocking: 是 — 指令承諾只改文字子欄，但只封鎖少數結構欄；傳入合法的巢狀清單欄會造成資料形狀與內容損失。

引句:「new_fm = fm[:k0] + [f"{lead}{field}: {_fmt_decision_value(newtxt)}"] + fm[k1 + 1:]」

file: `scripts/lumos:24897`

具體失敗場景：ADR 的 `alternatives_considered` 是專案既有的巢狀清單。呼叫者依 CLI 的任意 `--field` 介面修改它時，迴圈會吃掉 `- B`、`- C`，再寫成單一 scalar；自驗也只確認解析結果等於新文字，因此照樣成功。

最小函式級重現：

```text
$ decision-amend Systems/X d1 --field alternatives_considered --text "only A"
✓ decision-amend Systems/X.md d1.alternatives_considered 改好了(這條決策還沒推上去)
rc= 0
    alternatives_considered: only A
```

應白名單限定可改的 scalar 文字欄；遇到 list/block 結構必須拒絕，不能自動改型。

## F6 非 UTF-8 清單或報告造成裸 traceback

severity: minor  
blocking: 否 — 無效外部輸入只影響該次 record，但沒有依 CLI 慣例轉成清楚的 rc2。

引句:「lst = _note_audit_parse_list(Path(prepared).read_text(encoding="utf-8"))」

file: `scripts/lumos:24659`

具體失敗場景：AI 報告或清單因編碼錯誤而不是 UTF-8。兩個讀檔區塊只接 `OSError`，`UnicodeDecodeError` 穿透至頂層。

最小重現：

```text
$ python3 scripts/lumos note-audit record \
    --diff HEAD~1..HEAD --prepared /bin/ls --report /bin/ls
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xca ...
RC=1
```

應捕捉 `UnicodeError`，印出哪個檔案編碼不合並回 rc2。

## F7 `search:` 可把不存在的路徑驗成有效零命中證據

severity: minor  
blocking: 否 — 證據只做紀錄、不影響 CODE/MIXED 的擋法，但判定檔會錯誤標成 `evidence_ok: true`。

引句:「if ls is None or ls.returncode != 0 or len(ls.stdout.splitlines()) > _NOTE_AUDIT_SEARCH_CAP:」

file: `scripts/lumos:24558`

具體失敗場景：`git ls-tree` 對不存在的 pathspec 回 rc0、空輸出；後續 `git grep` 非零時 `cnt` 保持 0，因此宣稱 `=> 0` 就會通過。

最小重現：

```text
$ python3 -c '<對 HEAD 呼叫 _note_audit_check_evidence，
  evidence="search: definitely-not-present in no/such/path => 0">'
True
```

應要求 `ls-tree` 至少命中一個 blob/tree；不存在的範圍不能作為有效零命中證據。

## S1–S19 對照

- S1–S4：共用抽行、pre-push 上線點、完成審與標題/結構行的主路徑未見其他破壞；但同 ID 多 occurrence 的語境在 F1 丟失。
- S5：被 F1 破壞。
- S6–S8：信任方向與最重彙總本身成立；F6 是輸入例外，F7 是證據標記假綠。
- S9：亂數檔名及 `_write_lf` 原子換名未見破壞。
- S10–S11：分別被 F2、F3 破壞。
- S12：被 F4、F5 破壞。
- S13、S17、S18：範本渲染、簿記豁免、自裝檔登記與 SPDX 標示均已落入 diff，未見額外違約。
- S14、S15：仍是接線前人工校準義務，本 diff 沒有宣稱完成。
- S16：doctor 路徑已加入，但它給出的 CI 步驟若跑在 shallow checkout，會落入 F2 的 rc0。
- S19：依規格刻意延後到接線提交，本 diff 尚未接線，不能算已滿足，也未構成本輪額外違約。

## 固定席合約核對

- `lumos-cli-read` 的 search superseded/stale invariant、`guard-kill` 的 rc/JSON invariants、`lumos-cli-lifecycle` 的 reinject invariant、`design-loop` 的處置閘 invariant：相關函式與分支均未出現在 diff，判定不受影響。
- `授權與歸屬`：新 vendored 範本含兩行 SPDX；沒有把 LICENSE/COPYING/NOTICE 加入 `_VENDORED_TOOLKIT`，未破壞兩條授權合約。
- `測試假綠形態`：本 diff 未改 guard/bound-test 機制；但指定測試因唯讀沙盒無可用 temp directory，在案例開始前即失敗，不能把「測試綠」當作本席佐證。
- `pitfalls-code-loop`、`loop-convergence-recording`：唯一交集是將 `governance/note-verdicts/` 加入既有 `_BOOKKEEPING_DIRS`，未改處置或收斂語意；這與 S17 的用途一致。
- `lumos-deinit`、`slim-get`、`slim-install`、`slim-uninstall`：只受新範本 vendoring 影響，登記與授權標示齊全，未見刪除使用者授權檔的路徑。
- 其餘固定席節點——`reversibility-governance-ledger`、`節點範圍與索引守衛`、`doctor-irreversible-hint`、`cochange-guard`、`lumos-refcheck`、`check-r-guard`、`check-t-sentinel`、`雙向門放行`、`bound-tests-gate`、`canary-audit`、`規格落成可驗收條件`、`逃逸自動記`、`core-invariant-baseline`、`judge-severity-gate`——對應路徑未被 hunks 修改，未見合約破壞。

總結:最嚴重 severity major、blocking 共 5 條。