### arch-f1 S3 把 outcome/usd 塞進 canary record 的 --note 自由文字,重踩專案已淘汰的「散文塞結構化資料」舊路
severity: major
引句:「美元走 note 自由文字,不動欄位」
佐證:file: `scripts/lumos:15573`
說明:--canary-type/--probe 既有欄的 help 明講「結構化取代散文 note」,3469 行「D 前置」註解寫「原散文 note 不可重算」,4437 行獨立進度驗證器把 note 整段丟棄以隔離「散文注入」——專案已吃過虧、明文放棄的做法。S3 反向把要被 [S4] 逐筆回讀的結構化資料塞回 note,是把被取代的舊路重走一遍。

### arch-f2 S1 另開 pipeline_failures 計數,和 gap_select 既有的 unconverged 重試計數兩套並行、規則不同調
severity: minor
引句:「(不是它的錯,不降分),另在該筆累計」
佐證:file: `governance/autonomous_loop/gap_select.py:41`
說明:「gap 失敗放回/計次/何時放棄」requeue_unconverged 已是既有做法(降分+累計+滿 3 次轉 covered)。S1 另開一個不衰減、無上限收尾的 pipeline_failures,兩套計數並存規則各異,屬與既有分工略有出入。

## 對齊良好的面
- PRIOR-ART 段落點都在既有兩模組內,無另起檔案繞過。
- 死因擷取沿用 :213 既有殘文;S4 吃既有 canary 帳,兩次寫死「不建新帳本」。
- LINE 全走既有 line_notify,寫法與既有三處一致。
- 相容性 .get() 防呆與 backlog.py 現行寫法一致。
- 「不做」清單紅線清楚,沒藉機重設計收斂/放行架構。
