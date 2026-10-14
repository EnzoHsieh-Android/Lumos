severity: minor

資安席第六輪報告:在時限內沒有找到能讓新殘留、或殘留反例的擴大不經高風險審就進主線的繞法。我試了你列的各條,修補都擋住;只有一條環境變數的縫,很小,見下面第一條。實驗用 `git clone` 造的 repo,用 `_rc_r4_main_with_residual` 造出一筆合法殘留(決策 d12 在 `Projects/a_計劃`),再用真的 `lumos pitfalls --diff main..HEAD` 判分級。實驗暫存已刪。

**finding 1:入口清理漏掉 `GIT_DIR`,本機能把分級讀成 light**

severity: minor
blocking: 否 — 只影響本機閘;CI 在乾淨環境重算,而且同樣的 `GIT_DIR` 也會讓真正的 `git push` 推到假 repo,所以不是一條實際可走的路。
引句:「os.environ["GIT_NO_REPLACE_OBJECTS"] = "1"」
- 攻擊步驟:主線有殘留,分支上只在 d12 內容尾端加反例。做一個 bare clone,把它的 `main` 指到分支頂端,再用 `GIT_DIR=<該 clone> lumos pitfalls --diff main..HEAD --json` 判分級。
- 結果:`light 改動裡沒有程式檔(只有文件/資料/圖譜)`。同一份改動在乾淨環境判 `high 改到存著已登記殘留的筆記(docs/rc-knowledge/Projects/a_計劃.md)…`。
- 其他變數的結果:`GIT_NAMESPACE`、`GIT_CONFIG_COUNT`(`diff.relative=true`)、`GIT_SHALLOW_FILE` 都仍判 high。`GIT_OBJECT_DIRECTORY` 指到不存在的目錄時,閘直接報錯(失敗即擋,沒放行)。
- 建議:`main()` 順手清掉 `GIT_DIR`、`GIT_WORK_TREE`、`GIT_INDEX_FILE`、`GIT_CONFIG_COUNT` 這類,或明文記成範圍外。
- file: `scripts/lumos:53710`

**逐項實驗(都沒繞過,不另立 finding)**

- **用 `git mv` 改名並改決策**:`docs/rc-knowledge/Projects/a_計劃.md` 改名為 `z_計劃.md` 後再加反例,判 high,理由是「改到存著已登記殘留的筆記(docs/rc-knowledge/Projects/a_計劃.md)」。改動清單用了 `--no-renames`,舊路徑仍會出現。
- **先改索引的 `notes`、指到不存在的篇**:這一次推送就判 high,理由是「殘留索引記的決策所在筆記換了(… a_計劃.md → none.md …)」。
- **分兩次推送**:我讓第一次已經合進主線,主線索引的 `notes` 指向不存在的篇,第二次再改 d12。第二次判 light,因為起點索引已經被改過。這條只靠第一次那道 high 審把關。
  - 第一次推送只有 `lumos doctor` 的 warn(「索引的 notes 跟圖譜不同」),warn 不擋推送。
  - 所以第一次推送的審查席必須拒絕這種「換位置」改動。
  - 這是設計上接受的取捨,不是 bug。
- **決策放在「圖譜檔」判定外的路徑**:索引有記路徑時,任何路徑都比對得到,判定外也沒差。只有「舊索引沒 `notes` 欄、而且圖譜是扁平資料夾又不在 `docs/*-knowledge/`」才判不到。這個組合目前沒有實例:`origin/main` 沒有殘留索引,只有採用本功能前就有索引的專案才碰得到。
- **索引讀不出、鏡頭必答題被忽略**:把頂端索引改成 `{` 後,pitfalls 判 high(「頂端版本的殘留索引讀不出…」),鏡頭仍印出「這次新增的殘留算不出來(頂端的殘留索引讀不出)」和必答題。分級完全不讀鏡頭輸出,所以鏡頭被忽略不影響分級。
- **效能**:10 萬筆索引乘 10 萬個改動檔,`_residual_note_hits` 兩種情況各約 0.07 秒(耗時 0.08 與 0.06 秒),沒有退化。

最高等級 minor,blocking 0 條。
