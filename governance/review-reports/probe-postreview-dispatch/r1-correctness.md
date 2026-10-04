severity: clean

引句:「後續工作不得進入 `run_job`；缺可取消 runner 時 `--workers > 1` 應在模型派工前明確拒絕」

S8 已讀，無 finding。條款同時約束停止後續題、產出機器可辨識的失效 summary、退出碼 3；命名測試也逐一注入 `FileNotFoundError` 與 `TimeoutExpired`。現碼會讓例外由 future 冒出，兩種注入都翻紅，證明反例能抓到摘要缺失與下一題仍啟動：file: `governance/eval/ablation_lumos_first.py:177`、file: `scripts/test_lumos.py:37661`。

S9 已讀，無 finding。條款明定後續工作不得進入 `run_job`，因此不能只依賴 `run_job` 開頭檢查 stop；同時要求 `--workers > 1` 在模型派工前拒絕。現碼預先提交全部 futures，兩條指定斷言均翻紅，符合先紅基線：file: `governance/eval/ablation_lumos_first.py:299`、file: `governance/eval/ablation_lumos_first.py:338`、file: `scripts/test_lumos.py:37693`。

回退、PRIOR-ART、RETIRE-IF 與相關 Issue 已讀，無 finding。Issue 對啟動例外、已在途工作及半檔的界線與 S8/S9 一致：file: `docs/lumos-toolchain-knowledge/Issues/探針批次停止後的剩餘工作與落檔邊界.md:20`。

總結最嚴重 severity: clean；blocking: 0。
