severity: minor

零個 blocking 級問題,只有一條 minor。已實測的範圍:剝註解的記憶體與時間、撞名判斷的耗時。沒實跑的範圍:整條推送前閘的端到端耗時、新增的 Playwright `-g` 正規式在真的 playwright 裡的行為。

## Findings

1. `_name_filter_collisions` 的 regex_tail 路徑,每綁一個測試名就對全部標題重做一次 `_PW_TAG_TAIL_RE.sub`

severity: minor
blocking: 否

- 位置:修補後 `_name_filter_collisions` 裡 `if tail: cmp = _PW_TAG_TAIL_RE.sub("", cmp)`,放在逐標題迴圈內。標題去 tag 與名字無關,卻對每個綁定名重算。
- 具體輸入:1000 個綁定名,對 22000 個標題(20000 個 test 加 2000 個 group)。
- 實測,同一支腳本,修前版 `5f8f8e48:scripts/lumos` 對修後版 `2e62dcdb`(`web-gaps/scripts/lumos` 與它逐位元組相同):

| 模式 | 修前 | 修後 |
|---|---|---|
| regex_tail | 2.7s | 30.8s(約 11 倍) |
| regex | 2.8s | 4.5s |
| plain | 2.8s | 4.6s |

- 只有 regex_tail 是 11 倍,regex 與 plain 只多約 1.7 倍,所以拖慢主要來自這一行。
- 規模判斷:這個 repo 一次推送要真跑 1000 支 Playwright,每支都要起 playwright,光那段就是分鐘級。30 秒不會讓閘超時被擋,所以只算 minor、不阻擋。
- 順帶量到:`_PW_TAG_TAIL_RE = (?:\s@\S+)+$` 對單一標題內有大量 ` @x` 詞的輸入是平方級。20000 個詞加尾端空白要 6.8 秒,50000 個詞要 42 秒。一般標題不到 200 字,不會碰到,只供參考。
- 歸因:有證據的修復回歸。修前版沒有這個 sub,同一輸入 2.7 秒。
- 建議的方向:`_raw_test_titles` 產生時先算好去 tag 的小寫,每平台一次。

引句:「            cmp = _PW_TAG_TAIL_RE.sub("", cmp)」

## 已驗的主張

- **上一輪 32MB 字串的記憶體問題:一般輸入已修好。**
  - 32MB 的 `"a…`、`"""a…`、`@"a…`、`'a…`、`` `a… `` 都是 0.01 到 0.2 秒,沒有額外記憶體。
  - 32MB 的 `"""` 後接一串 `"k":"v"`(約 640 萬個孤立引號)要 1.8GB,修前版是 0.67GB;時間則是修後 0.43 秒對修前 2.26 秒。
  - 原因:新加的三引號與 `@"` 分支,在每個孤立引號處都推一格重複狀態,等於又走回「群組加星號」的寫法。
  - 這需要 32MB 的測試檔,真實 Kotlin 原始字串不會到這個量級,所以不報 finding。1MB 約 60MB 記憶體,線性。
  - `"\` 重複 32MB 的跳脫字串是 2.2GB,但修前版相同(都是原有分支),不是回歸。
- **剝註解沒有回溯爆炸:** 未閉合的 `"""`、`'''`、`@"`、`/*`,連續 `"`、`'`、`` ` ``,32MB 都在 5 秒內跑完且線性。
- **`_ANCHOR_MAP_CACHE`:** 每個 (平台根、profile 名、檔名錨) 只掃一次整個 repo,比修前「每條懸空各掃一次」少很多。快取是模組層級 dict,指令結束即釋放,沒看到洩漏。
- **`_name_collisions_across`:** 單次呼叫是名字空白數乘以 (group 數加 test 數),一般名字不超過 10 個空白,沒量到問題。
- **git grep 逾時與 Ctrl-C:** 這次的修補差異沒有 `git grep` 的新增或修改(patch 裡搜 `grep` 為 0 筆),不在這輪範圍。

## 圖譜固定席

這輪只改了 `scripts/lumos` 的名稱、撞名與剝註解邏輯和相關文字,沒有動到下列節點宣稱的行為。我沒有逐條跑它們的綁定測試,結論來自讀 diff。
- `lumos-cli-read` 的 search 濾網:不影響,沒碰 search 路徑。
- `design-loop` 的處置閘第五步:不影響,沒動處置閘。
- `guard-kill` 的 rc 優先序與 `--json` 純度:不影響。`_kill_method_name` 改走 `_split_test_ref_ex` 後,撞名改走 `error` verdict,rc 優先序不變。
- `lumos-cli-lifecycle` 的 re-inject:不影響。
- `測試假綠形態`:不影響。

## 未驗範圍

- 整條推送前閘的端到端耗時,以及真的 playwright 對新 `-g` 正規式的行為,沒有實跑。
- 實驗腳本與修前版 `lumos_before` 放在 /tmp/lumos-seat-work/code-測試名收自由字串/資源-sonnet/。

最嚴重 severity:minor,blocking 共 0 條。
