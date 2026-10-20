severity: minor

我拿本 repo 圖譜(907 篇、11MB)當基準,另造病態輸入實測。基準跑一次約 0.9 秒,常駐記憶體約 305MB,其中約 300MB 是直譯器載入 `scripts/lumos` 本身的底子。檔案描述元沒有外洩,容量上限也都是先判再讀,所以我只報下面三條。

## 檔案描述元(第①項)
- `_secinv_open_rel`、`_secinv_lstat_rel`、`_secinv_descend`、`_secinv_snapshot`、`_secinv_read_rel` 的目錄 fd 和檔案 fd 都在 `finally` 裡關,例外、提早 return 都會關。
- `_regular_own_fd` 判不是一般檔時會先 `os.close` 再回 None。
- 實測 1500 層巢狀目錄:`RecursionError` 被接住,輸出 `enumeration_failed 目錄巢狀太深`、`read_complete: false`,沒有崩潰。重列舉階段也沒有重複記錯。

## 上限先判還是先讀(第②項)
- 單檔先用 `fstat` 判 2MiB,總量判剩餘額度,最多只讀 `min(...)+1` 位元組,不會整份讀進記憶體再判。
- 1MB 全是空行的圍欄檔,以及 4 萬組偽圍欄行的檔(1.8MB),都在 1.2 秒內跑完,常駐記憶體約 316~364MB,沒有爆。

## Findings

### 1.
severity: minor
blocking: 否
- **位置:** `_secinv_surface` 與 `_secinv_coverage`。
- **問題:** 每個入口都對全部現行控制項掃三遍(`sorted(... if ... sid in r["surfaces"])`,其中 `r["surfaces"]` 是 list 比對),時間是「入口數 × 控制項數」。上限 64MiB 沒擋到這裡。
- **重現:**
  - 造法:1 份 inventory,多篇 `Systems` 各放控制項,每條掛一個入口。
  - 4 篇共 6000 條控制項、2000 個入口,3.9 秒。
  - 8 篇共 12000 條、4000 個入口,15.1 秒(約 4 倍)。
  - 用 cProfile 看,`_secinv_surface` 佔 17.5 秒中的 12.8 秒。
- **推算:** 順著比例到 64MiB 上限(約 20 萬條、約 1.2 萬個入口),會跑數十分鐘。這是我外推的,沒實跑。
- **修法方向:** 先把控制項依入口 id 建一次索引,再逐入口查。
- 引句:「ent = _secinv_surface(s["id"], s["description"], live)」

### 2.
severity: minor
blocking: 否
- **位置:** `_secinv_check_source`。
- **問題:** 每條 invariant 控制項都重新對來源節點呼叫 `extract_contracts` 和 `strip_test_refs`,同一節點被重算「控制項數」次。時間是「控制項數 × 該節點合約數」。
- **重現:**
  - 造法:一個 `Systems/big-inv.md` 放 N 條 `★INVARIANT★`,N 條控制項各指其中一條。
  - N=1000 時 3.15 秒,N=2000 時 8.1 秒。
  - 在 N=2000 的情形用 cProfile,`invariant_test_refs`/`strip_test_refs` 被呼叫了約 400 萬次(`strip_test_refs` 的累計時間是整體 27 秒中的約 12 秒)。
- **修法方向:** 在 `_secinv_build` 內建一份「節點 → 合約文字計數」的快取,每個節點只算一次。
- 引句:「hits = [strip_test_refs(x)[0] for x in extract_contracts(env.notes[srel])[0]].count(src["exact_claim"])」

### 3.
severity: minor
blocking: 否
- **位置:** `_secinv_list_dir`。
- **問題:** 10000 檔上限只算 `.md`,非 `.md` 的項目和目錄數都不設限,而且整層的名字和 `lstat` 都先收進 `out` 才排序。
- **重現:** 一個目錄放 30 萬個 `.txt`,常駐記憶體升到 564MB(基準 305MB),耗時 6.3 秒,每項約 850 位元組。這 30 萬項其實都被略過,不會被讀。照這個比例推,幾百萬項會到數 GB。這個外推我沒實跑。
- **修法方向:** 在列舉時對「總項目數」也設一個上限。
- 引句:「out.append((e.name, e.stat(follow_symlinks=False)))」

## 圖譜鏡頭(固定席節點)
- **`lumos-cli-read` 的 INVARIANT(search 預設排除 superseded)和 `design-loop`(處置閘)的 INVARIANT:** 這份 diff 只新增 `security` 子命令,並把 `_visible_lines` 的圍欄判定抽成 `_fence_regions`,沒有碰 `search` 或處置閘的程式路徑,判不影響。
- **`_visible_lines` 的抽取:** 我讀 diff 時沒看出行為變化,新舊對圍欄的 toggle 邏輯等價。此外,`_visible_lines` 本身對區間的線性掃描沒有引入新的二次方工作。
- **`lumos-cli-lifecycle`、`測試假綠形態`、`guard-kill`:** 新程式沒碰 re-inject、uninstall、guard kill,判不影響。
- **`_regular_own_fd` 加 `dir_fd` 參數:** 預設值 `None` 時呼叫形式不變,既有呼叫端行為不變。

最嚴重 severity:minor,blocking 共 0 條。

我造的實驗目錄已用字面絕對路徑刪除。
