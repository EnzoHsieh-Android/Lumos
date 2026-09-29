severity: minor

## F1 casefold 測試只覆蓋 ASCII，無法釘住完整比對鍵

severity: minor
blocking: 否
引句:「翻紅釘:比對鍵拿掉 casefold → ①②紅;git 失敗改回空清單 → ③紅;空清單也印查不到 → ④紅。」
file: `scripts/test_lumos.py:53784`
file: `scripts/lumos:28003`

1. ①②使用的 `Code-Review`、`CODE-FOO` 等名稱全是 ASCII；對這些輸入，`lower()` 與 `casefold()` 結果相同。
2. 把 `_drift_c4_dir_key` 改成 `nfc(d).lower()`，這兩項斷言仍不變，但已違反 S1 的「NFC 再 casefold」。例如 Git 名 `STRASSE` 與現存名 `Straße` 在 casefold 下同為 `strasse`，改用 lower 後不再對應。
3. 測試目前只釘住 ASCII 大小寫不敏感，沒有釘住所宣稱的完整比對鍵。
4. 未能重現：唯讀沙盒禁止建立共同規則要求的 shared clone；以上由測試輸入與比對函式靜態核對。

## F2 測試區塊標頭仍宣稱已撤回的行為

severity: minor
blocking: 否
引句:「刪除守衛不再跳過任何工具自裝檔——消費專案提交時」
file: `scripts/test_lumos.py:53515`

1. 新測試與 S5 都已改成「不跳過任何工具檔」，但整段測試的導航標頭仍寫「刪除守衛跳過工具自裝檔」。
2. 這是撤回後殘留的反向說法；搜尋該功能時會先把維護者導向已撤掉的行為。程式與新測試本身沒有同樣殘留。

## 處置核對

- delguard 從 `_delguard_is_diff_header` 到下一模組區段，在 `9cc20926` 與 `43270394` 的 SHA-256 都是 `d82f41660a9434322ed2fc76b9d771747c0794dfb79032a19bf96527e941522a`，實作與記帳已逐字回到基準。
- 程式中已沒有 `_delguard_vendored_skips`、`vendored_skipped`、`_DRIFT_C4_DIRS_MAX` 或 `_drift_c4_more_cmd` 的殘留呼叫。
- `t_delguard_scans_vendored_files_in_consumer` 有現場前置斷言，且會檢查工具檔名稱被抽取、note 不含 `vendored-skip=`；足以釘住撤回前的實作。
- `t_drift_c4_lists_all_dirs` 建立 23 個目錄並要求全部輸出，也拒絕「另有 N 個」與補充指令，已釘住上限撤回。
- casefold 只作比對鍵；回傳與列印仍取自現存目錄集合，因此新邏輯不會改印 Git 裡不存在的拼法。

## 圖譜鏡頭逐條判定

- `Systems/存量漂移守衛`：現行程式符合全部列出、以 NFC＋casefold 對應並列印現存名稱；只有 F1 的測試鑑別力不足。
- `Systems/bound-tests-gate`：未修改合約測試執行、懸空判定或退出碼；新增綁定測試名稱均存在。
- `Systems/guard-kill`：退出碼優先序與 JSON 純度路徑未改。
- `Systems/授權與歸屬`：未修改 `_VENDORED_TOOLKIT`、`_VENDORED_ALL` 或授權檔處理。
- `Systems/測試假綠形態`：刪除守衛與全部列出測試都有現場前置斷言；casefold 測試未區分 `lower` 與 `casefold`，見 F1。
- `Systems/lumos-cli-read`：搜尋的 superseded/stale 契約未改。
- `Systems/lumos-cli-lifecycle`：re-inject 與安裝生命週期路徑未改。
- `Systems/design-loop`：處置閘、計劃綁測試及收斂判定未改。

最高等級:minor