severity: minor

我實際跑過極端輸入。極端輸入的效能與記憶體沒有問題,`--compare-rules` 的參數組合和帳上 `quote_rule` 的各種型別也都有妥善處理。只找到 2 條 minor。

跑過且沒問題的項目:
- **各種怪輸入**:空報告、只有閉引號、`引句:」`、CRLF、BOM、U+2028、空引句 `引句:「」`、引句寫到結尾沒閉合、`「…』` 型態混用,結果都合理。
- **規模**:5000 條標籤耗時 0.02 秒。5MB 單行引句 0.34 秒、約 53MB。5MB 全是開引號約 240MB、0.4 秒。5MB 的「」交錯尾段 1.2 秒。標籤後接大量 `*` 或空白沒有正則退化。
- **比對成本**:1000 條引句對 5MB 快照,舊判準 2.84 秒、新判準 2.86 秒,沒有比舊判準更慢。`--compare-rules` 每組跑兩版,成本約兩倍,屬預期。
- **`--compare-rules` 參數組合**:帶報告、`--spec`、`--rule` 都是 rc2 擋下。非法 `--rule` 與缺 `--spec` 也是 rc2。帳本不存在、是目錄、非 UTF-8 都是 rc2 並印訊息。帳上的壞行、非物件列、型別不對的路徑都被略過,非 UTF-8 的報告或快照都有計數。
- **帳上 `quote_rule` 型別**:`_quote_rule_of` 先判 `isinstance(v, str)`,list 這類不可雜湊的值不會炸。

1. `--compare-rules` 遇到路徑含 NUL 字元會 traceback,整個掃描中止
severity: minor
blocking: 否
引句:「return (Path(rel) if Path(rel).is_absolute() else root / rel).read_text」
file: `scripts/lumos:26698`
- 輸入:帳上某列 `report_path` 或 `snapshot_path` 是 `"a\u0000b"`(手改或寫壞的帳)。
- 路徑:`_read()` 只接 `UnicodeDecodeError` 與 `OSError`,而 `Path.read_text` 對含 NUL 的路徑丟的是 `ValueError`。
- 結果:`ValueError: embedded null byte` 一路噴到最上層,rc1,前面已算的交叉表一行都沒印。我實測是帳裡一列壞路徑就讓整次量測報廢。
- 對比:同函式對壞 JSON 行與「非字串路徑」都做了略過計數,這條漏了。
- 建議:`_read` 的兩個 except 補上 `ValueError`,併進「讀不到」。

2. 最後一條引句的尾段一路掃到檔尾,後文任何一個落單 `」` 都會把合法引句判成 stray
severity: minor
blocking: 否
引句:「nxt = items[k + 1][0] if k + 1 < len(items) else len(rtext)」
file: `scripts/lumos:25886`
- 輸入 A:`引句:「合法前綴文字至少十個字」`,後面接 `## 後記` 與 `他說「甲」』`。
- 輸入 B:`他說「結論如下。引句:「合法前綴文字至少十個字」。以上」`,也就是引句被一個外層「」包住。
- 結果:兩者都得到 `ok=False, kind=stray`。
- 原因:最後一條的 `nxt` 是 `len(rtext)`,所以引句之後整份報告剩下的文字都算它的尾段。
- 影響:這與計劃寫的「引句結束後到下一條引句前」一致,但範圍比字面寬得多。第一階段寫側是 legacy,只影響 `--compare-rules` 的誤傷統計。第二階段把寫側常數翻成新判準後,報告後文只要有一個無關的落單收尾引號,就會擋下一份合法載體。
- ⚠ 這是設計取捨,我沒有實證真實報告的落單率。建議第一條 REVISIT 量測時,把「stray 且該行之後沒有任何引句標籤」單獨計數,以判斷誤傷來源。

附帶一條小事,不另列為 finding:舊判準的格式不合列不帶 `kind`,`quote` 是固定佔位字串「(引號未閉合/開閉型態不符,無法抽取)」(`scripts/lumos:25933`)。第一階段寫側是 legacy,所以擋下事件 note 的 `cats` 會記成 `miss`,`quote=` 片段也是佔位字串,在報告被覆蓋後沒法判真抓或誤傷。這與計劃寫的「`quote=` 片段讓 REVISIT 在報告已不在時仍能判斷」有落差,但只影響第一階段 legacy 的格式不合那一類。

實驗目錄已刪除。

總結:最高等級 minor,blocking 共 0 條
