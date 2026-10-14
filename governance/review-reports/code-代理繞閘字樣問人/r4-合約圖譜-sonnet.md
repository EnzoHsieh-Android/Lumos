severity: major

審查範圍:測試文件組逐 hunk 讀完,程式組只用來核對。以下全部對固定版本 465736e9 判斷(`9981c0e5` 只多了派工材料)。修前版用 `git show 9b8ce146:…/bypass-ask-hook.py`。臨時檔在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/合約圖譜-sonnet/`。

## Findings

1. 指令裡只要有一個空字串參數(`-m ''`、`-m ""`、`''`),整條指令就從結構分類掉到字面判。計劃寫的「用結構分類抓」的寫法因此漏問或誤問。
引句:「k = min(t.index(c) for c in "<>" if c in t)」
severity: major
blocking: 是
- **走到哪一行**:`_tokens` 的 `for t in lex:` 遇到空字串詞。
  - `_is_sep("")` 與 `_is_redirect("")` 都回 False。
  - `all(c in "();<>|&\n" for c in "")` 對空字串回 True,於是走進 `)>`、`;>` 的拆分分支。
  - 該分支的 `min(...)` 對空序列丟 `ValueError`。
  - `bypass_reasons` 把 `ValueError` 當「shlex 切不動」,改走 `_literal`。
- **應該是什麼**:計劃〈做法〉寫字面判只在「引號不成對」或「超過 2 萬字」才走(S4)。空字串引號不該算切不動。
- **重現**:cwd 設 `/Users/someone/work/repo`,指令用 `git commit -m '' …`,輸出是 `bypass_reasons` 的結果。

| 指令 | 修前 9b8ce146 | 修後 465736e9 |
|---|---|---|
| `git commit -m '' -$'n'` | `['commit-n']` | `[]`(漏問) |
| `git commit -m '' --no-\⏎verify`(反斜線加換行切開) | `['no-verify']` | `[]`(漏問) |
| `git commit -m "" -n` | `['commit-n']` | `['literal']` |
| `git config core.hooksPath ''` | `['config-hookspath']` | `['literal']` |
| `git push '' --no-verify` | — | `['literal']` |
| `cd <已存在的暫存 git repo> && git commit -m '' -n` | `[]`(拋棄式豁免) | `['literal']`(誤問) |

- 對照:`git commit -m ' ' -n` 修前修後都是 `['commit-n']`,所以問題只出在空字串。
- 漏問的兩個寫法正是 S1 條款寫「`$'…'` 包住旗標」「續行切開長選項」要抓的。
- 誤問的那條讓「結構分類加拋棄式豁免」整個失效。
- 歸因:有證據的修復回歸。修前能抓,修後掉到字面判。換形狀發生在 r3 把切詞改成 `_Sep`/`_Redir` 的那一段。
- 測試為什麼沒抓到:S1 有 `git config core.hooksPath ""` 這個案例,但斷言只看有沒有 ask,不看理由代號。它靠字面判過關,把這個洞掩蓋了。
- 修法:`_tokens` 的第三個分支先排除空詞。S1 加一條斷言,要求這類案例的理由代號是結構判的代號(例如 `config-hookspath`),不是 `literal`。

2. S4 條款寫了的兩項行為,綁定的測試沒驗。
引句:「目錄唯讀修剪失敗 應 印提示、不需要修剪時 應 也清掉舊殘檔」
severity: minor
blocking: 否
- 條款綁的是 `t_bypass_ask_fallbacks_and_budget`。「目錄唯讀修剪失敗印提示」和「不需要修剪時也清舊殘檔」其實由 `t_hook_event_trim_tmp_unique` 驗,後者沒綁到任何條款。
- 後果:三個月後有人只照條款查綁定測試,會以為這兩項沒有驗證。
- 歸因:未判定(條款和測試各自在不同輪加的)。

3. 〈審計修正紀錄〉「實作期」那條說「預篩階段的 try 不吞例外」沒有測試翻紅、刻意不釘。現在的測試把它釘住了。
引句:「預篩階段的 try 不吞例外」——預篩讀的是已經以替換方式解碼的文字
severity: minor
blocking: 否
- `t_bypass_ask_fallbacks_and_budget` 把 `m.prefilter` 換成會丟例外的函式,斷言 `entry` 回 rc 0 且不輸出。拿掉 `entry` 裡那層 try,這條會紅。
- 同一條也寫「故意改壞 18 種」「17 種有測試翻紅」,但文字只列了 16 種加這一種。數字對不上,且和 S4 條款自相矛盾。

4. d3 和 d4 沒對齊,Systems 節點也沒跟上。
引句:「事實,攻擊面從無限的寫法收成封閉的幾條規則」
severity: minor
blocking: 否
- d3 的 `why_chosen` 仍寫「攻擊面從無限的寫法收成封閉的幾條規則」,而 d4 說 d3 不宣稱封閉。d3 還是 `valid: true`。
- d3 否決方案②的理由是「仍擋不住刪掉重建成連結」。這條理由對出貨版同樣成立(d4 自己承認)。
- 讀 d3 的接手人會以為出貨版擋得住,d3 沒有指到 d4。
- `Systems/代理繞閘問人` 的「不管什麼」清單沒有 d4 那條「同一條指令裡改寫判斷當下已存在的路徑」。節點也沒有對應的 WHY 或 d4 指標。只讀這篇節點的人會漏掉這個攔不到的範圍。
- 歸因:未判定。

5. 計劃對「吃值旗標」的說法只對 `-n` 成立,`--no-verify` 沒照做。
引句:「commit 的長選項 `--message`、`--file` 等會吃下一個詞當值,`--` 之後不再看旗標」
severity: minor
blocking: 否
- 實測(結果是 `bypass_reasons` 回傳):
  - `git commit -m --no-verify` → `['no-verify']`
  - `git push -o --no-verify origin` → `['no-verify']`
  - `git push -- --no-verify` → `['no-verify']`
  - `git commit -m -n`、`git commit -- file -n` → `[]`
- `-m` 的值是 `--no-verify` 時 git 把它當訊息,並不跳過掛鉤。程式碼的 `_hit_codes` 對 `--no-verify` 只做全參數掃描。
- 方向是誤問,符合 d2「寧可漏問」的反方向。但計劃和 S2 都暗示「吃值旗標的值不算」,這裡兩處說法不一致。

6. 複製進來的預算區塊有一句已經過期。
引句:「目前註冊表最小值是 10」
severity: minor
blocking: 否
- 這支註冊的逾時是 5,最小值已經不是 10。
- 因為「有測試要求各份一模一樣」,不能只改這支,要連鄰居一起改,或把那句從逐字複本範圍拿掉。

7. 數字和說明沒有跟著更新。
引句:「量到一週約 371 次」
severity: minor
blocking: 否
- 〈實務隱患〉和 d1 還寫 371 次。〈量測〉後段已更新到 375、387、408。
- `_hookevent.py` 這次的行為改動也沒進節點:修剪失敗會往 stderr 印一行,所有掛鉤共用。「讀檔到換入之間別的程序追加的那一行會遺失」這項已知接受,也只寫在程式註解。`Systems/掛鉤存活事件` 沒有對應 REVISIT 或承認行。

## 固定席節點逐條判

- `lumos-cli-lifecycle`:新增的 WHY 句子內容和 `scripts/lumos`、`merge-claude-settings.py` 的實際改動一致。
  - 名單、狀態列、錨點、Codex 跳過 Bash matcher 都對得上。
  - 綁的 `t_bypass_ask_registered` 只驗安裝名單、狀態列、設定檔、Codex。自裝檔與錨點名單靠既有的集合相等測試。
  - `lumos lint` 0 問題。
  - 新增句子沒碰既有的 ★INVARIANT★(re-inject 保留 sentinel 外內容)→ 不影響。
- `lumos-cli-read`:只是 `scripts/lumos` 同檔牽連。這次沒動 `search` 的濾網 → 不影響。
- `design-loop`:處置閘第五步邏輯沒動。計劃有 `[S1]–[S6]` 條款且 S1–S5 定義了綁定測試 → 符合該 INVARIANT。
- `測試假綠形態`:新測試多數有「前置斷言證明現場成立」。
  - S3 用 `exp` 先建 repo,再斷言放行。
  - 但發現 1 說明 S1 對 `""` 案例只看 ask,屬於「現場走不到被測分支」型假綠,和該 INVARIANT 精神相符 → 影響:這一條。
- `guard-kill`、`pitfalls-code-loop`、`reversibility-governance-ledger` 與其他只列名的節點:只牽涉 `scripts/lumos` 或 `test_lumos.py` 同檔,沒動它們管的邏輯 → 不影響。
- `Issues/code-loop守衛main-direct盲區`:只因為 `test_lumos.py` 同檔被牽連 → 不影響。

## 三個核對問題

1. **原問題修復效果**:r4 配對案例我獨立跑了一部分(修前、修後都載入),結果相同。
   - `git commit -$'\156' -m x`:修前 `[]`,修後 `['commit-n']`
   - `git push $"--no-verify" o`:修前 `[]`,修後 `['no-verify']`
   - `git commit -m 1 >/dev/null -n`:修前 `[]`,修後 `['commit-n']`
   - 保留案例 `echo "x git push --no-verify"` 修前修後都是 `[]`,`git config core.hooksPath 2>/dev/null` 修前修後都是 `[]`。
   - 預篩對 `-$'n'`、`--no-ver\⏎ify` 修後都過。
2. **修補處相鄰路徑**:發現 1 是相鄰路徑的回歸,只出現在空字串參數的形狀。其餘案例我跑的都與修前相同或更好。
3. **同一案例修前、修後**:見發現 1 的表格。

## 未驗範圍

- 沒有跑完整的 `scripts/test_lumos.py`。
- 沒有在 root 權限下驗「目錄唯讀」這條測試。
- 沒有對照 `governance` 的審計條數(r1 33 條、blocking 18 條等)和上輪席報告,因為被要求不讀。
- 全 doctor 中 S12 顯示這份計劃紅 5/綠 0。這是上次規格閘的快取結果,我沒有重跑,不當證據。

最嚴重等級 major,共 1 條 blocking。
