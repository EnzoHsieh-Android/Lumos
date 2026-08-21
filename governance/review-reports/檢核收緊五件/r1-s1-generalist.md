# r1 對抗審查 — s1-generalist

範圍:全文件掃(未定義詞/內部矛盾/未言明假設/不可實作缺口/證據撐不住的主張),不重報 pre-flight 已修項目(design/high 誤擋、38 處數字、downgraded 失敗條件、--findings-doc 驗證、雙入口範本、check-a 落帳測試)。

---

## Finding 1(major)— S3 外家 fail-closed 判準比 `_TIER_ROSTER` 自家合約還鬆,「≥1 席」漏掉第二席

引句：「最後 K 輪(K=2)內至少一輪有 ≥1 席 family=external」

**問題**:`code/high` 的編制表其實有**兩個**獨立的 external `required-fail-closed` 席位——「外家finder」與「外家否決」(`scripts/lumos:4638-4639`):
```
_rseat("外家finder", "external", True, "required-fail-closed"),
_rseat("外家否決", "external", False, "required-fail-closed"),
```
既有 `_roster_observe` 對帳邏輯本身就是拿「實派 external 數」與「應派 external 數(= 2)」比,不是「有沒有 external」(`scripts/lumos:4727-4728,4744`):
```
req_e = [s for s in seats if s["requirement"] in ("required", "required-fail-closed") and s["family"] == "external"]
...
if len(exts) < len(req_e):
    fc = any(s["requirement"] == "required-fail-closed" for s in req_e)
```
S3 把判準寫成「該輪 ≥1 席 external」就算過,等於只驗到「外家finder」或「外家否決」其中一席在場即可放行,另一席可以永遠缺席而不觸發 FAIL。這直接比現行(僅供轉述、未硬擋的)對帳邏輯還寬——把「轉述」升級成「執行」時,執行的合約反而縮水了,而編制表本身兩席都標 `required-fail-closed`,語意是兩席都不可少。

**file:line 證據**:`scripts/lumos:4636-4639`(`_TIER_ROSTER[("code","high")]` 的兩個 external 席)、`scripts/lumos:4727-4728`(`req_e` 計算)、`scripts/lumos:4744`(既有數量比較邏輯 `len(exts) < len(req_e)`)。

**正確的 spec 應該說什麼**:判準應與既有 `req_e`/`exts` 對帳口徑一致——「最後 K 輪內至少一輪滿足 `外派 external 席數 ≥ 應派(=2)`」,或明確論證只需 1 席即可(finder 與否決可否互相代理?),並在文中解釋為何與既有 `_roster_observe` 的計數口徑不同。目前寫法留下一個可被字面實作、且會產生「合取通過但否決席其實從未出現」這種弱化結果的缺口。

---

## Finding 2(major)— `ratchet_ack` 是純量欄位,無法同時 ack 同一節點的多個閘

引句：「節點 frontmatter `ratchet_ack: <gate>@<date>`(走 `lumos set`,白名單加一鍵)」

**問題**:S2 的升級判準是鍵在 **(gate, node)** 這個複合鍵上的(「同一 (gate, node) 在 ≥20 個不同 commit 出現」)。但逃生門用的是 `lumos set` 走 `SCALAR_KEYS` 白名單(`scripts/lumos:7039`)——純量,一個節點只能有一個值,不是 list:
```
SCALAR_KEYS = {"status", "updated", "created", "type", "self_audit", "signed_off", "regen", "pitfall_ask", "pitfall_source"}
```
`cmd_set`(`scripts/lumos:7299-7321`)寫入時是整段覆蓋 `key` 的值,沒有「累加」語意。如果同一節點同時被 `check-s`(自足性審計)與 `check-r`(可逆性)兩道閘都念到 ≥20 commit(這完全可能——它們掃的是同一批 `type: system` 節點),使用者對 `check-s` 先 `lumos set ratchet_ack check-s@2026-08-21`,之後想再 ack `check-r`,執行 `lumos set ratchet_ack check-r@2026-08-21` 會**覆蓋**掉前一筆——`check-s` 的 ack 消失,30 天窗口失效,棘輪會在下次 doctor --ci 對 `check-s` 重新升級,即便使用者確實已經明示處理過。這是「實作時完全照字面做,得到錯的閘判定」的典型 major。

**file:line 證據**:`scripts/lumos:7039`(`SCALAR_KEYS` 定義,純量非 list)、`scripts/lumos:7299-7321`(`cmd_set` 單值覆蓋寫入邏輯)。

**正確的 spec 應該說什麼**:要嘛把 `ratchet_ack` 設計成可重複的 list 欄位(走 `lumos append`,不是 `lumos set`/`SCALAR_KEYS`),要嘛明確承認「一次只能 ack 一個 gate,同節點多閘要靠……(某種串接語法,如 `ratchet_ack: check-s@2026-08-21;check-r@2026-08-22`)」並定義棘輪讀端怎麼 parse 這個複合值。目前寫法對「同節點多閘同時被念」這個(判準本身就允許發生的)情況沒有定義行為。

---

## Finding 3(major)— S1 掃描範圍「body」與「frontmatter summary 也掃」自相矛盾,且與「抄 Check N」的實作方式衝突

引句：「的 body(frontmatter 的 summary 行也掃——承認句多在 KEY 行)」

**問題**:這句話的字面意思是「掃描範圍=body,但額外把 frontmatter 裡的 summary 行也塞進來」——暗示其餘 frontmatter 欄位(`tags`/`related`/`decisions` 等)不掃。但 S1 同時聲明「抄 Check N 掃描結構」(第 31 行:「Check A 抄 Check N 掃描結構」)。實際的 Check N 掃描方式是整檔 `read_text` 後只做圍欄抹空,不區分 frontmatter 與 body、也不挑欄位(`scripts/lumos:1224` 讀入 `text = (env.vault / rel).read_text(...)`,`scripts/lumos:1244-1246` 只把 fenced code block 抹空,frontmatter 其餘欄位原樣留在被掃的 `text` 裡):
```
text = (env.vault / rel).read_text(encoding="utf-8-sig")
...
_fence_re = re.compile(r"```.*?```", re.S)
text = _fence_re.sub(lambda fm: " " * len(fm.group(0)), text)
```
若真的「抄 Check N 掃描結構」,結果是**整份 frontmatter 全掃**(不只 summary),與「body(...summary 行也掃)」暗示的「其餘 frontmatter 不掃」互相矛盾。這不是文字瑕疵——兩種讀法會掃到不同範圍,而 S1 是**硬擋**(rc1)。若字面照抄 Check N,`related:`/`decisions:` 等欄位裡若剛好出現詞表命中的字串(例如某 Issue 標題含「零檢查」之類措辭被 wikilink 進 `related:`),會被硬擋,而這並非規格文字所描述的「summary 行」範圍。

**file:line 證據**:`scripts/lumos:1224`(Check N 整檔讀入,不分 frontmatter/body)、`scripts/lumos:1244-1246`(僅圍欄抹空,frontmatter 未被排除)。

**正確的 spec 應該說什麼**:明確二選一並寫清楚——①「掃全檔原始文字(含全部 frontmatter 欄位),與 Check N 完全同構」,②「只掃 frontmatter 解析後的 `summary` 值 + fence-strip 後的 body,其餘 frontmatter 欄位排除在外」(這需要比 Check N 多一步 frontmatter 欄位過濾,不是單純複製貼上)。兩者實作路徑與誤判面完全不同,目前文字兩者都像在講、卻互斥。

---

## Finding 4(major)— `--stale-gates N` 沒有處理與 `--since` 查詢窗口的耦合,會把「窗口外」誤判成「從未出現」

引句：「只列「距末見 ≥N 天或從未出現」的 gate」

**問題**:`gov --stats` 的資料是先被 `--since`(預設 90 天,`scripts/lumos:14237`)過濾出的窗口內事件,`cutoff` 只算「近 since_days 天」(`scripts/lumos:2965`):
```
cutoff = (datetime.date.today() - datetime.timedelta(days=since_days)).isoformat()
```
「距末見天數」與「未出現清單」(`scripts/lumos:2946` `absent = [g for g in _KNOWN_GATES if g not in agg]`)都只根據**窗口內**載入的 `agg` 算。如果某個 gate 實際上 100 天前才觸發過一次,但使用者只用預設 `--since 90` 執行 `--stale-gates 150`(想找「≥150 天沒動」的閘),這個 gate 在 90 天窗口內完全零筆,會被歸進「從未出現」桶——但它其實不是「從未出現」,只是「不在這次查詢窗口裡」,真實距末見天數是 100 天,並不滿足「≥150」的門檻,卻會被 `--stale-gates 150` 的過濾結果誤列為退場候選。文件也沒提到「N 應該 ≤ `--since`」這種前置條件或自動放寬窗口的機制。這正是這個功能存在的目的(挑退場候選)會給錯結果的情境,而不是邊角案例。

**file:line 證據**:`scripts/lumos:14237`(`--since` 預設 90)、`scripts/lumos:2965`(`cutoff` 只用 `since_days` 算)、`scripts/lumos:2946`(`absent` 只看窗口內 `agg`,不看窗口外)。

**正確的 spec 應該說什麼**:`--stale-gates N` 要嘛強制要求 `--since >= N`(不滿足就 rc2 或自動把窗口拉到 N),要嘛在「從未出現」與「距末見 ≥N 天但落在窗口外、無法確認」之間明確分成兩桶,不能把兩者混在同一份「退場候選」清單裡呈現成同一種確定性。

---

## Finding 5(minor)— 判定枚舉漏了「A 型帶多餘欄位」這個違規情況

引句：「型別非 A|B|C/B 的 issue 不存在或非 issue」

**問題**:標記規格明講 A 型「無其他欄」(第 41 行:`<!--lumos:risk=A-->` 天花板型,無其他欄),但緊接著的「判定」枚舉(第 46 行)只列了「無標記/型別非 A|B|C/B 的 issue 不存在或非 issue/B 的 downgraded 非法或未來日/C 缺欄」五種失敗態,沒有把「A 型卻帶了 issue=/downgraded=/why= 等多餘欄位」列為 finding。屬於測試枚舉不齊,不影響核心閘判定方向,列 minor。

**file:line 證據**:此為規格文字本身的枚舉缺口,無對應既有 code(功能尚未實作),故無 file:line 可引;僅指出規格內部第 41 行與第 46 行不一致。

**正確的 spec 應該說什麼**:判定枚舉補一條「A 型帶除型別外的其他欄位 → 一條 finding」,並在測試策略(t_checka_*)裡加一個對應案例。

---

blocker: 0, major: 4, minor: 1
