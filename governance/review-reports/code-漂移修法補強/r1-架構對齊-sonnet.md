severity: minor

## F1 佔位字 `<卷證>`、`<sha>` 在兩處各存一份字面
severity: minor
blocking: 否
引句:「_SET_COND_SLOTS = ("<整項新內容>", "<卷證>", "<sha>")」
佐證行:file: `scripts/lumos:27633`(既有 `_DRIFT_PLACEHOLDER_RE` 已含 `sha|卷證`,並由 `_drift_placeholder_err` 在 27502、27713、27726 共用)
1. 證據頁印的佔位字 `<卷證>`、`<sha>` 原本只由 `_DRIFT_PLACEHOLDER_RE` 認,這次 `lumos set` 那側另開一份 `_SET_COND_SLOTS` 字面,證據頁範本從後者取字(`_SET_COND_SLOTS[1]`、`[2]`)。
2. 兩份沒有機械連動:若日後改範本用字,`--reason` 那側的正則不會跟著變,照貼會漏擋。計劃與註解已明說「用途不同、不合併」,故只標 minor;佐證測試未跑,未能重現失敗場景。

## 逐項對齊檢查(判為一致,不列 finding)
- c4 同提交列檔:走 `_nodehome_git` / `_nodehome_split_z` / `_nodehome_show`(file: `scripts/lumos:23635`、`23643`、`23648`),它們底層是 `_lens_git`,沒自己呼叫 subprocess。一致。
- 終端輸出:新增的目錄列印過 `_nodehome_show` 加 `_esc_clean`,與同函式既有寫法一致。
- c3 `--reason` 佔位字檢查重用 `_drift_placeholder_err`(file: `scripts/lumos:27636`),與 c2、ack 同一支。一致。
- 刪除守衛 `_VENDORED_ALL` 純路徑跳過:與既有四處 `_vendored_state(root)[0]`(file: `scripts/lumos:18379`、`24491`、`24623`)口徑不同,但計劃明列為刻意,不列。
- 治理事件走既有 `_append_governance_log`,只在 note 加尾巴,沒另開寫入路徑。

## 圖譜鏡頭
未逐條展開(本席只判架構對齊);diff 沒有引入第二套 git、引號或治理寫入做法,判不影響架構層合約。

最高等級:minor
