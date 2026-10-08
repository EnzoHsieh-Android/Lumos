severity: minor

F1  
severity: minor  
blocking: 否  
引句:「缺可取消 runner 時 `--workers > 1` 應在模型派工前明確拒絕，預設僅開一路。」  
`--workers` 的合法範圍沒有完整定義。照字面只拒絕大於 1，會讓 0 與負數通過；目前 executor 會對非正值拋 `ValueError`，若改成直接串行迴圈則可能反而忽略無效值繼續執行。S9 應把 live 派工的唯一合法值明訂為 `--workers == 1`，並補 0、負數的 parser 反例。  
file: `governance/eval/ablation_lumos_first.py:299`  
file: `governance/eval/ablation_lumos_first.py:339`

F2  
severity: minor  
blocking: 否  
引句:「缺可取消 runner 時 `--workers > 1` 應在模型派工前明確拒絕，預設僅開一路。」  
S9 沒裁定 `--merge-only --workers 2` 的相容語意。現行 `--merge-only` 不派模型，若用 argparse 全域 `choices=(1,)` 實作會讓既有純合併命令無必要地變成 rc2；若只在 live 路徑檢查則可保持相容。計劃應明寫「僅非 merge-only 時 workers 必須等於 1」，或明示這是刻意的 CLI 破壞性變更。  
file: `governance/eval/ablation_lumos_first.py:308`  
file: `governance/eval/ablation_lumos_first.py:326`

子程序例外：已讀，無 finding。S8 正確區分現行可能發生的 `OSError` 與尚未設定 outer timeout、僅作未來防回歸的 `TimeoutExpired`，且要求停止、summary 與 rc3 三項結果。  
file: `governance/eval/ablation_lumos_first.py:174`

派工停止語意：已讀，無 finding。S9 的「不得進入 `run_job`」足以排除只靠函式入口 stop check、仍把所有 futures 預先提交的舊做法。  
file: `governance/eval/ablation_lumos_first.py:156`  
file: `governance/eval/ablation_lumos_first.py:340`

新舊輸出相容：已讀，無 finding。S8/S9 沒改結果 JSON schema，既有舊檔辨識及新版健康欄位驗證邊界仍可維持。  
file: `governance/eval/ablation_lumos_first.py:77`  
file: `governance/eval/ablation_lumos_first.py:181`

既有約束：已讀，無 finding。零新增相依、第四輪舊判定保留、真模型執行前先補邊界等限制均未被 S8/S9 推翻。

總結：最高 severity minor，blocking 0 條。
