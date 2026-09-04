preflight-4: ran

# r1 收貨紀錄(code-codex-d6,standard)

## 前掃
- 代碼迴圈無四類前掃;patch=scripts/lumos(自訂席 TOML 寫/收)+測試+skill 三處。

## 外家否決(Codex)6 條(1 major 5 minor;引句 6/6、行號 6/6)
- #1 agents 是檔案 mkdir 炸 HIT:折入 `skipped-not-dir` 態+訊息;紅測 d6(agents 是檔案)。
- #2 測試只搜欄名 HIT:折入 tomllib.loads 精確比四欄。
- #3–#6 「0.153+」開放版本宣稱 HIT:程式訊息+skill 三處改「0.153.2 實測選得中、0.144.1 忽略」。
## 架構對齊 6 條(2 major 4 minor)
- major① enforcement 沒對應列 HIT:折入 `codex-agent` 列(active/degraded 外方檔/inactive/unknown 不適用),列數測試 21→22、unknown 10→11。major② 三支 skill 對「框架在 TOML 還是派工詞」互相矛盾+引用停 d5 HIT:折入 統一「框架單源=TOML 的 developer_instructions,派工詞只給審材與鏡頭;舊版選不中時派工詞自帶框架」、引用改 d4/d6。
- minor:docstring 補④⑤步、teardown 步驟註解編號;三態改 created/unchanged/skipped-*(對齊 reinject 詞彙);第三種標記機制加註解說明 TOML 只能用行註解(不是另立做法)。
## 單reviewer 3 條(1 major 2 minor;引句/行號機驗見上)
- F1=外家 #1(已折)。F2 測試改 PATH 那行零鑑別力 HIT:刪掉。F3 merge-failed 時 hook 檔已 copy 但 TOML 不寫 HIT:刻意(設定檔壞=整側不算裝好),補註解。
