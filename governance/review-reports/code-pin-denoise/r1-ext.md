1. **major** — `governance/eval/retrieval_eval.py:647`

引句:「`_rat_splits = [args.split] if args.split else ["all", "held"]`」

失敗場景：完整評測只對 `all`、`held` 建 must/pin-noise 棘輪，完全未獨立檢查 `train`。因此 train 少掉一篇必看或增加固定席噪音，只要 held 的改善抵銷後令 all 不退，整輪仍會 PASS，違反「per-split must 棘輪」；pin-noise 也有同一抵銷漏洞。

能翻紅的最小重現：history 基線設 `train.must_in_out_count=10, held=10, all=20`；本輪回報 `train=9, held=11, all=20`。呼叫完整模式後斷言 gates 含且拒絕 `must-see 不退步(train 棘輪)`；現碼不會建立此 gate。唯讀沙盒無可用 temporary directory，未能實際執行重現。

max severity: major
