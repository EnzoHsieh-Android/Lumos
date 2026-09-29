severity: major

鏡頭:整合與知識同步(你是接手的人;預設文件與現實已經對不上,假設你三個月後照這份做,哪裡會撞牆)。

## F1 lands_in 只列 Systems/pitfalls-code-loop,但同一份範本的上一次幾乎同型修改記在 Systems/design-loop 的決策裡,不是這篇
severity: major
blocking: 是(lands_in 是 CLAUDE.md 鐵則五要求的落點宣告,漏列會讓下一個 session 照既有慣例查不到這次改動的決策紀錄,屬於「文件與現實對不上」的具體撞牆場景,不是措辭問題)
引句:「風險高訊號來自落點 [[Systems/pitfalls-code-loop]] 的守衛面標籤」
file: `docs/lumos-toolchain-knowledge/Systems/design-loop.md:110-114` —— 決策 `d6`(2026-08-28)記的正是「code-loop 正確性鏡頭派工措辭升級……改 templates.md §3 + code-loop reference 兩處摘要」,跟本計劃改的是同一份範本、同一節(§3 point 1)、同一種「reference 兩處濃縮複本」形狀。這條決策連 `REVISIT` 性質的回頭看條件都寫在同一篇(design-loop.md:180「鏡頭措辭升級未量測……回頭看條件:下次有兩個以上真 loop 跑過新鏡頭後,人抽看 findings 有沒有比舊名詞清單版更具體」)——這正好是本計劃〈誠實界線〉段落想回答的同一件事(量測正確性鏡頭改版有沒有讓審查挖得更深),但兩篇彼此不連。
失敗場景:三個月後有人想搞懂「§3 正確性鏡頭這九個子題是怎麼長出來的」,照本專案既有慣例會去查 `lumos decisions design-loop`(因為上一次同型改動就記在那裡),結果只看到 2026-08-28 的 d6,以為鏡頭自那之後沒再變過,連帶漏看本計劃的 WHY(小實驗證據、r1 全折的審計修正紀錄、撤除條件),也不會被 design-loop.md:180 的回頭看條件提醒去對照這次的量測結果。`lands_in` 只列 `Systems/pitfalls-code-loop`(該篇的「組件」段落目前只提 `scripts/lumos cmd_pitfalls` 與 `skills/lumos-code-loop/SKILL.md` 的對抗式審查機制,完全沒提 templates.md §3 的正確性鏡頭文字,也沒有類似 design-loop.md d6 那樣的先例)不會被自動找到。

## F2 高風險多席編制的「正確性」鏡頭名字沒有文字連到 §3 第 1 點,設計項 1「panel 多席時它跟著第 1 點走」只是斷言、沒有落地
severity: major
blocking: 是(照 spec 字面只改三處——§3 圍欄本文、reference.md 兩份濃縮複本、SKILL.md 步驟 2 半句指路——high tier 多席編制那條路徑完全沒被碰,而它就是本改動理論上最該生效的高風險場景)
引句:「所以 panel 多席時它跟著第 1 點走:哪一席拿到正確性鏡頭就拿到這五問,不會整段複製給每一席」
file: `skills/lumos-code-loop/SKILL.md:26` —— 「standard 循序只派一位;多席不同鏡頭(正確性 / 併發與資源 / 邊界與輸入 / 合約與圖譜一致)只在 high 的多席編制」——這行是現行代碼審一頁手冊的活文字(不是歷史回放段),`reference.md:570` 有同一份清單的展開版,兩處都只給「正確性」這個鏡頭*名字*,沒有一個字說「這一席的派工詞 = §3 第 1 點原文」。
file: `skills/lumos-design-loop/templates.md:295` —— §7.7 席位立場表的「正確性/邏輯」列只加「立場+預設姿態」(措辭自己改寫),表頭本身寫明「派工詞在既有鏡頭之外,加這兩句」——「既有鏡頭」是什麼內容,同樣沒有指到 §3。
失敗場景:high tier 代碼審派出四席不同鏡頭時,編排者(人或 Claude/Codex)看到 SKILL.md:26 的「正確性」這個詞,若沒有另外去翻 §3 圍欄逐字複製九子題,很可能沿用舊習慣寫一段簡短的「看這段程式碼對不對」——這正是本計劃自己在〈實務隱患〉段承認過的風險模式(「注意力稀釋……派工詞變長,審查員可能被新題帶離」的反面:根本沒被派到)。本計劃的驗收條款 S1–S3 只驗 §3 圍欄本文、reference 兩處濃縮複本、SKILL 步驟 2 三處"有沒有那五個子題標頭",完全沒有測到「high 多席編制那一席實際拿到的派工詞裡有沒有這五題」——也就是說,就算三支守衛測試全綠,high tier 這條路徑仍可能一題都沒問到,而「代碼審資料狀態鏡頭_計劃」的〈現況〉段落本身也沒提到 SKILL.md:26/reference.md:570 這個第二處鏡頭清單,顯示連盤點都不完整。

## F3(informational,不列入 blocking 計數)舊的「冪等併發」等字樣在歷史回放段落有另一層意思,grep 會混到不相干的文字
severity: minor
blocking: 否(純粹文件精度/可搜尋性問題,不會做出錯的審查行為——歷史段本身已明確標記「僅回放判讀用」,不會被現行派工詞引用)
引句:「邊界子題的填空範例拿掉「時區」」
file: `skills/lumos-code-loop/reference.md:239` —— 「bug canary 型別跨 slot 輪替……邊界off-by-one / 資源未釋放 / None例外路徑 / 冪等併發(code-loop 的四型,非 design-loop 的 a/b/c/d)」;`file: skills/lumos-design-loop/reference.md:237` 也有一份用「正確性／邊界／整合」當「不同鏡頭」名字的清單。兩處都被同一篇文件在附近幾行內標成「本段僅回放判讀用」/「保留給……歷史迴圈回放判讀」,是舊制 canary 注入型別的名字,跟本計劃要擴寫的審查員派工詞語意不同(前者是「往 bug 裡插哪一種假錯」,後者是「叫審查員答哪一題」)。
失敗場景:三個月後有人用「lumos search "冪等 併發"」或直接 grep「冪等併發」想確認新舊子題有沒有同步,會連著挖出這兩處歷史回放段的舊四型名字,容易誤判成「這裡也要改」或反過來誤判成「範本本來就沒統一過,不用管」而漏查真正該同步的 §3/reference 濃縮複本。建議本計劃在〈現況〉段落補一句,明講這兩處是歷史回放、不在同步範圍,省得下一個人重新查一次。

## 其餘查證(不構成 finding)
- 已讀,無 finding:Codex 編排路徑不會拿不到新問句。`scripts/lumos:17831-17833` 的 `_CODEX_AGENT_INSTRUCTIONS`(寫進 `CODEX_HOME/agents/lumos_reviewer*.toml` 的 `developer_instructions`)只有輸出格式框架(severity/blocking/引句/file 格式），完全不含「正確性」鏡頭的子題文字;`templates.md:117` 也明講「框架單源=developer_instructions(選得中時派工詞只給審材與鏡頭)」——鏡頭內容(含本次新增的五子題)永遠由編排者當下讀 §3/reference.md 組進派工訊息本文,不管編排者是 Claude 還是 Codex、Codex agent 選不選得中,都走同一份單源,沒有另一條會漏問新問句的路。
- 已讀,無 finding:`scripts/`、`docs/lumos-toolchain-knowledge/Systems/`、`scripts/test_lumos.py` 之外的既有測試檔,grep「冪等與併發」「冪等併發」「邊界：空集合」「例外與 None」全部 0 筆——這份鏡頭目前完全是散文層(skills/*.md),沒有程式碼字串複製它,守衛測試(S1–S3)要新增才會是第一份機械檢查,規劃本身沒有漏掉「程式碼裡也藏了一份」這種風險。
- 已讀,無 finding:「每支檔有家」(node_home)機制的 `_NODEHOME_CODE_EXTS`(`scripts/lumos:22258-22259`)不含 `.md`,`templates.md`/`SKILL.md`/`reference.md` 與新增的測試函式(測試檔本就排除)都不落在該機制管轄——本計劃不需要也不會被擋著要求幫這幾支檔另開 Systems 節點當 `about_code` 的家,F1 的落點問題純屬 `lands_in` 敘事完整性,跟「每支檔有家」的機械擋是兩件事。

總結:最嚴重 major,blocking 共 2 條(F1、F2);F3 為 minor、blocking 否,列出供參考。
