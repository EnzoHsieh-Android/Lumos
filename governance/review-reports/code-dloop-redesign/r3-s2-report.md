# code-dloop-redesign r3 s2 — 第三輪對抗審查報告

審查對象：`/private/tmp/.../scratchpad/codeloop/code-dloop-redesign-r3-s2.patch`（HEAD→工作樹全量），
repo 現況（`git status` clean、與 patch 對照）於 `/Users/enzo/harness/lumos-toolchain` 逐條查證，
關鍵發現皆已用構造案例對真代碼跑過（見各條「查證」）。

## 0. 前置：patch 檔與 repo 現況有一段落差（先講清楚，免得後面的結論被誤讀）

引句：「+    # dsp_dup_skip: 同鍵重複寫入預檢(重跑同指令不髒帳;逐行解析,壞行跳過)」

`code-dloop-redesign-r3-s2.patch` 對 `_jsonl_append_verified`（`scripts/lumos`）多帶一段 hunk：
在 append 前先逐行掃描，若同一 `key_field=key_value` 已存在就直接印 WARN、`return 0`（不寫新行）。
但用 `git diff -U10 -- scripts/lumos governance/eval/canary_calibration.py scripts/test_lumos.py`
對照 repo 現況（clean 工作樹，與 HEAD `ba3ae1f` 的差異），**這段 hunk 完全不存在**——全文搜尋
`dsp_dup_skip`／「已存在,跳過重複寫入」在整個 repo 掃零命中。patch 檔其餘 147 個 hunk 與工作樹逐字一致，
唯獨這一段是幽靈 hunk。

這代表本輪送審的 patch 與實際要進 repo 的內容不是同一份——不確定是「已經反悔拿掉但 patch 檔沒重出」
還是「patch 檔誤帶了別的分支/草稿的一段」。**下面的分析已排除這段幽靈 hunk**（因為它不在真代碼裡，
對真代碼的行為判斷不受影響）；但如果這段 hunk 之後真的要落地，先提醒一個潛在洞供之後參考：
它只比對 `key_field`/`key_value` 是否已存在，不比對整筆 `rec` 內容是否相同——若呼叫端用同一個
`--token` 送出兩筆**內容不同**的紀錄（非真正的「重跑同指令」），第二筆會被靜默吞掉並回報成功（rc0），
但實際落盤的仍是第一筆內容，違反「record 回報成功⟺該行已落盤且可讀回」的字面意圖（帳上確實有一行
帶該 key，但不是呼叫端剛剛想寫的那一行）。這段目前不在 repo 裡，故不列入下面編號 findings。

---

## Finding 1（HIGH，已用真代碼構造 repro 證實）：round-less `__seq{N}` 自動鍵與使用者可控 `--round` 值同一命名空間，可撞鍵讓新輪冒充舊輪的處置

檔案：`scripts/lumos`，`_loop_status_disposal`

引句：「groups[f"__seq{len(groups)}"] = [r]」

round-less 記錄的自動分組鍵用字串樣式 `__seq0`、`__seq1`…（`len(groups)` 遞增）。但緊接著的
`--round` 顯式值完全沒有格式驗證（`cmd_canary` 裡 `if round_id: rec["round"] = round_id`，
任何字串皆收）。兩者共用同一個 `groups` dict 的鍵空間——若某筆紀錄的 `--round` 字面值剛好等於
`__seq{N}`（N=當下已出現的 round-less 筆數），它會被 `groups.setdefault(rid_, []).append(r)`
併進**同一組**，而不是被視為新的一輪。

實測構造（真代碼、真 CLI，非臆測）：
1. 先寫一筆 round-less carrier（`findings_set` 齊全、report/snapshot 齊全、quote 能錨定）→
   單獨跑 `loop status --disposal` 已合法 PASS（rc0）。
2. 之後補一筆**新的判定**：`--round __seq0`（撞上第 1 步产生的自動鍵）、`kind=missed`、
   `severity=blocker`、**沒有帶 findings_set**（代表這一輪的 blocker 還沒被處置）。
3. 再跑 `loop status --disposal`：**rc0 PASS**，輸出仍是
   `✅ DISPOSAL GATE PASS`，兩筆被顯示為同一輪的 `__seq0.1`/`__seq0.2`，讀的還是第 1 步那筆
   舊的、已經處置過的 `findings_set` 當作「本輪」的處置集合。

這正是 r1/r2 兩輪已經修過好幾次的同一類洞（「較早 carrier 冒充最新判定」）的變體——差別只在於
這次的攻擊向量不是「round-id 被隔開後重現」（已有守衛），而是「显式 round-id 撞上内部自動鍵」
（完全沒守衛）。只要審查者（或任何呼叫 `canary record --round` 的腳本）用到 `__seq0`／`__seq1`
這種名字（不需要惡意，光是「不知道這是內部保留字」就會踩到），一個帶 blocker、完全沒處置的新輪
就能被舊輪的乾淨處置紀錄「借殼」通過。

修法方向：round-less 自動鍵改用不落在字串鍵空間的形式（例如 `(None, idx)` tuple 當 key，
或明確保留字首碼並在 `cmd_canary` 驗證 `--round` 不得以該保留字首碼開頭、rc2 擋掉）。

---

## Finding 2（HIGH，已用真代碼構造 repro 證實）：巢狀引號修法造成「開閉引號型態不一致」的引句被整條靜默丟棄，不進 miss 判定

檔案：`scripts/lumos`，`_quote_rows`

引句：「quotes = [m.group(1) if m.group(1) is not None else m.group(2)
              for m in re.finditer(r"引句[：:]\s*(?:「([^」]+)」|『([^』]+)』)", rtext)]」

本輪把抽取正則從「`[「『]…[」』]`（開閉可混用）」改成「`「…」` 或 `『…』`（開閉必須同型）」，
目的是修巢狀 `『』` 被提前截斷的洞（合理，也有測試覆蓋）。但副作用是：**開閉括號型態不一致
的引句（例如打字打成 `『…」`）現在完全不匹配任一分支，等於從 `quotes` 清單裡整條消失**，
不會被算進 miss，也不會讓整體判定變成「零引句」（只要報告裡還有其他寫對的引句）。

舊正則（`[「『]([^」』]+)[」』]`）對開閉不一致仍會匹配（只要不含另一種括號字元），所以舊行為
是「抽出來、比對、miss」；新行為是「根本抽不出來、悄悄跳過」。這把「验不了要 fail loud」的
設計原則（本函式 docstring 自己講的）反過來變成了「验不了就不算」。

實測構造（真代碼、真 CLI）：
```
snap.md: 本規則規定甲項必須先審查才能生效,乙項則不需要。
report.md:
  引句：「本規則規定甲項必須先審查才能生效」
  引句：『這句話快照裡完全不存在的編造內容」某某   ← 開『閉」，打字誤植
```
`python3 scripts/lumos quote-check report.md --spec snap.md` → **rc0**，輸出只印出第一條、
判「✅ 全數錨定」。同一份文字餵給*舊*正則（`re.findall`）能抽出兩條、第二條（編造內容）
比對 snap 會 miss——也就是說，**本輪修的這個正則讓一條原本會被抓到的偽造引句，變成完全不被檢查**，
而且不是靠內容矇混過關,是靠打錯一個括號字元就整條消失。`_loop_status_disposal` 的 ④ 也是
呼叫同一份 `_quote_rows`,受影響路徑相同。

由於 quote-check／disposal 閘的存在理由就是防「LLM 審查員編造引句蒙混過關」，這個回歸直接
削弱了本輪標榜要加強的機制。修法：括號不同型時不要整條丟棄——應歸類為「抽到但格式不合法」，
一律判 `ok=False`（比照 `too_short` 的處理方式），而不是讓正則直接不匹配。

---

## Finding 3（MEDIUM，已用真代碼構造 repro 證實）：`--disposal` 的留痕路徑解析改用 `_vault_repo_root(env)` 後，`--repo` 旗標被靜默忽略——git-less 部署環境下合法 loop 會假性 FAIL

檔案：`scripts/lumos`，`cmd_loop_status` / `_loop_status_disposal`

引句：「return _loop_status_disposal(rounds, loop_id, spec, n_badlines, _vault_repo_root(env),
                                     bad_linenos=bad_linenos)」

`loop status --disposal` 的 CLI 仍然接受（不拒絕）`--repo`（`--disposal` 的互斥檢查清單裡沒有
`repo`），但實際解析 report/snapshot 相對路徑的 root 只用 `_vault_repo_root(env)`（向上找
`.git`，找不到就退 `vault.parent`），完全不理會呼叫端傳的 `--repo`。對照同一函式裡的手足
`--settle` 路徑：`_loop_status_settle(..., repo)` 內部確實走 `_anchor_repo_root(repo)`，
`--repo` 顯式優先——兩條路徑對同一顆旗標的語意不一致。

這在「record 當下與 gate 執行當下環境一致」時不會出事（因為寫讀兩側各自重算 `_vault_repo_root`，
會算出相同值，自洽）。但一旦這兩個時間點環境不一致——最常見的就是 CI 產物/tarball 部署（複製
專案樹但不含 `.git`，相當常見的打包方式）——`_vault_repo_root` 在 record 當下（`.git` 還在）
算出真正的 repo root、把路徑存成相對路徑；到了 disposal 執行當下（`.git` 已經不在，例如部署後
的環境）退回 `vault.parent`，即使呼叫端正確地用 `--repo` 指出真正的 root，也會被忽略,
造成路徑解析錯誤。

實測構造（真代碼、真 CLI）：
1. 在含 `.git` 的臨時 repo 下 `canary record`（vault=`docs/kg`，report 用相對路徑
   `governance/r.md`）→ 帳面存 `"report_path": "governance/r.md"`（相對 repo root）。
2. 把整棵樹複製到另一個目錄並**刪掉 `.git`**（模擬 CI 產物/無 git 的部署環境）。
3. 在複製後的環境跑 `loop status --disposal --repo <正確的 deploy 根目錄>`（`--repo` 給的是對的）：
   **rc1 FAIL**，輸出：
   ```
   [disposal] 留痕: ✗ — r1.1 report 讀不到(governance/r.md)——record 完刪檔照樣擋
   [disposal] 留痕: ✗ — r1.1 snapshot 讀不到(snap.md)——record 完刪檔照樣擋
   ```
   即使檔案原封不動、`--repo` 正確給出,gate 仍假性 FAIL——因為它算的 root 是
   `deploy/docs`（`vault.parent`）而不是 `deploy`。

`skills/lumos-design-loop/SKILL.md` 本輪也加了一句「路徑以 repo root 相對落帳,gate 換 cwd 照樣
可重驗」,這句話在「git 一直都在」的前提下成立,但在上述 git-less 部署情境下不成立,文件的
承諾與實作有落差。

修法方向：`_loop_status_disposal`／呼叫端優先採用顯式 `--repo`（比照 `_anchor_repo_root` 的
「顯式優先、否則向上找 `.git`」慣例），只有未給 `--repo` 時才退回 `_vault_repo_root(env)` 自動偵測。

---

## 掃過但未列入 findings 的項目（有找但夠不上具體錯誤場景/嚴重度，僅記錄不佔用 finding 名額）

- `_loop_status_disposal` 的留痕重驗：若 carrier 本身缺 report/snapshot,會直接印「留痕缺席」
  並跳過對其他席（非 carrier）的全席重驗迴圈。這不會導致誤判 PASS（本來就已經 FAIL 了）,只是
  診斷訊息不夠完整（沒有一次列出所有問題席）,不影響最終 rc,不佔 finding 名額。
- `canary_calibration.py` 的讀回自驗（run_id 全檔掃描 + 半行補換行）：邏輯與新增測試
  `t_calibration_readback_hardening` 皆已實跑通過,未發現新洞。
- badlines rc2 訊息附行號（`bad_linenos`）：邏輯與呼叫鏈核對一致,無新增問題。

## 驗證方式

- `python3 scripts/test_lumos.py -k disposal_gate` → 28 passed, 0 failed（含 r1/r2/T4 三批新測試）。
- `python3 scripts/test_lumos.py -k calibration_readback` → 3 passed, 0 failed。
- `python3 scripts/test_lumos.py -k quote_check_nested` → 3 passed, 0 failed。
- Finding 1/2/3 均另外寫了獨立於既有測試套件之外的最小 repro 腳本,直接呼叫真實
  `scripts/lumos` CLI（非 mock）,附完整輸出於上文。
