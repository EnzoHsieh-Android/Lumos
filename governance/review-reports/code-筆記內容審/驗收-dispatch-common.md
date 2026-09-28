變更主題(驗收輪:三輪共 39 條發現已修進代碼;這輪審的是第 3 輪的修正差異 驗收-delta.patch,常見新洞是「修正自己引入的問題」與「上輪沒人看的角落」):lumos(python3 零依賴 CLI,單檔 scripts/lumos)新增「筆記內容審」第二層:推送前把一段 git 範圍裡新寫、終點還在的知識筆記行(Markdown,docs/*-knowledge/)抽出來,切成清單交給 AI 判定者逐行判 CODE/MIXED/CONTEXT;record 照信任方向收報告寫成 governance/note-verdicts/*.json;check 看被推送頂端提交裡的判定檔有沒有涵蓋每一行;skip 略過;計劃收尾(status→done/superseded)時整篇再判(完成審);decision-amend 改未推的決策文字欄。第一層(note-shape)的抽行函式改名成兩層共用(_notelines_*)。還沒接進 pre-push 掛鉤與 CI(等校準)。
設計(唯一規格,條款 S1–S19):/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/docs/lumos-toolchain-knowledge/Projects/筆記內容審_計劃.md
repo 在 /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns(可 Read/Grep 真代碼查證);git 實驗一律 git -C <你自己 mktemp 的臨時目錄>,不准在 repo 根跑 commit/reset/restore/checkout/stash,不准改 repo 裡任何檔。
測試跑法:cd /private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns && python3 scripts/test_lumos.py -k <關鍵字>(例:-k note_audit);不要跑全套(太久)。

輸出格式(硬性,收貨端機械檢查):
- 檔首第一個非空行:severity: <整份最高 clean|minor|major|blocker>
- 引句只准逐字引被審的 patch(驗收-delta.patch);patch 外的既有碼一律走 file: 佐證。
- 每條 finding:標題行「## F<n> <一句話>」(標題裡不寫等級);接著獨立一行「severity: <值>」、獨立一行「blocking: 是|否 — 一句判準」(否↔minor;是↔major/blocker,兩欄不得矛盾);一行「引句:「…」」逐字複製自凍結審材(≥10 字、引句內不要再包「」);審材外查證寫「file: `路徑:行號`」(反引號必加);具體失敗場景(哪個輸入走到哪一行);blocker/major 必附能當場翻紅的最小重現(指令+輸出),附不出就標「未能重現」並自降一級。
- 抑噪:低嚴重度疑慮給不出失敗場景就不要標(但未定義的詞/壞引用/內部不一致一律要報)。沒找到問題就交 severity: clean。
- 最後一行總結:最嚴重 severity、blocking 共幾條。
- 報告只寫進我指定的報告檔,不要改任何其他檔。
