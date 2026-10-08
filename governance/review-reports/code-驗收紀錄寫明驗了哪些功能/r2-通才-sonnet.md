severity: minor

## F1 多掛提醒的改法行被 _esc_clean 截斷時,引號只剩一半、「或把它補進」後半句消失
severity: minor
blocking: 否
引句:「改法:lumos remove {_drift_sh(sys_rel[:-3])} verified_by {_drift_sh(a)}」
file: `scripts/lumos:10643`(_esc_clean 超過 limit 就 out[:limit] + "…");`scripts/lumos:3664`(_DOCTOR_LINE_MAX = 300)
1. 輸入:Verification 檔名 140 字(Verification/LLL…L.md),system_refs 只列 Systems/A;Systems/B 的 verified_by 掛 `[[Verification/LLL…L]]`。
2. 走到:sr_extra 那一行字串先組好,整句再 _esc_clean(…, 300)。實測該行 309 字,被切在第二個參數中間,輸出尾端是 `verified_by '[[Verification/LLLL…`,單引號沒關,「,或把它補進那份的 system_refs」整段被吃掉。
3. 後果:照貼會卡在 shell 的續行提示(引號未閉合),或把後面接著貼的下一行吞進參數。這正是這輪 fix ① 想擋的「照貼出事」,只是換了觸發條件。長度要路徑加兩份 vrel 加 a 超過 300 才會中,中文檔名短、實際少見,所以 minor。
4. 修法:不要對整句截斷,改成只對 sys_rel、a 各自截斷前先判長度,超長就不印可照貼的指令、改印「檔名太長,請手動 lumos remove」;或把 limit 抬到足夠大。
5. 測試缺口:新案例只測空白檔名與 $(…),沒測超長;且 ② 只看參數個數 4,沒比對第 4 個參數是否等於登記原字面,截斷這類退化抓不到。

## 看過沒問題(不算 finding)
- `_drift_sh` 對 `[[Verification/V|x]]`:含 `[`、`|`,不符 `[\w./@%+=:,-]+`,走 shlex.quote 變單引號;remove 以 link_target 比對(`_cmd_remove_locked` 的 gone 與 edit_fm_remove),別名與 `#段` 都會被去掉再比,照貼後能命中。純量 verified_by(as_list 回單一字串)同路徑,沒問題。
- warn(cap=…):不帶 cap 時 shown 等於 list(lines),`len(lines) > len(shown)` 恆假,行為不變;空清單 shown 為空、「另 N 項」不印;問題數仍是 len(lines),與舊的「補差額」算法等值。呼叫端皆傳 list(原本 `issues += len(lines)` 就不支援生成器),不是新問題。
- 孤兒推薦:`_cap = len(sug)` 只在宣告且(因前面已 continue 掉「全寫壞」)至少有一個合格項時才成立,sug 不會是空;vt 為 None(stale/fail/superseded)時 `_suggest_systems_for_orphan` 內部 `vt is not None` 為假,會再算一次但結果仍是 None,落回舊流程,正確。同分排序改為 sorted(路徑),測試用 PYTHONHASHSEED 四種種子加五個同長 stem,舊寫法會翻紅,不空轉。
- stale 清單:只改 bare 模式的篩選;--legacy 與一般輸出把 `[stale]` 寫死,對 `Stale` 顯示正常;--candidate 與 --match 模式本來就不篩 status,只顯示原值,不受影響。程式其他處 `status ... in ("stale","superseded")` 仍分大小寫,屬既有設計(lint 提交時擋非小寫),不在本輪範圍。
- 已在 clone 跑 `-k doctor_check3`(25 過)、`-k orphan_suggest`、`-k case_insensitive`,全綠。
- 圖譜鏡頭:派工尾端沒附固定席筆記,不逐條答。

## 觀察(不標嚴重度,供作者取捨)
- 濾掉 `""`、`null`、`~`、`#…` 後,`system_refs: ["[[Systems/A]]", ""]` 或再多一項 `#Systems/B` 實測不再報任何壞項(3/4 只剩「Systems/A.md 漏: V」)。單獨出現時仍歸「讀不出任何一項」,新案例有釘;混在好項裡被靜默丟掉的情形沒有測試釘。屬設計取捨,我沒有找到具體會漏驗的功能,所以不標 finding。

最高等級:minor,blocking 共 0 條
