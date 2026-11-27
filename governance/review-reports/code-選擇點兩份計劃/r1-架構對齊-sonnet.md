severity: minor

## A1 兩份新計劃把 PRIOR-ART、RETIRE-IF 放在〈依據來源〉之後,既有計劃一律放在〈白話〉後面
severity: minor
blocking: 否
引句:「PRIOR-ART:〈Practical Mutation Testing at Scale〉(Petrović、Ivanković、Fraser、Just)4.1 Random Selection」
既有做法:同一個目錄裡,有 PRIOR-ART 與〈依據來源〉兩者的計劃共 40 份,其中 38 份把 `PRIOR-ART` / `RETIRE-IF` / `REVISIT` 三行連著放在〈白話〉(或〈為什麼〉)之後、第一個正文節之前。例子:`docs/lumos-toolchain-knowledge/Projects/選擇點變異加速第四段_計劃.md:35`(PRIOR-ART)、`:36`(RETIRE-IF)、`:37`(REVISIT);`docs/lumos-toolchain-knowledge/Projects/選擇點變異加速第三段_計劃.md:36`;`docs/lumos-toolchain-knowledge/Projects/選擇點表第四批常用語法_計劃.md:39`。
差在哪:`選擇點挑法易混淆寫法優先_計劃.md`(PRIOR-ART 在第 150 行、〈依據來源〉在第 141 行)與 `選擇點變異常駐切換最小實驗_計劃.md`(PRIOR-ART 在第 109 行、〈依據來源〉在第 100 行)是庫裡僅有的兩份放在〈依據來源〉之後的。我沒有查到有程式靠這個位置判讀,所以只是位置不同,不算新格式。

## A2 挑法計劃的〈實務隱患〉把 REVISIT 放在節中,後面接一條無關的條列;已排除與守衛面混用兩種寫法
severity: minor
blocking: 否
引句:「REVISIT:2027-01-31 本計劃上線後,確認消費專案的規則包與 lumos 是同一次更新」
既有做法:REVISIT 多半放在檔頭那一組三行(見 A1 的檔案行號),或獨立成行放在說明它的節尾。`docs/lumos-toolchain-knowledge/Projects/選擇點變異覆蓋選測試_計劃.md:39` 就是節尾獨立行的例子。〈實務隱患〉的收尾寫法有兩種:`- 已排除:` 條列(153 份計劃)與裸行 `已排除:`(44 份,例如 `docs/lumos-toolchain-knowledge/Projects/背景快取命中清鎖_計劃.md:45`)。
差在哪:這份計劃的 REVISIT 後面緊接一條「- 改 `scripts/test_lumos.py` 要先 `lumos anchor approve`」的條列,看起來像 REVISIT 的一部分。同一個區塊裡 `已排除:` 用裸行,`- 守衛面:` 卻用條列,兩種寫法混在一起。兩種寫法在庫裡都有先例,所以只是不整齊,不是新做法。

## A3 新 Issue 的摘要沒有 FLAG 行
severity: minor
blocking: 否
引句:「PITFALL:t_m2_cluster_gate 在 CI 偶發超過每支測試 180 秒上限而判紅,斷言本身沒錯」
既有做法:`lumos new issue` 的骨架先放 `FLAG:` 再放 `PITFALL:`(`scripts/lumos:35041`),提示文字也寫「FLAG:<TECHNICAL/DECISION/ORIGIN 三選一>」(`scripts/lumos:35062`)。現有 168 篇 Issue 裡 139 篇帶 FLAG,例如 `docs/lumos-toolchain-knowledge/Issues/背景啟動失敗誤報逾時.md` 摘要第一行是 `FLAG:TECHNICAL`。
差在哪:新 Issue 完全沒有 FLAG 行。庫裡另有 29 篇也沒有,例如 `Issues/收證歸因第三輪留下的小問題.md`,所以有先例。`scripts/lumos:12674` 的檢查只在 FLAG 有寫時驗值,所以不會被擋。⚠ 我沒看出 FLAG 缺了會不會影響推送閘或 doctor。

## 其餘對照,沒問題
- Issue 的 frontmatter(`type`、`status`、`created`、`updated`、`aliases`、`about_code`、`tags`、`summary: |-`)跟骨架與既有 Issue 一致。
- Issue 的 `PITFALL:` 用 `[出處:][根因:][repro:]`,`FACT:` 用 `[來源:生產][confirmed:]`,跟 CLAUDE.md 的表一致,也跟 `Issues/收證歸因第三輪留下的小問題.md` 的摘要寫法一致。
- Issue 正文四節「症狀、根因、現在怎麼繞、什麼條件算修好」跟 `scripts/lumos:35062` 的指定一致。
- 兩份計劃的 frontmatter(`related` 用引號包 `[[…]]`、`lands_in`、`tags` 三條)跟第四段計劃一致。
- 條款句式 `[Sn] 主體 應 … [test:名]` 與 `[manual:說明]` 跟第四段計劃一致。預期值表四欄「條款|輸入|預期|來源」、節名〈回退〉〈實務隱患〉〈落點〉〈依據來源〉〈審計修正紀錄〉也一致。
- `WHY:` 帶 `[出處:][因:][不選:][代價:]`,跟 CLAUDE.md 的欄位表一致。
- 連結一律用 `[[Projects/…]]`、`[[Systems/…]]`、`[[Verification/…]]`,我檢查過連到的節點都存在。第四批計劃那一句改動沿用同一寫法。
- 審計修正紀錄 `r1(日期,4 席):N 條/blocking N/…` 的句式跟第四段計劃一致。

最嚴重:minor
blocking 條數:0
