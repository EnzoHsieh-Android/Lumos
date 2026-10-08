severity: minor

## 問1 分層與依賴方向
大致對齊。既有鄰居:cmd_update(scripts/lumos:20912)呼叫 _vendor_toolchain(20859),後者呼叫 _reinject_all(20283),再呼叫 _reinject_claude_block(20311);紀律區塊算內容用 _expected_claude_body(20261,吃 root 路徑)。計劃把 _reinject_claude_block 拆成算與寫,預覽只呼叫算的那段,方向由上往下、沒有跨層直呼,與鄰居一致。唯一待釐清處見 F1(工具檔比對放哪一層)。
引句:「把 `_reinject_claude_block` 拆成「算出新內容」與「寫回去」兩段,預覽只呼叫前一段」
佐證:scripts/lumos:20311(目前算與寫混在同一函式,寫在 20344、20366、20387)

## 問2 命名與錯誤處理
旗標名 `--dry-run` 與 deinit 的旗標定義一致(scripts/lumos:45859);回傳碼成功 0、來源無效 2,與 cmd_deinit dry-run 回 0(20033)、守衛回 2(19997)一致。差異見 F2(預覽會 git pull)、F3(輸出語氣與來源 repo 分支的失敗碼)。
引句:「預覽成功回 0;來源無效、拉不下來照真的 update 的規矩回 2」
佐證:scripts/lumos:20033、20934

## 問3 第二種做法
預覽輸出本身沿用「先算計畫再印」的 deinit 做法,算紀律區塊差異沿用 difflib(20389),沒有另一種差異格式。但工具檔「列出會被換新的檔」有可能在預覽處另寫一份與 _vendor_toolchain 迴圈(20886-20895)相同的比對,形成第二份算法,見 F1。
引句:「用真的 update 那段同一份清單(`_VENDORED_TOOLKIT` 加 `_VENDORED_TREE_FILES`)、同一種比法(逐位元組比)」
佐證:scripts/lumos:20884-20895

## 問4 落點合不合理
合理。Systems/lumos-cli-lifecycle 的 responsibility 明列「安裝、更新、初始化與拆除(install、uninstall、update、…)以及把工具檔複製進消費專案」,update 的現況寫進那篇是對的;deinit 另有 Systems/lumos-deinit 自己的家,但本案不動 deinit,不必寫那篇(related 連結到它即可)。不需另開一篇。
引句:「  - Systems/lumos-cli-lifecycle」
佐證:docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md:9

## F1 工具檔差異清單可能另寫一份比對迴圈
severity: minor
blocking: 否
引句:「用真的 update 那段同一份清單(`_VENDORED_TOOLKIT` 加 `_VENDORED_TREE_FILES`)、同一種比法(逐位元組比)」
佐證:scripts/lumos:20884-20895
說明:既有「逐檔 filecmp 比對、決定要不要複製」的邏輯寫在 _vendor_toolchain 的迴圈裡,與複製動作糾在一起。計劃只說「同一份清單、同一種比法」,沒說抽成共用函式;若預覽處照樣再寫一個迴圈,同一套比對就有兩份,日後清單或規則改動容易漂移。⚠ 計劃的拆法沒涵蓋這段,對 _reinject_claude_block 有拆、對這裡沒講。建議同樣拆成「算清單」與「複製」兩段,預覽與真的 update 共用算清單那段。

## F2 預覽會 git pull 來源,與 deinit --dry-run 的零動作語意不同
severity: minor
blocking: 否
引句:「`--dry-run` 跟真的 update 一樣先 `git pull` 工具來源(帶 `--no-pull` 就不拉)」
佐證:scripts/lumos:20019-20033(deinit dry-run 直接印完回 0,零 mutation,連註解 19998 都寫「純預覽、零 mutation」)、45859(旗標說明「只印會動到什麼,不實際改動」)
說明:同一個旗標名在鄰居代表完全不動任何東西,這裡卻會改動來源 clone(拉到新版)。計劃有講理由並限於來源 clone,結構上站得住,所以只列 minor;但旗標說明文字需跟 deinit 的「不實際改動」區分,例如註明「仍會拉來源,專案不動」,否則使用者按字面理解會被誤導。

## F3 輸出語氣與來源 repo 分支的失敗碼沒對齊
severity: minor
blocking: 否
引句:「所以每個目標檔都印完整差異。目標檔不存在(會新建)、有檔但沒有區塊(會接上)、區塊標記壞掉(不會自動改)也各講一句。」
佐證:scripts/lumos:20021-20032(deinit 預覽:標題行「lumos deinit --dry-run(僅預演,不改動):」加縮排兩格的逐項說明)、20930-20931(來源 repo 分支遇 sentinel_broken 回 2)、20306(壞標記印警示到 stderr)
說明:(a) 計劃沒定預覽的標題行與縮排格式,既有預覽有固定開頭「lumos <指令> --dry-run(僅預演,不改動):」,實作時應沿用。(b) 完整差異與套用時只印 20 行(20295)不同,是刻意的,可接受。(c) 區塊標記壞掉時,真的 update 在來源 repo 分支回 2、其他路徑只警示仍回 0(20934 只看 rc);計劃第 7 點沒說預覽遇壞標記回幾,應明寫與真的 update 同碼,免得預覽回 0 而套用回 2(來源 repo)。

不對齊共 3 條,其中重大 0 條
