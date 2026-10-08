severity: major
根據 `/tmp/code1-r3.patch` 對照 `rw` 裡的 `scripts/lumos`,這批修正長出了第二套做法:連結正規式和分隔字表各多了一份。我只讀程式碼,沒有跑測試。

## 上一輪(r2 架構席)4 條的驗證

- **R2A1 路徑清控制字元:大致對齊。**
  - 舊違規那行改成 `{_esc_clean(p, 200)}:{n}`(`scripts/lumos:27427`)。
  - doctor 的 `shown` 也補了清洗(約 `:27275`)。
  - 殘留見下面 R3A5。
- **R2A2 比對鍵靠元組長度分形狀:已對齊。** `_ns_slot_key` 第一格改標 `"text"` 或 `"ptr"`(`:26914-26923`),`_ns_old_keys` 回三個具名桶 `{text, ptr, phys}`。`None` 鍵和元組長度分流都拿掉了。
- **R2A3 `check: slots`:沒有照鄰居收斂。** 改成同時有形狀與格子違規時標 `shape+slots`,是新長出的第三個值。見 R3A3。
- **R2A4 doctor 提醒依 `ci` 分流:這批沒動。** `:26816` 仍是 `elif not ci and gate_mode != "off" and ...`。見 R3A4。

## 三問

**① 分層與依賴方向:對齊。**
- `cont` 用傳入 dict 回填(`_ns_summary_logical`),和既有的 `sink` 寫法同形。
- `_ns_slots_old_lines` 改回傳 `(整條, 實體行)` 兩份,由 `_ns_old_keys(*old)` 接。依賴方向沒變,批次讀仍走 `_nodehome_cat_blobs`,治理帳仍走 `_gate_event_or_warn`。

**② 命名與錯誤處理:大致對齊。**
- 提醒字樣和「git 算不出就 fail-open」沿用原樣。
- 治理帳的 `check` 值有出入,見 R3A3。

**③ 第二種做法:有 2 條 major。**
- 連結正規式:`WIKILINK_RE`(`:378`)、`_NS_POINTER_ONLY_RE`(`:26293`)已有,又加了 `_NS_SLOT_LINK_RE`(`:26747`)。
- 分隔字表:`_NS_POINTER_ONLY_RE` 已有,又加了 `_NS_PTR_SEP_RE`(`:26749`)。
- 以下兩條分別細講。

## 不對齊條目

**R3A1 新增 `_NS_SLOT_LINK_RE`,與既有 `WIKILINK_RE` 幾乎同一個式子,理由不成立**
引句:「_NS_SLOT_LINK_RE = re.compile(r"\[\[[^\[\]]*\]\]")             # 連結,含別名與段落(舊行比對時從寬認)」
- 對照:`WIKILINK_RE = re.compile(r"\[\[([^\[\]]+?)\]\]")`(`scripts/lumos:378`)。
  - 兩者只差 `*` 對 `+?`,也就是新式子多認空連結 `[[]]`。
  - `WIKILINK_RE` 本來就認別名(`|`)和段落(`#`),註解說的「含別名與段落」它也做得到。
- 同一個 `_ns_slot_key` 裡,抽連結目標仍用 `WIKILINK_RE.findall(core)`(`:26922`),判斷「只放連結」卻用 `_NS_SLOT_LINK_RE`。同一條行裡有兩套「什麼叫連結」。
- 要「從寬」的對象其實是 `_NS_POINTER_ONLY_RE` 的 `[^\]|#]+`(它不認別名和段落),不是 `WIKILINK_RE`。新式子是為了繞開 `_NS_POINTER_ONLY_RE` 而生,卻沒有直接復用 `WIKILINK_RE`。
- 重現:`python3.14 -c "import re; print(re.findall(r'\[\[[^\[\]]*\]\]','x [[]] y'), re.findall(r'\[\[([^\[\]]+?)\]\]','x [[]] y'))"`。我沒執行,是讀正規式判斷的。
- 結果:空連結 `DEP:[[]]` 在 `_ns_slot_key` 會走 `ptr` 分支,`frozenset()` 為空,`_ns_is_old` 的 `o and ...` 又把空集合擋掉,行為雖然安全,但這是第二套定義造成的偶然。
severity: major
blocking: 否 — 沒造出放行錯誤的場景,但是第二種做法。

**R3A2 新增 `_NS_PTR_SEP_RE`,重抄 `_NS_POINTER_ONLY_RE` 的分隔字表,同一條流程裡出現兩套「只放連結」判定**
引句:「_NS_PTR_SEP_RE = re.compile(r"[見→,，、。;；與和及|｜\s]+")       # 判「只放連結」時連結之間准有的分隔」
- 對照:`_NS_POINTER_ONLY_RE`(`:26293`)的分隔集合是 見 → , ， 、 。 ; ； 與 和 及 | ｜,加上 `\s*`。字表逐字相同。
- 判定出現兩處,結論不同:
  - `_ns_slot_key` 用 `_NS_PTR_SEP_RE`+`_NS_SLOT_LINK_RE`,帶別名的 `[[A|別名]]` 算「只放連結」。
  - `_ns_slot_line_problems` 的 SEE 提示仍用 `_NS_POINTER_ONLY_RE.match`(`:26979`),`[[A|別名]]` 不算。
- 具體場景:新寫 `DEP:[[A|別名]]` 時,比對鍵認它是 ptr,但 `_ns_slot_line_problems` 的「改寫成 SEE:」提示不觸發,轉去走 `slot_check_keyed`。同一行在兩處被判成不同類。
- 已知的兩處用法(`:3605`、`:26344`)都沒跟著動。
- 判不準:這個差異可能是刻意的,「舊行比對從寬、新行判定從嚴」。但從寬應該用參數或帶旗標的同一個正規式表達,不是再抄一份字表。⚠
severity: major
blocking: 否 — 沒造出翻紅場景,但分隔字表現在有兩份,以後改一份會漏另一份。

**R3A3 `check` 欄位從單一字面值變成「兩處設定、三種取值」**
引句:「    kw = {"extra": dict(_ns_slot_extra(sviol), check="slots" if not (viol or errs) else "shape+slots")} if sviol else {}」
- 對照:`_ns_slot_extra`(`:27099`)已回傳 `"check": "slots"`,這行又用 `dict(..., check=...)` 覆寫。同一個欄位在兩處設定。
- 鄰居(`negation` 在 `:27411`、`tag-hints` 在 `:26717`、`old-sentence` 在 `:32261`)都是單一固定字面值,綁自己專屬的事件,沒有組合值。
- `shape+slots` 是新的取值形狀。`:7667` 的去重鍵含 `check`,它讓同時違規的 `blocked` 與只有格子違規的 `blocked` 分成兩類。
- 這是 R2A3 的改法,但沒收斂到「只在一處設定」。⚠ 我沒造出讀帳算錯的場景。
severity: minor
blocking: 否 — 只影響讀帳分類。

**R3A4 doctor 的 `--slots` 掛鉤提醒仍依 `ci` 分流,這批沒動**
引句:「        elif not ci and gate_mode != "off" and _NOTE_SHAPE_GOLIVE_MARK in txt and _SLOTS_GOLIVE_MARK not in txt:」
- 這條是 R2A4 原樣,diff 的 context 帶到它,沒改也沒在收貨紀錄標明為什麼不動。
- 對照:`_ns_negation_doctor_lines`、`_ns_tag_hints_doctor_lines` 不看 `ci`。
severity: minor
blocking: 否 — 提醒字樣的分流方式,不影響放行。

**R3A5 路徑清控制字元仍漏一處:`errs` 輸出**
引句:「            print(f"  {_esc_clean(p, 200)}:{n}  {rule} {frag}:{fix}", file=sys.stderr)    # 路徑清控制字元(r2 架構席)」
- 對照:同一函式上面兩行 `for e in errs: print(f"  {e}", file=sys.stderr)` 沒清。`errs` 的每條是 `路徑:…`,和 `viol` 同一類資料。
- 路徑清洗只補了 `viol`,同一個輸出裡仍混用兩種寫法。⚠ 我沒確認 `errs` 的路徑是否已在上游清過。
severity: minor
blocking: 否 — 輸出一致性。

不對齊共 5 條,其中 major 2 條

最高嚴重度 major,blocking 0 條
