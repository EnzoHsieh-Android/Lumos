severity: blocker
# r2 正確性席(sonnet)——棧別提問表態閘(修訂稿驗收)

前輪驗收:①skip 已解 ②CI 未解(見 C3) ③錨點部分未解、新洞 C5 ④多平台已解 ⑤原文對照已解 ⑥原子寫已解 ⑦派工前表態已解(殘留 C6) ⑧tier 未解(C1/C2)。

### C1 pre-push 的 if/elif 互斥,「不看 tier」在 high+有適用題時反而不經表態檢查
severity: blocker
blocking: 是——核心裁定在最需要它的情境失效。
引句:「tier standard 的既有 advisory 分支改成同一道閘。」
file: `scripts/hooks/pre-push:187`(`if ... "tier": *"high"`)、`scripts/hooks/pre-push:223`(`elif ... "stack_questions"`);tier=high 成立就走不到 elif。

### C2 CI 錯誤訊息硬寫 tier=high,且 ci.yml 不在 DEP
severity: major
blocking: 是——rc=1 也可能是未表態,訊息誤導排查;DEP 遺漏是 r1 已記帳的重複失誤型。
引句:「scripts/hooks/claude/impact-hook.py 棧段過濾」
file: `.github/workflows/ci.yml:48-51`(`::error::tier=high 代碼無 code-loop 留痕`)。

### C3 治理帳事件形狀漏 branch/head_sha,CI 端按分支重建做不到
severity: blocker
blocking: 是——CI 唯一路徑,缺兩鍵機制整個不通。
引句:「並追加治理帳事件 `{"gate":"code-loop","kind":"dispositions","commit":<head_sha>,"dispositions":{…}}`」
file: `scripts/lumos:20421`(`ev.get("branch") == branch and ev.get("head_sha")`)、`governance/.gitignore:12`。

### C4 `git cat-file -e <at_sha>:docs/*-knowledge/...` 的 `*` 不展開,todo 錨點恆判不存在
severity: blocker
blocking: 是——真實 git 指令實測重現:字面 glob 路徑 `fatal: path ... does not exist`。
引句:「`git cat-file -e <at_sha>:docs/*-knowledge/Issues/<名>.md` 存在」
file: `scripts/lumos:20083`(`cmd_dispatch_lens` 從 base_tree 動態解析 `*-knowledge` slug 的正確做法,可借)。

### C5 「root 對 at_sha 乾淨」在單平台 legacy 設定下=整個 repo 要乾淨,系統性假擋本機推送
severity: blocker
blocking: 是——legacy 分支 root=repo_root;多工是常態,WIP 檔會擋掉所有 test: 證據;實務隱患六條排除來源漏了這條。
引句:「要求該平台 root 在 `git diff --quiet <at_sha> -- <root>` 下乾淨」
file: `scripts/lumos:3384`(legacy 分支 `"root": repo_root`)。

### C6 ⚠ 表態與 pass 各綁自己的 sha,「同一套座標邏輯」是否要求相等沒講
severity: major
blocking: 是——派席前表態(commit A)→折入改碼(commit B)→pass;表態 sha=A、pass=B;祖先+簿記白名單那套套到表態上,A→B 非簿記改動會讓表態過期;「改碼後要不要重表態」spec 沒明講。
引句:「用跟 pass 留痕**同一套座標邏輯**解析表態記錄」
引句:「check 取該 sha 最後一筆事件（明文規則）」

### C7 ⚠ DEP 把「棧段過濾」記在 impact-hook.py 名下,撞單源架構
severity: major
blocking: 是——hook 只格式化 `lumos impact --file --json` 輸出;把 when 搬進 hook=觸發規則兩份。
引句:「只注入命中的題；沒命中任何題就不注入棧段。」
引句:「scripts/hooks/claude/impact-hook.py 棧段過濾」
file: `scripts/test_lumos.py:19096`(docstring「單源在 lumos,hook 不持有表」)、`scripts/hooks/claude/impact-hook.py:791`。

### C8 ⚠ S2 要求既有測試樣本改成觸發全表,沒說怎麼觸發
severity: minor
blocking: 否——拼湊命中 7 個 when 的樣本 vs 靠門檻硬灌全表,意義不同。
引句:「既有 `t_pitfalls_stack_questions` 的樣本改成會觸發全表的內容」

### C9 ⚠ 觸發只看 added 行,純刪除 diff 恆零適用題
severity: minor
blocking: 否——與既有 pitfalls 掃描一致,但「刻意不做/實務隱患」沒明講接受。
引句:「每題都必須有觸發；寫不出觸發的題本身就是設計問題。」
file: `scripts/lumos:16697`(刪除行不推進)。

逐節:現況查證數字 177/5 重對一致;五、副產品無新 finding;刻意不做/審計修正紀錄無 finding。
最嚴重 blocker(C1/C3/C4/C5);blocking 共 7 條。
