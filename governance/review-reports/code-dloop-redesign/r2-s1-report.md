# r2-s1 對抗審查報告 — code-dloop-redesign r2

範圍：`code-dloop-redesign-r2-s1.patch`（r1 五組 findings 修復批）。主鏡頭：資源/檔案生命週期
（handle 關閉/暫存殘留/寫入原子性/fd 洩漏）；副鏡頭：修復完整性、fix 引入新洞、相容回歸。

---

## Finding 1 — severity: major

**file:line**: `scripts/lumos:3617`（呼叫點）／`scripts/lumos:3590-3601`（`n_badlines` 計數迴圈，未改動但被新接線）

**摘要**：r1 對「①canary-log 壞行→disposal 閘 fail-closed」的修法，把 `n_badlines` 接進 disposal 閘——但
`n_badlines` 是對整份**共用** `.canary-log.jsonl`（所有 loop 共用同一檔，非 per-loop）逐行掃出的壞行數，
在成功 `json.loads` **之前**累加，因此**無法歸屬到任一 loop_id**。結果：loop A 完全乾淨、自己的每一筆
record 都合法,但只要同一支帳裡**任何一個不相關的 loop B** 有一行壞掉（例如 loop B 那邊曾經半行寫入),
`loop status <A> --disposal` 就會被 loop B 的髒行拖下水,回 rc2 fail-closed——即便 `rounds`（`if
d.get("loop") == loop_id: rounds.append(d)`）早已正確地把不相關 loop 的資料過濾掉,`n_badlines` 卻沒有
做相同的過濾。

**具體失敗場景**：vault 下同時跑兩個 design-loop（`loop-A`、`loop-B`，常態——skill 文件描述「自主迭代
loop」每天挑 gap 開新 loop,舊 loop 可能還沒結案）。loop-B 某次 record 因程序中斷留下半行（`_jsonl_
append_verified` 是這次修復才補上讀回自驗，**在它上線之前**寫入的舊帳仍可能有壞行；或未來任何非
lumos 寫入路徑弄壞一行）。之後對完全健康的 loop-A 跑 `lumos loop status loop-A --disposal --spec ...`
→ 因為同一支帳存在 loop-B 的壞行,`n_badlines>0`,直接印
`ERROR: canary-log 含 {n_badlines} 行不可解析——disposal 閘 fail-closed` 並回 rc2,loop-A 永久卡收斂,
即使它自己的每一筆 record 都是好的。

`n_badlines` 原本的設計意圖（註解「settle fail-closed 用;legacy/panel 維持容忍(行為不變)」）就是承認
這是 settle（罕用高把關閘）才要的全域敏感度,panel 明確選擇不用。disposal 是 design-loop/code-loop
**每輪都要跑**的日常收斂閘（SKILL.md：「... → rc0 即收斂」），把 settle 的全域炸半徑原封不動搬進來，
放大了误伤面。

引句：「return _loop_status_disposal(rounds, loop_id, spec, n_badlines, env.vault.parent)」

---

## Finding 2 — severity: major

**file:line**: `scripts/lumos`（patch 新增於 `cmd_anchor_verify` 尾段，對應目前檔案 `cmd_anchor_verify`
函式,約在 `mismatches.append(...)` 之後、`if as_json:` 之前——**經與目前 working tree 逐行比對確認，
這段程式碼實際上不存在於 `scripts/lumos` 現檔中**，只出現在送審的 diff 文字裡）

**摘要**：這個 hunk 在跟 report/snapshot 留痕完全無關的 `cmd_anchor_verify`（錨點雜湊核對函式）裡插入
一段「dsp_note_flush」批次寫入輔助：開檔存進 `_note_fh` dict、寫一行、`flush()`,但**通篇沒有 `close()`,
沒有 `with`,也沒有任何呼叫端叫用 `_note_append`**（我搜過整份 diff 與現檔,`_note_append(` 只出現在
定義處）。三個問題疊在一起：
1. 資源生命週期：`open(npath, "a", ...)` 拿到的 handle 只靠函式結束後 CPython 引用計數回收,沒有
   `try/finally` 或 `with`,不符本輪審查主鏡頭「handle 關閉」的最低要求——一旦真被接上呼叫點,
   每個不同 `npath` 就永久多開一個 fd,直到 `cmd_anchor_verify` return。
2. 死代碼：目前沒有任何呼叫點,所以這段程式碼**在當下的 diff 裡完全不執行**——但注解宣稱
   「r1 併發面 finding 的補強」,對評審製造「這條 r1 finding 已經修好」的錯覺,實際上什麼都沒修到。
3. 位置錯置：插在 `cmd_anchor_verify`（驗證器 baseline hash 比對）內部,跟它的職責毫無關聯,
   看起來像未完成或誤貼的殘留片段。

**具體失敗場景**：若後續有人依照注解字面意思接上呼叫（例如某個 `--note` 批次寫入路徑),`_note_fh`
會隨不同 `npath` 無上限累積開啟的檔案 handle,直到 `cmd_anchor_verify` 返回才被動回收；若這段邏輯之後
被搬到常駐/迴圈式呼叫的路徑（batch 模式很容易被這樣重構),就是真正的 fd 洩漏。即使不移植,目前
形態也是「宣稱修復但無效」的假修復,會讓下一輪覆核者誤以為「r1 併發面 finding」已收斂。

引句：「fh = _note_fh.setdefault(str(npath), open(npath, "a", encoding="utf-8"))」

---

## Finding 3 — severity: minor

**file:line**: `governance/eval/canary_calibration.py:86`

**摘要**：這次補的「寫後讀回自驗」正是為了防「中斷/併發可留半行且無人發現」（注解原話),但驗證本身
對**它要防的那個場景**沒有例外防護：`json.loads(tail)` 沒被 try/except 包住。如果真的發生併發寫入
把最後一行寫壞（該注解點名的目標場景),`json.loads` 會丟出未捕捉的 `json.decoder.JSONDecodeError`,
腳本直接以未處理例外的 traceback 終止,而不是印出設計好的
`"ERROR: calibration-log 讀回自驗失敗(末行非本次寫入)"` 訊息。修復想做的是「fail loud 但乾淨」,
實際在目標場景下變成「fail loud 但難看（traceback）」。

**具體失敗場景**：兩個 `canary_calibration.py` 行程幾乎同時對同一 `calibration-log.jsonl` 執行
`f.write(json.dumps(entry, ...) + "\n")`（各自獨立 `open(..., "a")`),若寫入未在單一系統呼叫內
完成致使兩者位元組交錯,`splitlines()[-1]` 讀到的最後一行可能是不合法 JSON 片段——此時 `json.loads`
直接炸,而非走到原本設計的錯誤訊息與 `return 2`。由於此工具本身「不進任何 gate」,衝擊面較小
（不會卡住 code-loop/design-loop 收斂),故列 minor 而非 major。

引句：「if json.loads(tail).get("ts") != entry["ts"]:」

---

## Finding 4 — severity: minor

**file:line**: `scripts/lumos:2826`（寫側)、`scripts/lumos:3617` 與 `scripts/lumos:8127`（讀側 `root`
形參)、`scripts/lumos:3908`（`disposal_gate` 用法提示範本)

**摘要**：r1 對「④相對路徑落帳」的說法是「repo root(vault.parent)底下存相對路徑、之外存絕對」,並且
`loop status --disposal` 的 CLI 明確保留、也在自動產生的操作提示裡要求帶
`--repo <root>`（`out["disposal_gate"] = f"lumos loop status {loop_id} --disposal --spec <計劃節點.md>
--repo <root>"`）。但 `_loop_status_disposal` 的 `root` 參數在讀側**根本不是從 `--repo` 傳進來的**——
`cmd_loop_status` 呼叫時傳的是 `env.vault.parent`,完全忽略了自己函式簽章裡已經收到的 `repo`
（來自 `--repo` CLI 值)；寫側 `cmd_canary` 同樣是拿 `env.vault.parent` 當「repo root」,並非用檔案系統
的 git repo 根。這與同檔案既有的慣例（`_rel_cascade_dir`：「repo root:docs/<slug>-knowledge 型= docs
的上層」,顯式判斷 `env.vault.parent.name == "docs"` 再往上一層)不一致——本專案真正的 vault 就是
`docs/lumos-toolchain-knowledge/`（CLAUDE.md 明載),此時 `env.vault.parent` = `docs/`,不是 repo 根,
而 SKILL.md 指定的留痕位置 `governance/review-reports/<loop-id>/` 是 `docs/` 的**同層**目錄,不在
`docs/` 之下——`_pr.relative_to(env.vault.parent.resolve())` 對這類路徑必定丟 `ValueError`,永遠落到
「存絕對路徑」分支,「repo root 相對路徑落帳」這個賣點在真實部署目錄結構下根本不會生效；`--repo`
參數則從頭到尾是裝飾性的、無論填什麼都不影響行為。目前因為寫側/讀側都摔進同一顆「絕對路徑」保底,
不會導致當下測試或同機同 checkout 情境出錯,故列 minor,但這是一顆「文件/CLI 提示宣稱的行為」與
「實際程式碼行為」對不上的隱患：一旦有人依既有慣例（`_rel_cascade_dir`）「修正」寫側改用真正 repo
根,而沒同步修讀側，或者在 git worktree／換 checkout 路徑（本環境明確有 `EnterWorktree`/
`ExitWorktree` 工具鏈,是會被用到的流程)下重新驗證絕對路徑失效的 provenance,就會重現 r1 原本要修的
「留痕假失蹤」症狀。

引句：「_stored = str(_pr.relative_to(env.vault.parent.resolve()))」

---

## 已排查、判定非新洞的項目（供交叉核對，非 finding）

- **round-id `"__legacy"` 合併分組**（`_loop_status_disposal` 把所有無 `round` 欄的記錄併成同一組):
  比對過既有 `_loop_status_panel`（`rid_ = r.get("round")`,同樣把所有 `None` 併一組),行為與既有
  panel 慣例一致,不是這次патч新引入的回歸。
- **`_sha256_file`／`_jsonl_append_verified`**：讀寫都走 `Path.read_bytes()`／`with open(...)`,
  handle 生命週期正常，無洩漏。
- **quote 正則巢狀修復與 10 字下限**：邏輯與新增測試（`t_quote_check_nested_quotes_and_min_length`）
  對得上，未發現繞過路徑。

---

max severity: major
