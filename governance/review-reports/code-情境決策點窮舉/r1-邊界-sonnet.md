severity: major

審查結果:兩道新自檢在真型錄與 `--sg` 完整模式下都跑得過(問題 0 個)。問題出在怪輸入下的行為,和幾道守衛沒有測試把關。我在 `git clone` 出來的複本上對 `check.py` 逐道改壞再跑相關測試,取得下面的紅綠結果。複本與暫存目錄已刪。

**finding 1:「改由 範本 T<n>」路徑的三道守衛,改壞了測試仍全綠**

severity: major
blocking: 是

引句:「    if behavior_value(env["rows"][cid][9]) != f"範本 {group}":」

引句:「    return [] if _parts_in_order(env["lumos"], snip, body) else [f"片段不在範本 {group} 的「### 壞寫法:{cid}」小節程式裡"]」

`_template_route_problems` 有三道守衛:通電批次的「行為測試或正向約束=」要對得上範本、小節程式不可為空、片段要依序出現在小節程式裡。
- 真型錄「範本」列是 0 筆,新測試只用「單一識別字寫範本」這一案走進這個函式,而這一案在第一道守衛前就返回了。`_fence_body` 另外有單獨測試,但不經過這個函式。
- 最小重現:在 `configs/ast-grep/kotlin-android/check.py` 依序做下列三種改壞,每次跑 `python3.14 scripts/test_lumos.py -k kt_catalog_bad_snippets_reach_rows`,結果都是 rc 0。
  1. 拿掉 `behavior_value(...)` 那兩行。
  2. 拿掉 `if not body:` 那兩行。
  3. 把上面第二句引句的 `return` 整句換成 `return []`。
- 對照:拿掉 `<無片段>` 守衛的改壞會紅(rc 1),所以測試機制本身有效,只是沒覆蓋這條路徑。
- 同一個測試裡,`_rule_route_problems` 的 `r.get("dir") != "rules"` 與訊息前綴 `[cid]` 檢查也一樣:把整句條件換成 `if r is None:` 仍 rc 0。

**finding 2:〈API 決策點〉的多道守衛改壞後測試不紅**

severity: major
blocking: 是

引句:「        if r is None or r["retired"]:」

引句:「    return {cid for r in dt_rows if not r["retired"] for cid in re.findall(r"[A-Z]+-\d+", r["checks"])}」

以下改壞,跑 `-k kt_catalog_api_decision_points` 都是 rc 0。
- 拿掉 `or r["retired"]`:歸到停用列的 `D-n` 不再報。
- 拿掉 `not r["retired"]`:停用列的檢查被算進「被情境列引用」。
- 拿掉 `("jvm", head.group(5))`:JVM 母體的 sha256 不再核對。測試只動過 klib 那份。
- 把 `if missing_anchor or len(names) < _API_MIN_NAMES:` 的任一半拿掉:測試的「太薄」案例同時缺錨點又不到下限,兩個條件各自沒人把關。
- 拿掉「同一個名稱出現兩列」那段 `if name in seen`。
- 拿掉 jvm-only.txt 的「klib 已有,不用手列」和「要寫 名稱 | 寫法」兩道檢查。

**finding 3:`// BAD` 標法的變體讓「規則」路徑誤報或漏報**

severity: major
blocking: 是

引句:「                out.append((str(f.resolve()), nxt + 1, _norm_code(lines[nxt].split("//")[0])))」

引句:「            i = ln.find("// BAD")」

在複本的 `samples/bad/kt-map-await-deferred/` 放樣本檔,片段是 `.map { it.await() }`,跑 `bad_snippet_reach_problems`。

誤報(修法照做也過不了):
- 樣本寫 `// BAD-NEXT` 標多行語句(repo 內 `kt-oncompletion-ignores-cause`、`kt-flow-catch-empty` 已有這種標法)。程式只認下一行,片段在更後面的行,報「片段不在…標了 // BAD 的行上」。`_bad_lines` 對那種檔只回傳下一行的內容。
- 「`// BAD:說明`」之後的下一行有字串網址,例如 `val u = "http://x"; val a = xs.map {…}`。`split("//")` 把那行截在 `http:`,片段被切掉,誤報。
- 「`// BAD:說明`」在檔尾(後面沒有程式行),`nxt` 是 None,什麼都不加,片段找不到,報同一個錯。
- 下一行是 `@Foo` 這類註解行,標到註解而不是函式,同樣誤報。
- `//BAD`(沒空格)不被認,同樣誤報。

漏報:
- `ln.find("// BAD")` 是子字串比對,`// BADGE` 這種不相干註解也算標記,片段在那行就放行。

另外,`rglob("*.kt*")` 後的 `read_text(encoding="utf-8")` 沒有包 try,樣本目錄裡有非 UTF-8 檔就拋 `UnicodeDecodeError`,整支 `check.py` 噴 traceback。我用 `\xff\xfe` 的檔重現。

**finding 4:片段只有 `…` 時比對空轉成「通過」**

severity: minor
blocking: 否

引句:「    for part in [p.strip() for p in re.split(r"…|\.\.\.", _norm_code(snip)) if p.strip()]:」

`_parts_in_order(lm, "…", "anything")` 與 `_parts_in_order(lm, " ", "x")` 都回 `True`(已實測)。片段若是純 `…`、`...` 或空白,所有 `// BAD` 行或範本小節都會被當成比對成功。目前真型錄沒有這種片段,所以是潛在漏洞。

**finding 5:`check()` 裡 `why` 被 SARIF 迴圈蓋掉,錯誤訊息的原因不對**

severity: minor
blocking: 否

引句:「        problems.append(("<reach>", "要載入 scripts/lumos:" + why))」

`check()` 開頭用 `lumos, why = load_lumos()`,中間 SARIF 迴圈又 `got, why = sarif_gate_rule_ids(...)` 把 `why` 蓋掉。我把 `load_lumos` 換成回 `(None, "boom-原因")` 後跑 `check(sg)`:
- `<api>`、`<situation>` 的訊息都是 `…scripts/lumos:boom-原因`。
- `<reach>` 的訊息變成 `…scripts/lumos:lumos:boom-原因`。
- SARIF 那段若有成功,原因還會換成別的字串或空白。

修法:`<reach>` 那條改用另一個變數名,或在載入時就把訊息存起來。

**finding 6:型錄裡 `Job0`、`SupervisorJob0` 兩列的理由寫錯**

severity: minor
blocking: 否

引句:「| Job0 | 無決策 | 內部實作類別,App 不直接用 |」

這是 `skills/kotlin-idioms/checks-catalog.md` 的列(第 1303 行;`SupervisorJob0` 在第 1451 行)。klib 清單裡 `Job0` 與 `SupervisorJob0` 是 `Job()`、`SupervisorJob()` 這兩個工廠函式的 JS 名稱別名(`final fun kotlinx.coroutines/Job0(...)`),App 會直接呼叫它們。「內部實作類別」的理由是錯的,抽法也沒有像處理 `flowCombine` 那樣排除這類別名。目前對行為無影響(`Job` 與 `SupervisorJob` 兩列已覆蓋),但表上寫了不實說明。

**其餘鏡頭,判不影響**
- 型錄怪列:`| x | 無決策 |` 缺理由格 → 報「理由不准空白」。歸屬欄寫 `D-04`、`撞名D-4`、`無決策、D-4`、全形逗號,都有報。母體那行 sha 寫成大寫十六進位 → 報第一行格式不對,錯誤訊息不會誤導。
- 片段的 `\|` 與 `_CELL_RE` 一致。
- 壞字元片段(`"`、`/*`、`${`、反引號、`\0`)丟 `_reachable` 都不拋例外,回 False。
- `load_lumos` 失敗、`dt_table` 有問題、`scan` 回 None 的路徑都有處理。
- `_kt_sit_path_ok` 抽出後,條件與原本兩處完全等價:`rel` 不是測試檔且過 `_stack_changed_ok(rel, skip)`。`skip` 的預設值 `frozenset()` 與原呼叫端傳入的集合相容,不影響其他節點的行為。固定席節點這次沒附上,我只判了這一點。

severity: major
總結:max severity = major,blocking 3 條(finding 1、2、3),minor 3 條。

相關檔案:
- `/Users/enzo/harness/lumos-d4-triggers/configs/ast-grep/kotlin-android/check.py`
- `/Users/enzo/harness/lumos-d4-triggers/scripts/test_lumos.py`
- `/Users/enzo/harness/lumos-d4-triggers/scripts/lumos`
- `/Users/enzo/harness/lumos-d4-triggers/skills/kotlin-idioms/checks-catalog.md`
