severity: major

資安席第三輪找到 2 條 major。第一條在這一輪新加的「刪問答列要升 high」守衛上,可以完全繞過。第二條是「判過 testable 不准改判」只綁節點名與編號字串,換節點名或換編號就能重問。實驗 repo 已刪。

severity: major
blocking: 是 — 在 `.gitattributes` 把治理帳標成不比對內容,刪掉判過 testable 的問答列時,推送前的分級仍是 light,守衛等於沒有。
引句:「只看 -U0 diff 的刪除行(改一列 = 刪一行加一行);新增的問答不算。只讀 git,不載圖譜」
攻擊步驟:
1. 基線:主線上已有一筆 `Systems/S` 反例 c1 的 residual-ask,判 testable。
2. 對照組:分支 ctl 只把 `docs/.governance-log.jsonl` 清空。`lumos pitfalls --diff main..HEAD --no-lint --json` 回 `high`,理由是「推送範圍刪掉或改掉治理帳裡 residual-ask 的列 1 筆」。這是守衛該有的反應。
3. 攻擊組:分支 atk 同一個提交裡新增 `.gitattributes`,內容 `docs/.governance-log.jsonl -diff`,再清空治理帳。
4. 此時 `git diff -U0 main..HEAD -- docs/.governance-log.jsonl` 只印 `Binary files a/docs/.governance-log.jsonl and b/docs/.governance-log.jsonl differ`,沒有任何 `-` 行。`_residual_ask_rows_dropped` 數到 0,`asks_dropped` 不成立。
5. `pitfalls` 回 `light`,理由是「改動裡沒有程式檔(只有文件/資料/圖譜)」。
6. 接著在 atk 上 `lumos guard residual-ask Systems/S 下單不得超賣 --case c1 --checker opus/2026-10-14 --verdict untestable`,rc=0,同一個 c1 被改判 untestable。再提交後 `pitfalls` 仍是 `light`。
7. 結果:判過 testable 的反例被抹掉、重問到想要的答案,推送前沒有被要求高風險審。
8. 同一手法還有:在帳檔前 8000 個位元組放一個 NUL 位元組,git 也會當成二進位檔。
9. 修法方向:這條 `git diff` 加 `--text`,並強制 `--no-textconv`。更穩的是不靠 diff 文字,改成比較起點與頂端兩版帳檔的 residual-ask 列集合,頂端少了任何一列就升 high。

file: `/Users/enzo/orca/workspaces/lumos-toolchain/review-converge/scripts/lumos:44512`

severity: major
blocking: 是 — 「判過 testable 的反例不准改判」只記在節點名加編號字串上,改節點名或改編號就能重問;這正是這一輪要擋的「換個方式重問」,而且同一推送內不會升 high。
引句:「判過 testable 的反例在整個節點都記著,改字換指紋也不准再判 untestable」
攻擊步驟(兩條路各自獨立):
1. 同一個反例換編號。主線已有 `Systems/S` c1 判 testable。執行 `lumos guard residual-ask Systems/S 下單不得超賣 --case c1b --checker opus/2026-10-14 --verdict untestable`,rc=0 並寫入帳。編號只是標籤,反例內容沒有進入比對,所以 c1b、c2 之類都是新反例。
2. 換節點名。`git mv docs/kg/Systems/S.md docs/kg/Systems/S2.md` 並提交,再執行 `lumos guard residual-ask Systems/S2 下單不得超賣 --case c1 --checker opus/2026-10-14 --verdict untestable`,rc=0。`out.testable` 以節點名為鍵,新節點名沒有 testable 紀錄,同一條合約的同一個 c1 就被改判 untestable。
3. 提交後 `pitfalls --diff main..HEAD` 回 `light`,理由是「改動裡沒有程式檔」。新增問答列不算 `asks_dropped`,節點改名也沒有任何守衛反應。
4. 修法方向:testable 的記錄要跟著合約內文走(不看節點名,例如另存只含合約內文的指紋集合),或在改名、搬合約時沿用舊紀錄。反例要比內容而不是編號,至少要求編號對應到反例文字並一起進帳。

file: `/Users/enzo/orca/workspaces/lumos-toolchain/review-converge/scripts/lumos:18931`

另外幾個攻擊角度我檢查後,擋得住或判斷不構成新洞:

- 殘留搬到別的節點、改節點名、手改索引拿掉一筆或縮小守備範圍:`removed` 與 `shrunk` 會升 high。
- 同一推送裡加一列問答再刪一列:淨差異為零,沒有影響。
- 只改索引不改圖譜:`doctor` 會比出不一致。
- 手寫偽造的 residual-ask 列(新增,不經第二個代理)和手寫 `[audit:]` 日期,目前沒有任何守衛擋得住。這是帳本本來就可手改的前提,我沒有實測完整流程,放行。

最高等級是 major,blocking 共 2 條。
