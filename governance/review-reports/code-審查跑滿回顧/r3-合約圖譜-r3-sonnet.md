severity: major

席名:合約圖譜-r3-sonnet(鏡頭:合約與圖譜一致、手冊與條款 S1–S18 一致)。實跑都在臨時 repo(`_cr_repo` 造的),沒碰真帳。

### F1 治理帳是符號連結時,人裁寫得進去、讀側卻當沒有,三個擋點全部靜默放行 (修補引起)
severity: major
blocking: 是 — 寫入端回「已記人裁」、閘與擋點讀不到,等於人裁紀錄成功卻不生效(S7、S10「寫成功才算記」被打破),擋住新一輪的機制整個失效且不報錯
- 輸入:`docs/.governance-log.jsonl` 是指向別處的符號連結(例如共用帳)。`loop cap-decision` 照常成功。
- 走到哪:r2 把 `_retro_gov_events` 的讀法從 `read_bytes()`(跟隨捷徑)換成 `_retro_read_bytes` → `_regular_own_fd`(`O_NOFOLLOW`),讀不到就回 `[]`。寫入端 `_gate_event` 用 `open(path, "a")`,照樣跟隨捷徑,把事件寫進捷徑指向的檔。
- 壞在哪:讀寫對同一個檔的看法不一致。`loop retro --template` 回「沒有人裁紀錄」、`canary record` 新一輪 r4 記得進去(rc 0)、處置閘第八步印「—(沒有人裁紀錄,不需要回顧)」。這是 fail-open,而且沒有任何訊息。r2 之前這條路是綠的(`read_bytes` 跟隨捷徑)。
- 引句:「+    raw, _err = _retro_read_bytes(Path(root) / "docs" / GOV_LOG_NAME, limit=None)」
- 佐證行:file: `scripts/lumos:13082`(讀側);file: `scripts/lumos:1495`(`_gate_event` 的寫側 `open(path, "a")`);file: `scripts/test_lumos.py:69886`(`t_cap_retro_r2_gov_not_regular` 只測管線,沒測「捷徑時讀寫要一致」)。
- 重現(臨時 repo,`_cr_repo` + `_cr_loop`,把治理帳改名後建捷徑指回去):

```
DECIDE 0 ✓ 已記人裁:crx extra-round(帳上輪次 r1, r2, r3)
real bytes 405
TEMPLATE 2  擋下:crx 沒有人裁紀錄——要先記人裁
RECORD r4 0 ✓ 這筆審查結果(none)記下來了
[disposal] 跑滿回顧: —(沒有人裁紀錄,不需要回顧)
```

  同一個修補還有同源的小尾巴:`_ledger_tail_needs_newline` 也改成不跟隨捷徑,捷徑帳檔尾缺換行時不再補換行,但寫入照樣跟隨捷徑。出口二選一:讀寫兩邊對「治理帳是捷徑」採同一個處置(寫入端也拒絕並回 1,或讀側跟隨),並補一支兩邊一致的測試。

### F2 條款 S18 綁的測試驗不到它三個承諾裡的兩個
severity: minor
blocking: 否 — 行為本身(F2 之外)有別支測試守著,只是條款與綁定測試對不上,S18 的綁定測試被拿掉那兩段邏輯也不會翻紅
- 條款寫三件事:已存在回 2 不動檔;骨架編碼失敗不留殘檔;卷證資料夾是符號連結或落點在 repo 外回 2 不寫。綁的 `t_cap_retro_template_write_no_clobber` 只驗第一件(加上提示不印重導向)。後兩件分別在 `t_cap_retro_r2_unencodable`、`t_cap_retro_r2_write_symlink_dossier`,條款沒綁。
- 引句:「+- [S18] 當 `--template --write` 執行,回顧檔已存在應回 2 且不動檔;骨架編碼失敗不得留下殘檔;卷證資料夾是符號連結或落點在 repo 外應回 2 且不寫 [test:t_cap_retro_template_write_no_clobber]」
- 佐證行:file: `scripts/test_lumos.py:69554`(`t_cap_retro_template_write_no_clobber` 本體,沒有捷徑資料夾與編碼失敗的案例)。
- 重現:把 `cmd_loop_retro` 裡 `inside` 那段檢查整段拿掉,`t_cap_retro_template_write_no_clobber` 仍綠(只有 `t_cap_retro_r2_write_symlink_dossier` 會紅,而它沒被任何條款綁)。

### F3 檔案超過 256KB 或讀不動時,提示叫人再跑一次 --check,形成繞圈 (修補引起)
severity: minor
blocking: 否 — `--check` 的第一行問題已經寫明「超過 256KB」,人看得懂;但「兩條提示不會互相叫對方先做」這個 r2 承諾(`t_cap_retro_r2_prompt_no_deadend`)在這個角落不成立
- 輸入:回顧檔存在、狀態「沒有」(從沒 `--record`)、檔案 300000 位元組。
- 走到哪:`_cap_retro_check` 讀不到分支呼叫 `_cap_retro_fix_cmd(root, loop_id, 'none')`;該函式只看 lstat 是不是一般檔,是 → 回「回顧檔已在、還沒記:--check 過了再 --record」。
- 壞在哪:`--check` 與 `--record` 輸出的是「回顧檔超過 256KB(…)→ 回顧檔已在、還沒記:lumos loop retro crx --check 過了再 lumos loop retro crx --record」;處置閘第八步也叫人跑 `--check`,而 `--check` 又叫人跑 `--check`。`--template --write` 因檔已存在回 2,也導回同一句。沒有任何一處告訴人「把檔縮到 256KB 以內」(chmod 000 的檔同理)。
- 引句:「+        return f"回顧檔已在、還沒記:{_retro_cmd(loop_id, '--check')} 過了再 {_retro_cmd(loop_id, '--record')}"」
- 佐證行:file: `scripts/lumos:13355`(`_cap_retro_fix_cmd`);file: `scripts/lumos:13188`(`_cap_retro_check` 讀不到分支)。
- 重現:臨時 repo 記人裁後 `cap-retro.json` 寫 300000 個 `x`,`loop retro crx --check`、`--record`、`--template --write` 輸出皆如上。

### F4 筆記與函式說明沒跟上 r2 的切行改法(\r、處置閘讀帳),且新測試沒被任何筆記引用
severity: minor
blocking: 否 — 只是讓下一個讀筆記的人以為切行規則是 `split("\n")`、以為處置閘還在用 splitlines
- `_canary_ledger_scan` 的 docstring 與 `Systems/loop-retro.md` 的 r1 PITFALL 都寫「單一讀法用 split("\n")」,但 r2 後實際是 `_ledger_lines`(認 `\r\n`、`\n`、`\r`),程式碼是依據,筆記沒改;`t_cap_retro_r2_cr_line_endings`(守 `\r` 行尾與處置閘不再劈 U+2028)沒有任何筆記或條款引用。
- 計劃〈誠實界線〉那條「處置閘自己的讀帳迴圈、doctor S12、`_loop_close_stamps` 仍用 splitlines」已過期一半:處置閘的讀帳迴圈這次已改 `_ledger_lines`(`cmd_loop_status`),留下的只有 doctor S12 與 `_loop_close_stamps`。同一區塊多插的 r2 那條缺口說明夾在原句與它的 `REVISIT:2026-11-06` 之間,違反「回頭條件緊鄰原句」。
- 引句:「     ★切行用 split("\\n")★:寫入端 json.dumps(ensure_ascii=False) 不跳脫 U+2028/U+2029/U+0085,splitlines 會把含它們的一列劈成兩半、」
- 佐證(筆記同一句):`loop-retro.md` 該行寫「審查帳單一讀法改成 split("\n")」,在 diff 第 132 行當上下文出現,r2 沒改
- 佐證行:file: `scripts/lumos:414`(docstring);file: `docs/lumos-toolchain-knowledge/Systems/loop-retro.md:24`;file: `docs/lumos-toolchain-knowledge/Projects/審查跑滿回顧_計劃.md:107`;file: `scripts/lumos:2276`(doctor S12 仍 splitlines)。

### 查過沒問題(不列為 finding)
- `_ledger_tail_needs_newline`、`_regular_own_fd`(預設 `require_owner=True` 不變,`_local_ledger_append` 仍擋別人的檔)、`_drift_ledger_append` 三個呼叫者行為與筆記 reversibility-governance-ledger 的敘述一致;`_gate_event`、`_append_governance_log` 呼叫同一支。
- `_esc_clean` 擴大清除範圍(雙向覆寫、孤立代理字元)對 INVARIANT 行(canary-audit 兩條)無影響:`_jsonl_append_verified` 未動。
- 手冊六處到頂句與指令速查、templates.md 都教 `--template --write`、無 `--template >`;計劃條款 S3、S6、S11、S14–S17 的描述與程式一致;`[test:]` 名稱在三篇筆記裡都找得到對應函式。

總結:最嚴重 major,blocking 1 條
