severity: minor

我只查了邊界輸入,沒跑 `-k` 測試子集。四條 finding 都是 minor,沒有會做出錯誤放行、損壞資料或讓規格閘讀不到定義行的問題。實驗在 `/tmp/lumos-seat-work/` 底下的複本做,完事已刪。

## b1 人裁寫回把 CRLF 計劃整份改成 LF,「換行沿用原檔」寫了卻不會發生
severity: minor
blocking: 否
引句:「nl = "\r\n" if "\r\n" in text else "\n"」
file: `scripts/lumos:75476`(`_situation_rule_insert`),`text` 來自 `cmd_situation_rule` 的 `text = ppath.read_text(encoding="utf-8")`

1. 輸入:計劃檔本身是 CRLF。`Path.read_text` 用通用換行,讀進來的 `\r\n` 全變 `\n`。
2. 實測:`"\r\n" in p.read_text(encoding="utf-8")` 印出 `False`。所以 `nl` 永遠是 `"\n"`,「有 `\r\n` 就用 `\r\n`」那句是死碼。
3. `_situation_rule_write` 再把這份 LF 全文寫回去,整份計劃的每一行換行符都被改掉,diff 看起來是整份重寫。
4. 規格閘方面沒壞。`_note_lines` 兩種換行都切,我用 CRLF 全文直接餵 `_situation_rule_insert`,寫入時的雜湊與規格閘讀回來的雜湊一致。
5. 修法:讀檔改成 `open(..., newline="")` 或讀 bytes 再解碼。
6. 修之前,先把註解與驗收條款裡「沿用原檔」那句改成實情。

## b2 規格閘認人裁條款:先讀整本治理帳,才判門與生效日
severity: minor
blocking: 否
引句:「new = new - _spec_gate_ruled_ids(_vault_repo_root(env), rel, text)」
file: `scripts/lumos:14557`(`_expected_requirement`);推送前的呼叫端在 `scripts/lumos:17300`(`_expected_push_one`)

1. 輸入:只要計劃有至少一條新行為條款,`_spec_gate_ruled_ids` 就整本讀一次治理帳,之後才判 `door != "high"` 與生效日。
2. 本 repo 的帳是 22MB、125521 行。我量到 `_spec_gate_ruled_ids` 每次約 0.165 秒,而且帳裡一筆 situation-rule 都沒有。
3. 本 repo 有 204 份 `status: doing` 的計劃。計劃自己寫過,家節點會被上百份計劃連到,所以候選可能上百份。
4. 估算:候選有 100 到 200 份時,推送前多出約 17 到 34 秒,而且全是白讀。這是估的,我沒實際跑推送前。
5. 修法:把這段移到 `door != "high"` 與 `day < _expected_since()` 的判斷之後。或在 `_spec_gate_push_candidates` 一輪內共用一次讀帳結果。

## b3 `--clause` 帶非 UTF-8 位元組(孤立代理字元):殺傷力驗證跑完才丟 UnicodeEncodeError
severity: minor
blocking: 否
引句:「data = text.encode("utf-8")」
file: `scripts/lumos:75463`(`_situation_rule_write`),呼叫處 `cmd_situation_rule` 的 `except RuntimeError` 只接 RuntimeError

1. 輸入:`--clause $'按下\xff按鈕時,畫面應更新'`。argv 解碼後帶 `\udcff`。
2. `_situation_rule_clause_problem` 回 None,`_situation_rule_insert` 回 `S2`,都放行。
3. 我直接呼叫 `_situation_rule_write(p, new)`,抛出 `UnicodeEncodeError`。
4. `encode` 在 `try` 之前,所以沒有暫存檔殘留,計劃也沒動。
5. 但在完整流程裡,這發生在 Gradle 殺傷力驗證(可能十幾分鐘)跑完、使用者終端答 y 之後,最後落成 traceback。
6. 修法:在 `_situation_rule_clause_problem` 加 `c.encode("utf-8")` 的早期拒絕。

## b4 新條款插在最後一條定義行之後,會切斷那一條自己的縮排續行
severity: minor
blocking: 否
引句:「after = max([r["line"] for r in rows if r["line"] in in_sec] or [heads[0]])」
file: `scripts/lumos:75472`(`_situation_rule_insert`)

1. 輸入:節內最後一條是 `- [S3] 收到訊息時,系統應回應 [test:x]`,下一行是縮排續行 `  續行 第二行`。
2. 實測結果是 `- [S3] …`、`- [S4] 按下按鈕時,畫面應更新 [test:t_b]`、`  續行 第二行`。續行從 S3 底下被搬到 S4 底下。
3. 規格閘 `clause_bindings` 只看單行,所以閘的判定不變。
4. 影響:計劃正文的可讀性與歸屬錯了。
5. 修法:`after` 往後吃掉緊接的縮排續行,或遇到續行時改插在續行之後。

## 附:manifest 與圖譜鏡頭

**邊界走查,沒出問題的**
- spec 字串:`S0`、`S01`、`#S` 後空、小寫 `s1`、全形 `＃`、結尾換行、阿拉伯數字 `S٣` 都回 None。`Projects/a#b#S2` 取最後一個 `#`,`.md` 結尾會被去掉。
- 引句:全形空白被收成一個空格。9 個實字被擋、10 個通過。
- 條款編號(插入函式實測):節裡沒條款、節標題是最後一行、檔尾沒換行、條款散在別節(取全文最大號加一)都插對位置、號碼對。
- 雜湊(lens 4):我模擬「寫入時算」與「`_spec_gate_ruled_ids` 讀回」。純文字、CRLF、反引號與粗體、NFD、U+2028、`\x0b`、行首 `#` 與 `>` 都得到同一個雜湊,都認得出來。寫回的行規格閘會讀成定義行、綁得到 `--test`。
- `--old` 範圍:跨行、含特殊字元、剛好卡在段起訖行的邊界,用 `str.count` 與 `str.index`(不走正規式)都處理得對。

**manifest 2 條**
- 第 1 條(`scripts/lumos:75400`):誤報。那是 `os.open("/dev/tty")`,下一行就 `os.close(fd)`,沒有洩漏。
- 第 2 條(`scripts/lumos:75466`):誤報。那是 `os.open` 接 `os.fdopen(fd, "wb")` 放在 `with` 裡,會關。例外時的 `os.unlink` 清理也有。

**圖譜鏡頭**
- 這次沒附固定席節點,我自己也沒用 `lumos impact` 查。
- 我只用讀程式碼判斷。這份 diff 對 `_expected_requirement`、`_spec_gate_twoway_*` 的改動,只扣掉「治理帳雜湊對得上」的條款,沒帳或帳讀不到都回空集合,等於不放寬。所以對規格閘宣稱的行為不影響。
- `cmd_guard_kill` 新增的 `recipes_override` 預設 `None`,原本的兩個呼叫端路徑沒變。
- `_impact_home_map` 只在記憶體圖譜(`_texts` 不為 None)多走一條路,磁碟圖譜的鍵與行為不變。

最嚴重 severity:minor;blocking 共 0 條。
