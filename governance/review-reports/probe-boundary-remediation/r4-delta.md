severity: major
# r4 全新差異席原報告

快照核對：`r4-postfix-snapshot.patch` SHA256 `945b76e6d22855514f5bd90dfcff1ff4531d66fbabfb1a26cf361978fb6a0d76`，369行，均相符。

Finding 1：缺結果檔雖會停止後續派工，整批最終仍假綠。`run_job` 只把失效狀態放進回傳文字與 `stop`；`main` 未保存這個狀態，末尾重新以磁碟掃描覆寫 `poisoned`。完全缺檔時沒有檔案可掃，因此輸出未標失效且回傳 0。

severity: major

blocking: 是。

引句：「探針退出異常、結果檔不可讀或整批失效都設停止旗標，後續不再派工。」

file: `governance/eval/ablation_lumos_first.py:191`、`governance/eval/ablation_lumos_first.py:339`、`governance/eval/ablation_lumos_first.py:344`、`governance/eval/ablation_lumos_first.py:357`。

最小重現：stub 探針 subprocess 回 `returncode=1` 且不建立 `--out` 檔，使用一題、`workers=1` 執行真 `main()`。實跑得到 `status="★探針批次失效★ rc=1"`，但 `rc=0`、`summary.skills_health_poisoned=[]`、`missing=1`；斷言 `rc == 3 and summary["skills_health_poisoned"]` 會翻紅。持久化 `results:["bad-row"]` 亦得到同樣假綠。

舊 schema 的 `skills_health_bad`、逐場 `fatal` 與新頂層 `fatal` 整檔排除：已讀，無 finding。

既有失效檔先掃描、再決定是否補跑模型：已讀，無 finding。

部分 JSON 留檔後的停批與最終 rc3：已讀，無 finding。

普通 `inconclusive` 與帶完整普通失敗列的 rc1 模型結果：已讀，無 finding。

健康檢查 fatal、歷史正常資料互讀：已讀，無 finding。

MOC 新家入口與 `verified_by` 反向連結：已讀，無 finding。

總結：最嚴重 severity major，blocking 1 條。
