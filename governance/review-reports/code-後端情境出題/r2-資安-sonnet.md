severity: minor

我只找到一條能重現的洞:規格閘與 lint 共用的解析函式裡,有一條正規式在特定輸入下會變慢到卡死,所以是 minor。這條是修補新引入的。其餘項目掃過沒有發現問題:

- **密鑰與連線字串:** 整份快照沒有金鑰、權杖或帶密碼的連線字串。`governance/eval/mcp-lab-2026-10-12/compose.yaml` 的密碼是 `<<lab-admin-password>-password>` 這種佔位字,埠只綁 127.0.0.1。
- **本機絕對路徑:** 112ad15f 新增或改動的檔裡,沒有 `/Users/...` 這類路徑。`qo-ablation-2026-10` 目錄也沒有,commit 985d8818 的遮蔽有生效。`/Users/enzo/orca/...` 只出現在 r2-snapshot.patch 夾帶的審查報告引文裡。
- **子程序:** 這兩輪之間,`scripts/scenario_probe.py` 和 `qo_ablation.py` 的 diff 只有移除 `subprocess`,沒有新增。
- **計分器的 `re.search`:** `qo_ablation.py:180` 的 `re.search` 吃的是 gold.json 裡的 regex。gold.json 是 repo 內的固定資料,不是外部輸入。

severity: minor
blocking: 否
- **誰:** 能在 repo 提交一份計劃筆記的人,例如開 PR 的貢獻者。
- **從哪裡:** 筆記的〈待決問題〉一節。
- **送什麼:** 節內放一行只有大量空白、結尾接一個非 Q 的字元,例如 `" "*40000 + "x"`。
- **拿到什麼:** `parse_pending_questions` 靠 `_PQ_LOOKS_RE` 判斷「這行像不像題目」。這條正規式的字元類 `[\s>*+\-\d.、)）|\[\]xX]*` 後面緊接 `\s*`,兩段都能吃空白,於是出現平方級回溯。規格閘、lint、`pitfalls --stage` 三處都會呼叫這個函式,所以 CI 的規格閘或 lint 會被拖到卡死(拒絕服務)。
- **重現:** 載入 112ad15f 的 `scripts/lumos`,呼叫 `m.parse_pending_questions("## 待決問題\n" + " "*N + "x\n")`。N=20000 耗時 1.88 秒,N=40000 耗時 7.8 秒;單獨對該正規式測,N=16000 為 1.24 秒。時間隨長度平方成長,100 萬字元的一行會跑數小時。
- **為什麼只列 minor:** 攻擊者必須先有提交筆記的權限,影響只是 CI 逾時,沒有資料外洩或程式執行。修法是把前導字元類裡的 `\s` 拿掉,或把 `\s*` 併進字元類。
引句:「_PQ_LOOKS_RE = re.compile(r"^[\s>*+\-\d.、)）|\[\]xX]*\s*[QＱ]\s*\d|\[(?:阻塞|不可逆)\]|\[(?:類|階段|狀態)\s*[:：]")」
file: `scripts/lumos:6921`(112ad15f 版,查證用 `git show 112ad15f:scripts/lumos`)
歸因:有證據的修復回歸
- **修前(c960f6de):** `git show c960f6de:scripts/lumos | grep -c '^_PQ_LOOKS_RE'` 輸出 0,這條正規式不存在。
- **修後(112ad15f):** 同一條指令輸出 1,正規式在第 6921 行,並用 `parse_pending_questions` 實測出上面的耗時。
- **推論:** 修前版本沒有這條正規式,所以這個問題是修補(`_PQ_LOOKS_RE` 的引入)帶進來的。

總結:最嚴重 minor;blocking 共 0 條。
