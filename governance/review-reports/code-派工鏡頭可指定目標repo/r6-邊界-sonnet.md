severity: minor

邊界與輸入(修補鏡頭)第六輪。我先在複本上跑了 `_lens_author_name_show` 與掛鉤 `_spec_name_show` 的邊界比對,再對 `lumos` 與掛鉤做破壞測試,最後用真的 `dispatch-lens` 跑了一個含惡意名字的 repo。正文沒有發現現行會裸印、會逃出框的路徑。下面三條都是跳脫規則的小缺口或測試守衛的洞,都不擋。

我讀了 40 組邊界字串。兩邊輸出完全相同,沒有任何分岔:NEL、U+2028、U+2029、變體選擇符、ZWJ 組合字元、孤立代理、BOM、DEL、tab、框線、全形反引號、`\u2039\u2039`、反斜線開頭的 `\u2039` 等。

severity: minor
blocking: 否 — 現行輸出沒有裸印或逃出框,只是跳脫格式有歧義
引句:「f"\\u{ord(c):04x}" if (c in SPEC_NAME_ESC_CHARS or unicodedata.category(c) in SPEC_NAME_ESC_CATS) else c for c in s[:limit])」
問題:超出基本平面的字元(碼位 5 位十六進位)跳脫成 `\ue0041` 這種 5 碼寫法,規格寫的是 `\uXXXX`(4 碼),讀的人與審查席分不出它跟「U+E004 加字元 1」。`lumos` 的 `_kill_esc` 同寫法(同一個格式字串),掛鉤抄了同一份。
具體失敗情境:節點名 `"\U000E0041"`(標籤字元)與 `"\ue004" + "1"` 輸入不同,但兩者都印成 `‹\ue0041›`。我在複本上實測 `a == b` 為 True。
另一個缺口:變體選擇符補充區(U+E0100,類別 Mn)、U+FE0F、U+034F、U+17B4、U+180B(都是 Mn),以及 U+3164(Lo)、U+2800(So)、U+115F(Lo),全部不跳脫、肉眼不可見。實測 `‹a󠄀b›` 看起來等於 `‹ab›`。名字長度上限 300,可以夾帶約 300 個隱形碼位的資料。名字只由 U+3164 組成時印成看起來是空的 `‹ㅤ›`,不是 `(空名字)`。
佐證:``file: `scripts/lumos:_kill_esc`、`scripts/hooks/claude/dispatch-lens-hook.py:_spec_name_show` ``

severity: minor
blocking: 否 — 現行程式沒有漏印,是守衛的覆蓋洞,改壞也不會紅
引句:「守的是行為(t_dispatch_lens_spec_author_names_e2e_sentinels 每個輸出點」
問題:註解宣稱每個輸出點各放一個哨兵,實際沒涵蓋全部。我把下列輸出點各自改成裸印後,跑 `-k e2e_sentinels`,兩支哨兵測試都維持全綠:
- 「超預算沒算」那段,兩個分支各改一次,都沒紅。
- 「太泛不列」在第一個分支(找得到程式檔但沒牽到任何節點)改成裸印,沒紅。
- 「(超出上限,只列名)」那行(`it['rel']` 改裸印),沒紅。
- `_arch_target_text` 裡「…另有 N 條,見 節點」改裸印,沒紅。
- 同函式「節點太多,規則沒貼」那行改裸印,沒紅。
- 同函式「宣告的節點讀不到規則…照鄰居審:檔名」那行改裸印,沒紅。
- 其餘 8 個改壞(計劃來源行、只在提交裡的節點、只在提交裡的檔、牽連檔、節點路徑行、第二分支的太泛不列、目標架構節點名、目標架構框)都有紅,哨兵本身可信。
- 哨兵正規式只要同一行有未配對的 ‹ 與 ›,夾在中間的裸印就會被當成「在標記裡」。目前固定說明文字沒有這種結構,所以只記為風險。
- `skipped_files` 那行不是只在預算用完時才會出現。我的探針 repo 沒設定 impact,程式檔就被歸進「超預算沒算」,同一支檔同時出現在「找得到」與「超預算沒算」。所以這個分支很容易走到,不是冷門路徑。
具體失敗情境:有人把第二個分支的 `skipped_files` 改成 `', '.join(skipped_files)`,計劃檔名帶指令句就裸印進派工詞,而守衛仍綠。
佐證:``file: `scripts/test_lumos.py:_lr5_sentinel_repo`、`scripts/lumos:cmd_dispatch_lens_spec` ``

severity: minor
blocking: 否 — 現行兩邊實作一致,只是樣本沒涵蓋會分岔的類別
引句:「SPEC_NAME_ESC_CATS = frozenset(("Cc", "Cf", "Zl", "Zp", "Cs", "Co", "Cn"))」
問題:20 筆樣本覆蓋了 Cc、Cf、Co、Cn、標記、反斜線、框線、反引號、80/81、300/301、空與純空白。但沒有 Zl/Zp(U+2028/2029)、Cs(孤立代理)、NEL、5 碼碼位。我在掛鉤複本把 `Zl`、`Zp`、`Cs` 三類拿掉,跑 `-k hook_name_show`,測試仍綠。只拿掉 `Cs` 也綠。拿掉 `strip()` 與把截斷改成 `limit+1` 則有紅。
具體失敗情境:掛鉤那份 `SPEC_NAME_ESC_CATS` 日後漂移,漏掉行分隔或代理類,兩邊比對測試抓不到。`lumos` 端共用 `_PATH_SPECIAL_CATS`,另有守衛,所以風險集中在掛鉤這份獨立抄本。
佐證:``file: `scripts/hooks/claude/dispatch-lens-hook.py:SPEC_NAME_ESC_CATS` ``

已讀,無 finding:
- 名字本身含 ‹ ›:兩邊都轉成 `\u2039` 與 `\u203a`,不能撐破標記。
- 反斜線開頭的 `\u2039` 字串:轉成 `\u005cu2039`,看得出是字面反斜線,不會被當成跳脫序列。
- 框線字元:名字含 5 個以上 `─` 時全數轉成 `\u2500`,`_frame_injected` 不會拆掉那一行。
- 換行與 U+2028:名字進得去 `dispatch-lens`,輸出都轉成 `\u000a` 與 `\u2028`,不會變成框內新的一行。
- 截斷:`s[:limit]` 以碼位計,跳脫在截斷之後做,不可能切在 `\uXXXX` 中間。切在 ZWJ 或組合字元之後只會留下孤立標記,ZWJ 本身會跳脫。實測上限 300 的最壞輸出約 1.8K 字。
- 總量上限 `_lens_spec_cap_lines`:單行超長時截在行內,可能留下沒收尾的 ‹,但仍在框內,不影響安全。
- 只列名字用的 `_vault_node_check` 放寬改成只看路徑安全:換行與 NUL 有擋。
- 真的 `dispatch-lens` 探針:名字含 ‹›、`\u2039`、U+2028、標籤字元、BiDi 覆寫、私用區、100 字長名、`─────` 開頭,節點列、落點、計劃連結行全都包在標記裡。
- 掛鉤四種說明行(讀不到、逾時、鎖狀態未知、範圍算不出)的 `what` 欄位都過 `_spec_name_show` 並加框。
- 對掛鉤複本把 `limit` 改成 `limit+1` 或拿掉 `strip()`:測試會紅。

最高等級 minor,blocking 0 條。
