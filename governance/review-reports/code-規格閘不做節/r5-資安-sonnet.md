severity: major

這輪我找到 3 條。實驗 repo 是 d9d97ccb 的 clone，做完已刪。

## F1 git replace 讓計劃從推送範圍的檔名清單消失，整道檢查靜默放行

severity: major
blocking: 是 — 推送前的規格閘（pre-push 的 `spec-gate --push-check`）只靠 `git diff --name-only` 決定查哪些計劃，而 git replace 能讓這份清單變空。CI 沒有跑這道檢查，所以本機被繞過就沒有後盾。
引句:「bad, oks = _spec_gate_push_scan(env, rr, plans, git_range, _spec_gate_touched_plans(vrel, touched))」

攻擊步驟與輸出：
1. 造一份風險低、但「## 不做」節寫了「不做退款及實作扣款」的計劃並提交。這裡的提交編號記為 C。
2. 不補輕量審，先跑基線。`spec-gate --push-check d9d97ccb..HEAD` 回 rc=1，訊息是「帳上沒有這個編號的輕量審」。
3. 另造一個樹等於 d9d97ccb 的假提交 N，再 `git replace C N`。
4. 這時 `git diff --name-only d9d97ccb..HEAD | wc -l` 印 0。
5. 重跑同一條 push-check，沒有任何輸出，rc=0，放行。
6. 把 HEAD 推到 bare remote（`--no-verify` 只是省掉實驗用 repo 沒裝的 hook）。remote 收到的是真提交，`ls-tree` 看得到 `Projects/試驗_計劃.md`，歷史有 `a91c0ca2 plan+rec`。replace ref 不會被推出去，所以閘看到的和遠端拿到的不一樣。

`scripts/lumos` 與 `scripts/hooks/pre-push` 都搜不到 `NO_REPLACE` 或 `--no-replace-objects`。這個洞原本就在，但本輪的「推送範圍改到的 Projects 筆記一律重判」整個建立在這份清單上，所以一併受影響。修法是推送閘所有 git 呼叫都加 `--no-replace-objects`（或設 `GIT_NO_REPLACE_OBJECTS=1`）。

佐證：scripts/lumos 的 `_spec_gate_push_check` 內 `git ... diff --name-only` 呼叫（約 `scripts/lumos:9354`，clone 內 `diff` 在 9354 行）。

## F2 一條正規指令就能記出放行的輕量審，席名只比前綴，記帳不驗派工與報告內容

severity: minor
blocking: 否 — 屬於計劃 d1 已承認的天花板（工具不驗身分）；下面只回答你問的「比既有偽造多給了什麼」。
引句:「isinstance(a, str) and a.strip() and not nfc(a.strip()).startswith(」

攻擊步驟與輸出：
1. 接 F1 的情境，不動帳檔，只敲一條正規指令：
   `lumos canary record none --loop 試驗 --auditor "架構 對齊" --severity clean --findings 0 --spec <計劃> --snapshot <計劃副本> --reviewed <副本sha256> --report <3 行的假報告> --note x`
2. 輸出「這筆審查結果(none)記下來了」。
3. 重跑 push-check，輸出「✓ 試驗_計劃:全靠人驗，改動通過小改動閘」，rc=0。
4. 沒有 `loop next` 派工記錄、沒有任何席實際讀過那幾行。報告檔內容完全不被檢查（沒附報告時只擋一次）。
5. 席名檢查只擋以「架構對齊」開頭的名字。「架構 對齊」中間多一個空白就算成通才席。真的只派了架構對齊席、再改個名字，也能過「要有一席不是架構對齊」。

這輪新增的快照與雜湊綁定，擋住了「審無關檔」和「審後改了被略過的行」。但對編排者來說，造一份快照只多一條 `cp` 加 `shasum`。它沒有擋下「沒人審」，只擋下「審了別的東西」。要補強，可以讓 `canary record` 對輕量審要求 `loop next` 的派工紀錄；或席名改成白名單，不再用前綴黑名單。

佐證：scripts/lumos 的 `_spec_gate_push_light` 內 `_seat_ok`（clone 內約 `scripts/lumos:9290`）。

## F3 危險內容放在規格閘看不到的地方：程式碼圍欄、連到的節點正文，都判風險低且不派審

severity: major
blocking: 是 — 這條路徑完全不經過不做清單，所以這次新增的輕量審門檻根本不會被觸發。真的要碰金流或對外寄送的計劃，只要換個寫法就判風險低。
引句:「判風險高的照舊不在這道檢查裡(要走設計審);檔案不在磁碟上(這次刪掉的)不查。」

這條不是這輪修補造成的，是門判定本來的盲區。但本輪的目標正是不讓這類計劃不經審就上去，所以仍須處置。若判定「門的關鍵字掃描本來就是啟發式」而接受，要寫明理由並另立 Issue。

攻擊步驟與輸出（用 `lumos spec-gate` 逐一判）：
1. 同樣的字「實作退款流程並寄送通知信，資料庫刪除舊訂單」，放在 HTML 註解裡，判「風險: 高（退款、寄送）」。放在開頭欄位也判高，所以註解和 frontmatter 有被掃。
2. 同一段放進 ``` 程式碼圍欄，判「風險: 低（硬訊號都沒命中）」，PASS，沒有被略過行，也不需要任何輕量審。
3. 計劃只寫「做法見 [[Systems/外部做法]]」，內容放在另一個沒有風險標籤的 Systems 節點正文，同樣判低、PASS。連到的節點只被檢查合約行與標籤，不掃關鍵字。

## 試過但沒打穿

- **讀不成文字的計劃：** 在推送範圍內放一份非 UTF-8 的計劃，被擋（rc=1）。
- **壞設定與壞帳：** 把 `.lumos/config.json` 改成壞 JSON，被擋（rc=1）。在帳檔塞非 UTF-8 行加十萬層巢狀行，也被擋（rc=1）。
- **窗口與雜湊綁定：** 規格閘留痕之後才能審、審的路徑必須是這份計劃、快照雜湊要對得上，這幾道我沒找到繞法。
- **鐘點不夠沒做到：** 分多次推送、新分支首推，沒有另外做實驗。

最高等級 major，blocking 2 條。
