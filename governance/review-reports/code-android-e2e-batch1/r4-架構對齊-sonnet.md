severity: minor

審查範圍:只看 `r4-repair.patch`。我另外 grep 了 `scripts/lumos` 裡所有處理孤立代理字元的寫法,獨立判斷。

## 1. 分層與依賴方向

一致,沒有跨層。

- 新函式 `_e2e_fix_surrogates` 放在 `scripts/lumos:40566`,緊接在唯一的呼叫者 `_e2e_load_json`(`scripts/lumos:40552`)之後。
- 它只做純字串與容器遞迴,不呼叫任何其他函式,也不碰 I/O。
- 唯一呼叫點是 `scripts/lumos:40563`,走 `scrub=False` 那條分支。
- 這跟鄰居 `_macrobench_stab_load`(`scripts/lumos:39894`)加 `_macrobench_stab_scrub`(`scripts/lumos:39910`)的分層一樣:載入函式先用 `_events_depth_ok` 限深,再交給遞迴的清洗函式。「函式定義在呼叫者之後」的排列也相同。
- 其餘改動是說明文字、`_lumos_config_at_ref` 的 docstring、shell 腳本的註解和測試,沒有新的依賴方向。

## 2. 命名與錯誤處理

大致一致,有一個小差異(見 A1)。

- 命名:鄰居是 `_macrobench_stab_scrub`,新的叫 `_e2e_fix_surrogates`。前綴照 `_e2e_` 家族,動詞 `fix` 比 `scrub` 精確,因為它只換孤立代理字元。可接受。
- 錯誤處理:跟鄰居相同,沒有 try/except。依賴「呼叫前已限深」的 docstring 說明(`呼叫前已限深`),與 `scripts/lumos:39911` 同樣的契約。
- 遞迴形狀(str、list、dict 的 key 與 value 都處理、其餘原樣)與 `_macrobench_stab_scrub` 逐行對應。

## 3. 第二種做法

專案裡沒有現成的「只把孤立代理字元換掉、其他不動」的遞迴函式,所以這次不算寫了第二支同功能函式。我逐一確認過:

- `_esc_clean`(`scripts/lumos:19331`)會把 C0、C1 控制字元和雙向控制字元一起換成空格,連換行和 tab 都被清掉。這正是修補要避免的行為(要保留人寫的放行理由裡的換行和 tab),所以不能直接用。
- `_SECINV_SURROGATE_RE`(`scripts/lumos:7193`)與 `_secinv_is_text`(`scripts/lumos:7199`)只做偵測,不做替換。
- `scripts/lumos:21785`、`scripts/lumos:51132` 等處是偵測並拒絕;`surrogateescape` 和 `surrogatepass` 系列是編碼層處理。
- 我對照的 `_e2e_fix_surrogates` 在 diff 的 `+` 行(`scripts/lumos:40566`),不是舊有函式,所以沒有拿它跟自己比。

不過有兩處重複,列為 A1。

## A1 孤立代理字元的正規式與遞迴骨架各抄了一份
severity: minor
blocking: 否
引句:「        return re.sub("[\ud800-\udfff]", "\ufffd", v)」
- 同一個字元類 `"[\ud800-\udfff]"` 已經在 `scripts/lumos:7193` 定義成模組層常數 `_SECINV_SURROGATE_RE`,新碼在函式內又內嵌一份字面值。
- 遞迴骨架與 `_macrobench_stab_scrub`(`scripts/lumos:39910`)除了葉節點(`_esc_clean` 與 `re.sub`)之外完全相同,而且是第二份獨立的遞迴實作。
- 這屬於「結構對、細節沒有共用既有定義」,所以判 minor。它沒有引入新的行為(沒有現成函式做同一件事),所以不是 major。

不對齊共 1 條,其中 major 0 條
