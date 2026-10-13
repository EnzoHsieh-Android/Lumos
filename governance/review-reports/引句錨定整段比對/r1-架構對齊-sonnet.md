severity: major

我只讀了 spec 與程式,沒改任何檔,也沒建實驗目錄。

## 1. 「反引號/圍欄遮蔽」沒指定重用既有函式,有重寫第二份的風險
severity: major
blocking: 是
引句:「包在反引號行內程式碼或 ``` 圍欄程式碼區塊裡的不算(說明文字示範格式時常這樣寫,舊抽取器會誤抓,見 Issue 第四點)。」
file: `scripts/lumos:4902` `_visible_lines` 的說明寫「全檔唯一的 fenced-code 判定實作」。
file: `scripts/lumos:375` `_strip_inline_markup` 的說明寫「全檔唯一,別在別處自寫第二份」。
file: `scripts/lumos:404` `_inline_hidden` 是行內可見判定的「唯一本體」。
file: `scripts/lumos:390` `_inline_visible_mask` 是位置不動的遮罩版。

1. 既有做法:圍欄用 `_visible_lines` 逐行 toggle(含縮排 ≤3、嚴格/寬鬆兩段式),行內用 `_inline_hidden` / `_inline_visible_mask`。這兩支都明文禁止第二份。
2. spec 做法:S4 與抽取規則 1 只寫「包在反引號或圍欄裡的不算」。沒有說用哪支既有函式,也沒說不重寫。`_quote_rows` 目前是整份文字的 regex(`scripts/lumos:25773`),實作者最順手的做法就是在裡面自寫一個「圍欄/反引號掃描」。
3. 差在哪:
   - `_visible_lines` 回的是剝掉圍欄標記行、行號重編的行串,位置會變。
   - 規則 2 要跨行配對括號,所以必須用位置不動的遮罩。行內的 `_inline_visible_mask` 可以;圍欄這邊沒有現成的遮罩版,spec 沒說要新增還是改接。
   - `_inline_hidden` 的語意是「未閉合反引號之後整行不信」。同一行有落單反引號時,它會把後面的「引句：「…」」整段遮掉。這是否可接受,spec 沒寫。
4. 判準:引入第二種遮蔽做法才算 major。spec 必須點名重用哪兩支,並說明遮罩如何跟跨行括號配對接起來。

## 2. 缺 ts 時 fail-open 到舊判準,跟既有兩個先例都不同
severity: major
⚠
blocking: 是
引句:「早於或缺 `ts` 用舊判準;記帳寫側、手動 `quote-check`、席位核對 `seat-check` 一律用新判準」
file: `scripts/lumos:25958` 這一帶(資安席生效日判定)對 ts 讀不動或沒帶時區回 `fail`,註明「壞資料不放行」。
file: `scripts/lumos:10493` 和 `scripts/lumos:26437`:`_SEV_WRITESIDE_CUTOFF` 直接字串比日期。

1. 既有先例一(`_SECURITY_SEAT_SINCE`)是壞 ts 就 fail closed;先例二(`_SEV_WRITESIDE_CUTOFF`)是字串比對。spec 說要照搬這兩個,實際走的是第三種:缺 ts 退回比較寬的舊判準(fail-open)。
2. `_loop_ts_key` 對沒帶時區的 ts 也回 `None`(`scripts/lumos:11758`)。spec 沒寫 `None` 時走哪邊。
3. 實況:`docs/.canary-log.jsonl` 4205 列,沒有任何一列缺 ts 或缺時區。所以「缺 ts 用舊判準」目前是死分支,卻開了一個降級後門。同帳上的資安席是擋下,這邊是放行。
4. 判不準 ⚠:缺 ts 退回舊判準,若是為了回放相容才這樣設計,spec 應寫明理由,並說明為何不比照資安席擋下。

## 3. PRIOR-ART 把 `_SEV_WRITESIDE_CUTOFF` 的比較方式說錯,spec 與測試對常數形狀不一致
severity: major
blocking: 是
引句:「切換時間設在合入隔日、帶時區,比較走 `_loop_ts_key` 換算 UTC(那兩處註解記載的坑:合入當天白天仍有人用舊碼寫帳;字串比日期會依記帳機器時區判不同)。」
file: `scripts/lumos:9966` `_SEV_WRITESIDE_CUTOFF = "2026-08-27"` 是純日期字串。
file: `scripts/test_lumos.py:26935` 測試寫 `f"{m._QUOTE_STRICT_SINCE}T00:00:00+08:00"`。

1. `_SEV_WRITESIDE_CUTOFF` 不帶時區,比較也不走 `_loop_ts_key`,是字串比對(`scripts/lumos:10493`、`scripts/lumos:26437`)。「比 `_loop_ts_key`、字串比日期會判不同」那句只出現在 `_SECURITY_SEAT_SINCE` 的註解(`scripts/lumos:8217`)。spec 把兩者混成一個「既有做法」。
2. 常數形狀的矛盾:
   - spec 說 `_QUOTE_STRICT_SINCE` 是帶 `T00:00:00+08:00` 的完整時戳,寫法同 `_SECURITY_SEAT_SINCE`。
   - 先寫好的紅測試卻把它當純日期,再自己接上 `T00:00:00+08:00`。
   - 照 spec 的形狀實作,測試會得到 `...T00:00:00+08:00T00:00:00+08:00`,既讀不動,又讓「切換日當天」那組永遠過不去。
3. 要二選一定案:常數選哪個形狀、比較走哪支,spec 和測試要同步。
4. 判準:同一件事在 spec 與既有測試裡成了兩種做法。

## 4. 舊/新判準並存於 `_quote_rows` 的方式沒說
severity: minor
⚠
blocking: 否
引句:「抽取函式多一個「用哪一版判準」的參數(預設新判準)。」
file: `scripts/lumos:25774` 說明寫「★單一實作★」。
file: `scripts/test_lumos.py:26838` 測試呼叫 `m._quote_rows(report, _QFS_SNAP, strict=strict)`。

1. 照 spec 加參數、舊判準留在同一函式內,不算違反單一實作。但 spec 沒有明說舊判準分支留在 `_quote_rows` 內,不另開 `_quote_rows_legacy`。
2. 參數名稱 spec 沒寫,測試用的是 `strict=`。實作者只能從測試反推。
3. 另外有兩個測試替身用 `def quote_rows(*args)`(`scripts/test_lumos.py:27186`)和 `lambda *_`(`scripts/test_lumos.py:36926`),不收 kwargs。只要寫側呼叫沿用預設值、不傳 `strict`,就不會踩到。處置閘那邊傳 `strict=` 才是新路徑。
4. spec 值得補一句:寫側三處(`scripts/lumos:10965`、`scripts/lumos:26529`、`scripts/lumos:26787`)不傳參數。

## 5. 處置閘「載體那筆帳的 ts」未涵蓋 vacuous 輪
severity: minor
blocking: 否
引句:「處置閘照該輪載體那筆帳的 `ts`(`_loop_ts_key` 換算 UTC)決定:不早於切換時間用新判準」
file: `scripts/lumos:26319` `_qsrc = carrier if carrier is not None else latest[-1]`。

1. 既有處置閘在 vacuous 輪(零發現)沒有載體,改取 `latest[-1]`。
2. 該輪走到抽取的前提,是 vacuous 輪的 `ok and vacuous and carrier is None` 分支會印「略過」,不抽引句(`scripts/lumos:26369`)。所以這個缺口不影響結果,但「載體」一詞與既有 `_qsrc` 的用法不完全一致。
3. 建議對齊既有 `_qsrc` 取法(當前只有 carrier 路徑會真的讀)。

## 6. 不推進 `_REPLAY_ENGINE_REV` 與既有做法一致
已讀,無 finding。
file: `scripts/lumos:9969` 版本常數停在 `d5-2026-08-25`,早於 `_SECURITY_SEAT_SINCE`(09-12)。資安席與嚴重度寫側的向前生效改動都沒推版本。spec 照這個先例走,並要求推送前實跑回放黃金抽查,對齊既有規矩。

## 7. `lands_in` 與範本、SKILL 引用
severity: minor
⚠
blocking: 否
引句:「  - Systems/loop-convergence-recording」
file: `docs/lumos-toolchain-knowledge/Systems/design-loop.md:62` 是收貨三道的既有家,內有 `quote-check` / `_quote_rows` 的描述。
file: `docs/lumos-toolchain-knowledge/Systems/loop-convergence-recording.md:84` 的 `about_code` 只列 `scripts/lumos`。

1. `_quote_rows` 的現況在 `Systems/design-loop.md` 有 `quote-check` / `_quote_rows` 的描述。`loop-convergence-recording` 只有 12 處提到引句或 quote。
2. 選 `loop-convergence-recording` 作 `lands_in` 未必錯,但哪一篇是 `_quote_rows` 的家,spec 沒指明。判不準,建議開工前確認。
3. 範本與 SKILL 引用核對過:`templates.md` 的錨定紀律那行在 §1(第 63 行),`lumos-code-loop/SKILL.md` 第 34 行有同句摘述,兩處都存在,spec 的同步改動目標成立。

總結:最高等級 major,blocking 共 3 條(第 1、2、3 條)。
