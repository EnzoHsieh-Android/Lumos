severity: major

我站攻擊者那邊試過了。新判準 `full-span-v1` 本身我繞不過去,隨機模糊測試 3 萬筆也沒有例外或誤判。能被利用的洞都在周邊的 `--compare-rules` 和 note 寫入。

沒找到突破點的幾項:
- 前綴照抄後接編造、換行補收尾引號、前文有沒閉合的開引號、引句內夾標籤(吞標籤),新判準都判不過。
- 引句後面接一對平衡的「…」或『…』,新舊判準都放行。計劃書〈工具保證的範圍〉已明寫不防,所以我不算它是新洞。
- 退版風險:`quote_rule` 缺鍵時照 legacy 判。帳上沒有逐列雜湊,刪掉這個鍵比改 sha 簡單。第二階段(常數翻成 `full-span-v1`)上線後,有帳本寫權的人刪鍵就能把新帳降回舊判準(finding 4)。

1. `--compare-rules` 對帳上路徑沒設防,壞路徑會讓指令崩潰或卡死,也會讀到 repo 外的檔
severity: major
blocking: 是
引句:「        return (Path(rel) if Path(rel).is_absolute() else root / rel).read_text(encoding="utf-8")」
file: `scripts/lumos:_quote_compare_rules 內的 _read`
- 誰、從哪、送什麼:任何能改 `docs/.canary-log.jsonl` 的人(例如 PR 帶進來的帳列),在 `report_path` 或 `snapshot_path` 填入下列值,等維護者跑 `lumos quote-check --compare-rules`。
- 含 NUL 的路徑(`"a\u0000b"`)會讓指令以 `ValueError: embedded null byte` 帶 traceback 崩潰。孤立代理字元(`"\ud800x"`)則是 `UnicodeEncodeError` 崩潰。我實際跑過。`_read` 外面只接 `OSError` 和 `UnicodeDecodeError`,這兩個都是 `ValueError` 的後代,漏接。一列壞行就讓整本帳的比較報表拿不到。
- 指向具名管線(FIFO)會永久卡死。我實測 5 秒沒返回。指向 `/dev/zero` 之類的無窮檔,`read_text` 會讀到記憶體爆掉(從程式推論,沒實跑)。
- 路徑穿越成立:`../outside.txt` 或絕對路徑都被讀進來,沒有限制在 repo 內。我實測 repo 外的檔被當快照讀取,計入「兩版都錨定」。
- 內容不會被印出來。輸出只有計數,以及舊判過新判不過清單裡的 `rp` 路徑字串。所以不是檔案內容外洩,只是能當「某檔含不含某句」的存在性探針,風險很低。
- 該有的修法:路徑解析後限制在 repo 內,只讀一般檔,`_read` 的例外改接 `(OSError, ValueError)`。

2. 擋下事件 note 把審查席可控的引句片段原樣寫進版控治理帳,終端控制字元沒過濾
severity: minor
blocking: 否
引句:「    snippet = re.sub(r"\s+", " ", first).strip()[:60] if first else "-"」
file: `scripts/lumos:_quote_block_note`
- 誰、從哪、送什麼:審查席(可能被提示注入)在被擋的引句開頭放 `\x1b[2J\x1b]0;…\x07 report=/etc/x id=deadbeef`。
- `\s+` 只壓空白類字元(含 U+2028 和 U+0085,這兩個沒漏),但 ESC、BEL 等其他控制字元原樣進 note。JSON 檔本身會跳脫,所以帳檔安全。
- 我實測 `lumos gov --full` 把 note 原樣印到終端,ESC 序列真的生效(清屏、改標題)。
- note 裡 `quote=` 排在 `report=` 前面,第一個 `report=`/`id=` 字樣是審查席放的。照 `report=(\S+)` 取第一個的讀者會被騙。`kind=` 和 `cats=` 排在前面,不受影響。
- 60 字也能放一句持久的提示注入文字進版控帳。
- 該有的修法:片段只留可印字元(例如濾掉類別 `Cc`/`Cf`),或改成 `repr` 後再截。

3. 大量短引句會讓處置閘、寫側、比較指令各自線性放大,耗時沒上限
severity: minor
blocking: 否
引句:「                kind = "both" if not passes(other_rows) else ("new-only" if write_rule == "full-span-v1" else "legacy-only")」
file: `scripts/lumos:_quote_block_note`
- 輸入:約 1.1MB 的報告含 5 萬條 10 字以上引句,快照約 1.4MB。
- 兩版判準各要 55 秒左右(實測 55.2 秒和 56.0 秒),原因是每條引句都對整份快照做兩次 `in` 搜尋。
- 新增的程式讓這個成本多了一倍:`_quote_block_note` 擋下時另用另一版判準再算一次,`--compare-rules` 每組也兩版都跑。
- 這個放大本來就有(舊判準同樣慢),所以只算 minor。「5000 個未閉合標籤 1 秒內」的測試涵蓋不到這條路徑。⚠ 報告大小在實務上有沒有上限,我沒查證。

4. 第二階段上線後,`quote_rule` 缺鍵退成 legacy,刪一個鍵就能降級
severity: minor
blocking: 否
引句:「    沒有 quote_rule 鍵 → legacy(帳上無章);值是認得的版本 → 用它;其他值一律判失敗(可能是新版程式寫的,也可能帳被手改)。」
file: `scripts/lumos:_quote_rule_of`
- 第一階段全帳都是 legacy,所以缺鍵退 legacy 沒有新風險。
- 第二階段之後,有帳本寫權的人刪掉那一列的 `quote_rule`,處置閘就改用 legacy 判,舊判準放行的編造後半就過了。帳上沒有逐列雜湊,這比改 sha 更便宜。
- 值寫成亂碼會判失敗,方向是安全的。但 `{v!r}` 不限長度,一個超大字串會原樣印在閘輸出。
- 建議第二階段另外擋「已有第二階段證據的帳列缺章」,例如用 `ts` 切點,或要求章與帳列的 sha 綁在一起。

我建的實驗目錄已刪,repo 沒動。

總結:最高等級 major,blocking 共 1 條
