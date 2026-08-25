1. severity: major  
blocking: 是  
判準：E2 只是依賴邊與日期條件成立時的啟發式補網，無法保證接住 header 損毀；不改會讓實作者照規格靜默略過唯一可直接觀測的壞帳本。  
引句:「header 損毀帳本跳過不報:損毀已有補網 E2 兜底」

實碼依據：`scripts/lumos:930-1004` 的 E2 必須同時具備 `valid:false`、合法 `ended`、特定 typed 連入邊及 `updated < ended`；它既不通報壞帳本，也不保證每條翻案鏈都符合這些條件。`scripts/lumos:8391` 只是 `resume` 失敗時印出「交補網 E2」，不是 doctor 對壞 header 的完整兜底。

2. severity: major  
blocking: 是  
判準：最老天數的時區、取整方式與非法或缺失 `header.ts` 均未裁定，不改會讓實作者產生依執行時刻差一天或直接例外的實作。  
引句:「計 transitions==0 的帳本數與最老天數」

例 1 要求 2026-08-04 到 2026-08-25 固定為 21 天，但實際 header 是帶時刻的 UTC timestamp；若用 `timedelta.days`，在滿 21×24 小時前會得到 20。另 `_ledger_read` 只驗 `event/root_decision_id/node`，合法 JSON 即使缺少或寫壞 `ts` 仍可成為合法 header，現有規格與例 3 都未定義如何處理。應明定以哪個時區的 calendar date 計日，以及缺失/非法 `ts` 是跳過、用檔名日期，或另行提示。

已讀無 finding：

- `warn_soft:486` 的宣稱屬實：確實印出但不增加 `issues`。
- `_ledger_read:8162` 與 `_rel_cascade_dir:8103` 的位置、主要語意屬實。
- `cmd_rel_cascade_list:8288` 確實明言不做開放／完成精確分類。
- 例 2、例 4、例 5 與現有帳本及目錄形狀沒有衝突。
- 例 3 的「壞 JSON 不 traceback」符合 `_ledger_read` 跳過壞 JSON 的既有語意；問題只在宣稱 E2 足以兜底。
- `warn_soft` 可承載三段訊息且不改 rc；具體排版仍可用 `head`、`lines`、`advice` 完成。

總結：最嚴重 severity 為 major；blocking 共 2 條。