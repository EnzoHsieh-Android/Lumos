### arch-f1 condensed 的未標判定沒有明文接回 collect_unjudged,有另立第二套定義的風險
severity: major
引句:「單改一處不夠,要換三態介面+兩個呼叫端(retrieval_eval.py:339/:382)的排名剔除。」
佐證:file: `governance/eval/retrieval_eval.py:221`
佐證:file: `governance/eval/refresh_labels.py:11`
說明:_labels_of docstring「未標判定禁用本函式」、refresh_labels「單一實作禁另寫」;[S1] 通篇沒一句要委派 collect_unjudged——照字面會長出第三套判準,正是既有紀律禁止的。

### arch-f2 metric_rev 是第二條「尺版本」軸,與既有棘輪比較鍵 goldset_rev 的關係沒交代
severity: major
引句:「history 列加 metric_rev;舊列凍結不重算;過渡期雙報(舊尺+新尺同印)直到下次 repin,gate 門檻在雙報期末重錨。」
佐證:file: `governance/eval/retrieval_eval.py:300`
佐證:file: `governance/eval/retrieval_eval.py:528`
說明:must_ratchet/pin_noise_ratchet 只用 goldset_rev 篩「同尺才比」;公式改變不動 goldset_rev——同 goldset_rev 不同 metric_rev 的列會被棘輪當同尺比,正是該設計要防的事故換了觸發軸。

### arch-f3 08-17 裁定被翻,spec 沒安排回頭在標註刷新_計劃留「被翻」紀錄
severity: major
引句:「真的修尺——condensed 計分為主尺方向,細節過設計審」
佐證:file: `docs/lumos-toolchain-knowledge/Projects/標註刷新_計劃.md:69`
說明:原筆記仍白紙黑字「拒;未標靠 delta 補標消滅,不靠改尺」且 08-22 複查重申「沒有推翻的新理由」;散文刻意不做非結構化 decisions,--superseded 機制掃不到——兩篇筆記對同一件事給相反權威說法,E3 類債務本案沒接上。

### arch-f4 [S2] coverage 與既有 S4 unjudged_rate 是否同源未講清
severity: minor
引句:「coverage 誠實線:每題附 top-k 已判覆蓋率」
佐證:file: `governance/eval/retrieval_eval.py:691`
說明:既有訊號已是 collect_unjudged 同源、held-only;[S2] 的每題覆蓋率是同一數字的細粒度版還是獨立計算,spec 沒交代。

## 對齊良好的面
PRIOR-ART 紀律扎實;兩個收斂點逆向準確;[S3b]/[S3c] 邊界清楚;[S4] 不推倒既有基建;decisions 四欄完整。
