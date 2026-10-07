severity: minor

驗證方式:把兩邊 register.ts 與案例檔複製到 /tmp 臨時目錄,用 node --experimental-strip-types 直接 import `seatOf` 與 `parseMarker`,對 13 種前綴(空、BOM、全形空白、ZWSP、U+2028、tab、U+0085、VT、FF、NBSP、U+2060、CR)乘 15 種標記寫法(標記後接 tab、全形空白、尾端 ZWSP、全形 LUMOS、標記後接 U+2028 或 U+0085、第三段全是 ZWSP、很長的 emoji 值)乘 2 種尾巴,共 390 組,兩邊結果(事件帳取前 200 字後比)0 組不一致。兩份案例檔 cmp 一字不差,案例每筆在事件帳 seatOf 上都符合期望(守衛端由 guard.test.ts 跑)。

逐項結論:
- 開頭 BOM、全形空白行、只有格式字元的行:兩邊都用同一個 `clean`(NFKC 加剝 `\p{Cf}`)判空行,同樣跳過;事件帳 `if (!clean(raw)) continue` 與守衛 `firstLine` 一致。
- 判成標記後,事件帳用 `SEAT_RE.exec(raw.trim())`,守衛用 `SEAT_RE.exec(line)`(line 即 `raw.trim()`),比對對象同一個字串。
- 守衛多了 SEAT_LOOSE_RE 這一關(判 none 或 bad),事件帳沒有;但凡 SEAT_RE 比得上,開頭必是 ASCII 的 LUMOS-SEAT 加冒號,必過 loose 判準,所以 loose 不通過的情形一定也過不了 SEAT_RE,結果同為 null。
- 標記後接 tab、全形空白:`\s` 涵蓋,兩邊同樣取第一個 token。
- `segOk`:事件帳版少了 `typeof p === 'string'`,但輸入來自 `split`,必為字串,無差。

### F1 前 200 字截斷可能切在代理對中間
severity: minor
blocking: 否 — 只在席名帶 emoji 且總長超過 200 字的非常態輸入下發生,且 `pattern`、`cmd` 既有的截斷本來就同寫法
引句:「return parts.length === 3 && parts.every(segOk) ? m[1].slice(0, 200) : null」
最小重現:`seatOf('LUMOS-SEAT: a/r1/' + '😀'.repeat(150))` 回傳長度 200、最後一個碼元是 0xd83d(孤立高代理)。JSON.stringify 會寫成 `\ud83d` 跳脫,Python `json.loads` 讀回孤立代理字元,之後若讀取端以 UTF-8 輸出該字串會丟 UnicodeEncodeError。⚠ 後半(讀取端是否真的印出 seat 欄)我只確認 `lumos events` 文字輸出不含 seat、JSON 輸出沒實測,未能重現到崩潰。實際席名不會帶 emoji,所以只標 minor;守衛端不截斷所以兩邊沒有分岔。

## 圖譜鏡頭
- lumos-cli-read(★INVARIANT★ search 預設排除 superseded):本次未動 search 與其濾網,牽連檔只是 scripts/lumos 與 test_lumos.py 被列入;不影響。
- guard-kill(rc 優先序、--json 純度):未動 guard kill;不影響。
- design-loop(處置閘第五步,審材須為 .md 計劃):本次計劃筆記仍是 .md,計劃條款 S1–S4 都有 [manual:]/[test:] 綁定;不影響。
- 測試假綠形態(還原翻紅釘須配現場成立前置斷言):`t_ledger_seat_re_matches_guard` 的抽取正規式改成 `^const SEAT_RE = /(.+)/$`,兩支外掛 `check("...抽得到 SEAT_RE")` 先斷言抽得到,再比一字不差,有前置斷言;案例檔比對有 `is_file()` 前置。不影響。
- lumos-cli-lifecycle(re-inject 只覆蓋 sentinel 之間):未動 re-inject;不影響。
- reversibility-governance-ledger、pitfalls-code-loop、loop-convergence-recording:只因 scripts/lumos 被牽連,本次 diff 沒改 scripts/lumos;不影響。
- lumos-guard、lumos事件帳(家):about_code 都已補 seat-fixture.ts,筆記敘述與程式一致;lumos-guard 該節第三點寫「事件帳那樣兩端各寫一份再拿同一組案例對」與本次作法相符。
- 小提醒(非 finding):事件帳筆記寫「派工詞第一個非空行是合格審查席標記時的值」,與計劃的「守衛會認成審查席」相比略簡,但不矛盾。

總結:最嚴重 minor,blocking 0 條
