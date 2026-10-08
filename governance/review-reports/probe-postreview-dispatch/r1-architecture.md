severity: clean

引句:「缺可取消 runner 時 `--workers > 1` 應在模型派工前明確拒絕，預設僅開一路。」

串行派工與停止邊界：已讀，無 finding。規格以「後續工作不得進入 `run_job`」約束派工層，能避免只把 executor 改成單 worker、卻仍預先提交全部工作的假修復；現碼確實在 `main` 一次提交所有 future。file: `governance/eval/ablation_lumos_first.py:338`

CLI 拒絕邊界：已讀，無 finding。`--workers` 屬消融批次編排參數，由同一個 `main` 在模型派工前拒絕大於 1，符合既有 CLI 邊界；預設值與說明也位於同一模組。file: `governance/eval/ablation_lumos_first.py:295`

子程序例外與摘要收尾：已讀，無 finding。`subprocess.run` 現位於 `run_job`，而 summary 與退出碼由 `main` 統一收尾；規格要求把啟動例外轉成停止訊號、仍走既有 summary 路徑，沒有建立第二套結果協定。file: `governance/eval/ablation_lumos_first.py:156`；file: `governance/eval/ablation_lumos_first.py:346`

圖譜落點與模組家：已讀，無 finding。生產碼仍由 `Systems/ablation-lumos-first` 管理，測試落在既有 `scripts/test_lumos.py` 並由 `Systems/測試假綠形態` 承接；計劃的 `lands_in` 已包含兩者，`codex-harness` 則保留整體探針生產端脈絡。file: `docs/lumos-toolchain-knowledge/Systems/ablation-lumos-first.md:6`

凍結審材：已核對 SHA256 `4f968e49d3d009b04e8644d2d31244fc2ca38da9c12b821a6ac41a836ac40fd2`，100 行。

總結最嚴重 severity clean，blocking 0 條。
