severity: major

整體用白話講:這一輪把「猜名字」整段拿掉是對的,猜法被打穿的洞確實補上了。但換成「照擋」之後,擋下來訊息教的修法走不通。另外斷言文字改保留字串的做法,有一處計數副作用,也有兩處測試抓不住改壞。

## Findings

**F1**
severity: major
blocking: 是
檔案:`scripts/lumos`(`_spec_gate_push_one`,`cfg_gone` 那段,修後約 16006–16012 行)
引句:「(或改一個字讓留痕過期)再重跑 lumos spec-gate {_sh_quote(Path(prel).stem)}」

失敗場景:多平台專案的預設平台條款通常寫裸名,例如 `[test:fee_jvm]`,留痕卻記成 `jvm:fee_jvm`。設定改回單平台,實作已經做綠。這時推送被擋,訊息叫人重跑規格閘,實際上怎麼跑都走不出來:
1. 條款沒動就重跑,規格閘印「已有放行留痕、條款沒變;測試現在綠=已做完,不用重跑」,不寫新留痕。再推,同一句訊息又擋。
2. 照訊息「改一個字」再重跑,規格閘改判「S1 fee_jvm 綠——新行為現在就該紅」,rc=1,一樣不寫留痕。再推,變成「風險低留痕過期」又擋。
3. 唯一的出路是把實作還原成紅、補跑規格閘,或把計劃改成 plan_risk: high。訊息沒講這條路。

「照現在的設定改條款的測試寫法」這句也不適用,因為這個情境下條款本來就是裸名、合法。

重現:我在修後版本的測試目錄副本裡加了探針測試(沒動 repo)。步驟是照 `t_spec_gate_record_keeps_platform` 的 mp1b 情境做完設定改回單平台,再依序推送、重跑、改字重跑、再推。

| | 修前 e0603d082 | 修後 374e77519 |
|---|---|---|
| 設定改回單平台後推送 | `PUSH1 0 ✓ 留痕裡的 1 支測試全綠(jvm:fee_jvm)` | `PUSH1 1` |
| 條款沒動就重跑 | — | `RERUN_SAME 0`,印「不用重跑」,留痕仍是 `['jvm:fee_jvm']`;再推 `PUSH2 1` |
| 改一字後重跑 | — | `RERUN_CHANGED 1`,留痕仍是 `jvm:fee_jvm`;再推 `PUSH3 1`,訊息變「留痕過期」 |

歸因:有證據的修復回歸。修前能放行,修後被擋,且訊息教的修法不通。
- 「換成照擋」是人裁的形狀,我不質疑。
- 缺陷在訊息:它承諾的「重跑」在實作已綠的計劃上無效。
- 計劃的 REVISIT(2027-05-03)只提到「不再要人重跑」,沒承認這條死路。
- 訊息至少要講明這種情況只能還原成紅再補跑,或改走設計審。
- 另一條路是用當時平台清單解析舊留痕,REVISIT 已提過。

**F2**
severity: minor
blocking: 否
檔案:`scripts/lumos`(`_tg_statements` 與新函式 `_tg_ws_keep_strings`)
引句:「out.append(_tg_ws_keep_strings(rb[m.start():k]))」

失敗場景:字串現在連換行一起原樣保留,但 `_tg_strong` 剝字串用的 `_TG_LIT_PAT` 認不得跨行的原始字串。多行原始字串裡出現的 `assertEquals` 字樣,會被算成一條強斷言。

重現(同一份 `_tg_analyze`):
- 改動前 `assertEquals(1, f())`,改動後 `assertTrue("""\n assertEquals mention\n """, f() > 0)`。
- 修前:`['tq/assert-weakened']`。
- 修後:`[]`,強斷言數從 0 變 1,「斷言變弱」被蓋過。

歸因:有證據的修復回歸。`_tg_strong('assertTrue("""\n assertEquals mention\n """, x)')` 修前是 0,修後是 1。要這種輸入才會踩到,所以評 minor。

**F3**
severity: minor
blocking: 否
檔案:`scripts/lumos`(`_tg_statements` 與 `_tg_expected_cands`)
引句:「text_of[li] = _tg_ws_keep_strings(rb[ls:le])」

失敗場景:只重新縮排或搬進巢狀類別的測試,如果斷言參數是帶 `.trimIndent()` 的多行原始字串,現在會被列成 `tq/expected-changed`。
- 原因是 `sig` 相同、`isig` 不同,走「只比預期值」那條路,而原始字串裡的縮排現在算內容。
- 修前這個 case 是 `[]`,修後是 `['tq/expected-changed']`。
- 整檔縮排加倍也一樣。

這是計劃有意的取捨(「字串原樣保留」),但 `.trimIndent()` 讓縮排其實不算內容,會多出可放行的候選。

歸因:有證據的修復回歸,但屬設計取捨。

**F4**
severity: minor
blocking: 否
檔案:`scripts/test_lumos.py`(`t_tq_guard_string_comma_args`)
引句:「("字串裡多一格空白", 'assertEquals("a b", f())', 'assertEquals("a  b", f())'),   # 代碼審 r3 單審席 D2」

失敗場景:`_tg_ws_keep_strings` 在 `_tg_statements` 有兩個呼叫點,新增的案例只覆蓋 `assertEquals(` 這一條。我把第二個呼叫點(中綴 `shouldBe` 那條)改回整段壓空白,`-k tq_guard` 仍是 37 passed, 0 failed。
- 實際行為:`f() shouldBe "a b"` 改成 `"a  b"`,修後會列 `tq/expected-changed`,改壞版 `[]`。
- r3-fix-mutation.md 的 Q2 只改壞了一處。

歸因:有證據的原有漏查(測試覆蓋)。這是同族路徑沒各補一支測試。

**F5**
severity: minor
blocking: 否
檔案:`scripts/lumos`(`_spec_gate_push_one`)
引句:「if cfg_gone and not done:」

失敗場景:`cfg_gone` 的「已完成計劃降成提醒」那條路沒有任何測試覆蓋。
- 我把 `not done` 拿掉,`-k spec_gate` 391 passed、`-k prepush_spec_gate` 37 passed,全綠。
- 這條路本身是對的:我用探針驗過,done 且留痕沒過期、或指紋不符,都印「提醒…設定改過?」並放行,不跑測試。
- 但已完成計劃一律不跑留痕測試,被誤擋時沒有測試會紅。

歸因:未判定,修前沒有這條路。

## 三問答覆

1. **原問題的修復效果**
   - 被刪的含冒號測試不被後綴頂替:`t_spec_gate_record_keeps_platform` 11 條全過。
   - 我另外驗過:單平台、含冒號、測試還在的名字照跑(`SINGLE_COLON_PUSH 0`,`jvm fee: rounds up` 有被執行)。
   - 抽斷言文字:`"a b"` 改 `"a  b"` 與 tab 改空白,修前 `[]`,修後 `['tq/expected-changed']`。
   - `_ENV_MISSING_WHYS` 與舊常數等價。
     - 舊值是 `_AGP_DEVICE_MISSING["why"]`,新值是兩格(kotlin、java)共用同一 dict 的 why 集合,結果是同一個單元素集合。
     - 全 repo 已沒有 `_ENV_MISSING_WHY` 舊名的殘留引用。

2. **修補處正常、錯誤與相鄰呼叫路徑**
   - 多平台不受影響:`not split` 擋掉,多平台名字不會誤進 `cfg_gone`。
   - `-k tq_guard` 405 passed。
   - 已完成計劃那條路行為正確(見 F5),但沒有測試。
   - 錯誤路徑(F1)訊息的修法走不通。
   - 順帶的行為變化:單平台下被真的刪掉的含冒號測試,修前判紅並自動記逃逸,修後照擋但不記逃逸。我沒做實跑,只看程式判斷,因為修前走 dangling 判紅、`real` 為真所以會記逃逸。這點可能是有意的,只列出來。

3. **同一案例修前修後**
   - F1:修前放行,修後擋下且重跑走不通。
   - F2:修前 `tq/assert-weakened`,修後無候選。
   - F3:修前 `[]`,修後 `tq/expected-changed`。
   - F4:正常程式下修前 `[]`,修後會列;改壞版 `[]`,測試照綠。
   - F5:修前沒有這條路;改壞(done 也擋)測試照綠,探針驗過現行行為正確。

## 圖譜鏡頭

固定席節點(`lumos-cli-read`、`guard-kill`、`測試假綠形態` 等)宣稱的合約都不在這份 diff 的路徑上,沒有破壞。`測試假綠形態` 的「還原翻紅釘要配前置斷言」:新增的 S3 d4 案例有前置斷言;只有最後一條 `ran.count("jvm fee_jvm") <= 1` 偏寬鬆,靠 `returncode == 1` 補上。

## 未驗範圍

- 計劃 PRIOR-ART 引的 Allure、Orangebeard 等外部說法,我沒上網查證。
- 全套 3700 案例沒跑,只跑了上面列的子集。
- tab 換空白的獨立案例有手動驗過,但測試檔沒有這條。
- Java 棧的行為案例沒另跑,只看到 `_ENV_MISSING_EVIDENCE` 對 java-junit 共用同一格。

我的探針腳本與副本已清掉(只刪自己這個席位目錄與一個自己留下的 gctl-run 現場)。
