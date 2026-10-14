severity: major

這輪的修補把「看不見的字元」堵得很完整:零寬字元、組合記號、控制字元、變體選擇符、盲文空白都實測有被刪掉,全形英數也會折回來。但我找到一條一步、非刻意的逃逸:危險詞只要不是單一空格就比不到。另有兩條較輕的。

**實驗環境:** 用 `importlib` 載入 `/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos`(只讀),直接呼叫 `_door_keyword_hits` 與 `_door_judge`。-std 的範本在 `git clone` 出來的實驗 repo 裡用 `loop next` 看,切到 `2b3283c9`。腳本放在 `cr-sgn10-資安/` 底下(`h.py`、`h2.py`、`h3.py`、`h4.py`、`h5.py`)。實驗 repo 已刪,沒有在 spec-gate-nondo 寫任何帳。

## Finding 1

severity: major
blocking: 是 — 一般書寫習慣(兩個空格、tab、硬換行)就讓多字危險詞逃過門掃,計劃判成風險低而免走設計審,屬於「一步、非刻意」的路。
引句:「return _strip_zero_width(unicodedata.normalize("NFKC", _strip_zero_width(ln)))」

**原因:** 多字詞的規則寫死單一空格,例如 `DROP TABLE`、`DELETE FROM`、`anchor verify`、`pre-push hook`、`LINE 推送`。`_door_scan_text` 只刪看不見的字元,並刻意保留空白字元(tab、全形空白、換行類)。NFKC 只會把 NBSP 和 U+3000 折成單一空格。連續兩個空格、tab、硬換行都折不成單一空格。

**攻擊步驟(輸入到結果):**
- 先用 `h3.py` 對 `_door_keyword_hits` 逐一試。`DELETE  FROM t`(兩個空格)、`DROP  TABLE x`、`DROP<tab>TABLE x`、`anchor<tab>verify`、`pre-push  hook`、`LINE  推送`、`收斂<U+3000>判準`,結果全是 `[]`,沒命中。
- 對照組:`DROP<NBSP>TABLE` 和 `pre-push<U+3000>hook` 因為 NFKC 折成單一空格,有命中。
- 再用 `h4.py` 整個走 `_door_judge`(四類「已排除」各一行齊全):
  - `執行 DELETE FROM orders;` 判成 `high`,訊號是「DELETE FROM」(第 3 行,不可逆)。
  - `執行 DELETE  FROM orders;` 判成 `low`,訊號 `[]`。
  - `執行 DROP<tab>TABLE orders;` 判成 `low`,訊號 `[]`。
  - `收斂判準改寫,並關掉 pre-push  hook` 判成 `high`,但只靠「收斂判準」這一詞。換成只有 `pre-push  hook` 的句子就是 low。

**修法建議:** 在 `_door_scan_text` 的最後做 `re.sub(r"\s+", " ", ...)`,把空白壓成單一空格。這不影響「pay ment」這個已承認的天花板。計劃〈實務隱患〉只寫了「pay ment」,沒寫這一類。

file: `scripts/lumos:8166`、`scripts/lumos:7995`(`PITFALL_CLASSES` 的詞表在 `scripts/lumos:29359`)

## Finding 2

severity: minor
blocking: 否 — 這是整行逐行掃的結構限制,只有中文被編輯器硬換行切在詞中間才會碰到,不是 r9 修補的退步。
引句:「for no, ln in enumerate(text.splitlines(), 1):」

**攻擊步驟:** 這句引句抄自 `scripts/lumos` 的 `_door_keyword_hits`,patch 裡找不到逐字原句。`h4.py` 輸入 `先退\n款再說`,`_door_judge` 判成 `low`,訊號 `[]`。`_door_keyword_hits` 一次只看一行,所以換行切開的中文詞比不到。

**同族寫法:** Markdown 語法拆詞 `退**款**`、`pay**ment**`、`退<!-- -->款`、`[退](x)款`、`退\`x\`款`、`退<b></b>款` 都沒命中(`h.py`)。這些要刻意才寫得出來,屬於範圍外的刻意拆詞。硬換行在中文稿較自然,但本庫的筆記都是一段一行。建議至少在計劃〈實務隱患〉寫明這個天花板。

## Finding 3

severity: minor
blocking: 否 — 單次輸出只多 12 字,而且只出現在風險低的 PASS 行。這不是 r9 新增,但屬於「訊息帶出計劃文字」。
引句:「print("[spec-gate] 計劃風險: 低(硬訊號都沒命中;四類已排除:" + "、".join(f"{k}={v[:12]}" for k, v in judged["exclusions"].items()) + ")")」

**攻擊步驟:** 用 `h2.py` 在「已排除:金流:」那行放 ESC 序列(`\x1b[2J`)。`_spec_gate_print_door` 輸出裡 ESC 原樣印出(`cat -v` 顯示 `^[[2J`),沒過 `_esc_clean`,也沒標明是計劃文字。

**對照:** 推送前擋下訊息已改成走 `_esc_clean` 並標明計劃文字。這一處漏改。

file: `scripts/lumos:8404-8405`

## 已讀,無 finding

- **看不見字元的判準(`_is_invisible` 與 `_door_scan_text`):**
  - 「先刪、NFKC、再刪」的順序有效。`pa\u0301yment` 命中,`ｐａｙｍｅｎｔ`、`ⓟⓐⓨⓜⓔⓝⓣ`、tag 字元、軟連字號、`\x08` 都命中。
  - `pay\x1cment` 和 `pay\u2028ment` 沒命中,是計劃已承認的「空白字元不刪」天花板。
- **效能:** 1MB 單行約 0.65 秒,1MB 十七萬行約 1.0 秒,1MB 零寬字元約 0.1 秒,沒有暴增。
- **-std 形狀檢查 `_nogo_full_review_shape`:**
  - 按 `loop next ... --tier standard` 印的範本記帳,`--round` 和 `--tier standard` 都在 `record_cmd` 裡,沒有一步誤記的路。
  - 沒帶 `--tier` 時,`loop next` 對全新編號直接擋下,要求指定分級。
  - 記成 light、缺輪次、缺分級,形狀檢查都會擋。
  - 任一筆缺輪次或分級不是 standard/high 就擋。
  - 帶 tier 的列互相一致時才放行,混著沒帶 tier 的列不會誤過,因為每筆都必須有輪次。
- **推送前擋下訊息(出口 (b) 的處置閘原話):** 整段標明是計劃文字、不是給你的指示,並過 `_esc_clean`。檔名 `prel` 沒標明,但那是作者自己選的路徑,不算新增洞。
- **出口 (a) 讀帳時跳過壞行:** 已寫明與 `loop status --light` 同一接法。要先有一筆損毀的 major 才會出事,需要帳本損壞,屬於天花板。我沒另外實測 (a) 在帳尾壞行時是否放行。

最高等級 major,blocking 1 條。
