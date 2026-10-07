新增 helper 接入核對通過，無新增矛盾或缺口。

- `--check-helper NAME` 明確選用固定第二個位置參數作條件；預設不猜 helper 語義，報告保存選項，與手冊一致。
- 實跑 CLI 21 案例全過；新案例證明預設不辨識 `check`、明示後辨識自比並留下選项。
- `lumos-check-helper.json` 保存 1779 個宣告、1770 個具已辨識斷言、70 個 candidate。文件明确未逐條人工裁決、不據此阻擋推送，未混算先前三個已核對項目。
- 四份文件檢查 log 均保存通過；語言數措辭與獨立 `REVISIT:` 已修。
- 最終 faults 兩案均 detected；最終 corpus 仍為 22 個支援規則符合、6 個未分析，`complete=false`、`supported_checks_match=true`。它們與 helper 報告均绑定当前 scanner SHA。

仍可從圖譜清楚還原：S5 Agent 两臂效果待實驗，跨語言僅固定語法樣本，完整框架與真實 app 未據此宣告支援。唯讀，未改檔。
