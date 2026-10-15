severity: major

審查對象是修後 20df2187 的文件半邊(`r3-repair-docs.patch`)。我實際讀了 `scripts/lumos`,並跑了去處詞表、e2e 路徑、xargs 與 kill 觸發、子句邊界和量法程式。

## Findings

**1. d1 決策文字還寫著舊的去處字,跟程式不一致**
severity: major
- blocking: 是
- 位置:`Projects/前端知識與風險詞_計劃.md` 開頭 `decisions:` 的 d1。
- 問題:d1 說「後面緊接寫出去處——給、到、至、往——照算」。修後程式 `_PITFALL_SEND_DEST` 只認「給」加外部名詞,「至 往 向 對 予」和「到」都拿掉了。同一份計劃的做法 9 與程式註解已經改過,只有 d1 沒跟上。決策有挑戰程式的效力,三個月後的人會照 d1 把「至、往、到」當去處加回去,把 r2 的 major 修回去。
- 具體例:
  - 「送出表單至客服信箱」依 d1 應照算。修後程式不命中(我跑過,空結果)。
  - 做法 9 也明寫它在 r2 改成不算。
  - 「送出請求到外部」仍命中,但靠的是「外部」,不是「到」。
- 引句:「後面緊接寫出去處——給、到、至、往——照算」
- 歸因:有證據的修復回歸。
  - 修前 f14f6808 的程式 `_PITFALL_SEND_DEST` 是 `[給至往向對予]`,d1 與程式一致。
  - 修後 20df2187 程式改了,d1 仍是同一句(`grep -c "給、到、至、往"` 兩版都是 1)。
- 附帶:d1 的 `context` 寫「356 份」,做法 9 寫 357 份,屬 minor。

**2. 做法 7 的「寫法」正規式是舊的,跟程式和 S61 相反**
severity: minor
- blocking: 否
- 位置:做法 7 的「寫法(2026-10-15 代碼審 r1 修正後)」那行。
- 問題:文件的 `^(?!(?:[^/]+/)*?(?:src|lib)/)…` 是 r1 版。修後程式是 `^(?!(?:[^/]+/)*?(?:src|lib)/(?:[^/]+/)*?e2e/)…`,只在 src、lib 出現在 e2e 之前時才排除。
- 具體例:
  - `e2e/lib/x.ts` 和 `e2e/src/a.ts`,依文件正規式是 False(排除),依程式 `_is_test_infra_file` 是 True(infra)。
  - 這正是 S61 要求的行為,所以文件這行跟 S61 自相矛盾。
- 歸因:有證據的修復回歸。修前文件與程式的正規式一致;r2 改了程式,文件這行兩版逐字相同,一直沒改。
- 引句:「寫法(2026-10-15 代碼審 r1 修正後):`^(?!(?:[^/]+/)*?(?:src|lib)/)(?:[^/]+/)*?e2e/|\.e2e\.|」
- 同樣沒跟上的措辭(指向「路徑中有 e2e/ 且不在 src、lib 底下」,沒說明 e2e 之下的 lib、src 不排除):
  - 做法 7 第 1 形狀。
  - 效能檢核目錄 infra 節。
  - pitfalls-code-loop 新節。
  - 實務隱患守衛面那條。

**3. 效能檢核目錄的 infra 觸發表和綁定測試清單沒同步**
severity: minor
- blocking: 否
- 位置:`Systems/效能檢核目錄.md` 的 `infra-signal`、`infra-pid` 兩列,以及 infra 節末的「綁的測試」。
- 問題:
  - 兩列缺修補後的 `xargs` 之後(選項可帶一個參數),也缺 `.kill(`。
  - 做法 6 表格(修補差異有改)已經寫了,但這張表沒跟。
  - 該節的觸發說明只寫「`xargs kill`、`process.kill(`」。
  - 綁定測試清單缺 `t_infra_kill_variants`、`t_infra_xargs_many_spaces_linear`、`t_test_infra_path_e2e_inner_lib_src`。
  - 我跑過 `xargs -I {} kill {}`、`xargs -n 1 kill`、`child.kill()`、`os.kill(`,程式都命中 infra-pid,所以是表落後,不是程式錯。
- 引句:「| `infra-pid` | infra | 殺程序前有沒有確認 pid 是自己起的… | 指令位置的 `kill` `pkill`、`pgrep`、`$!` | `.pid` |」
- 歸因:有證據的原有漏查。這張表在修前就沒有 `xargs` 與 `.kill(`,修補差異也沒動它;目錄與表雙向同步的規定是計劃自己立的。

**4. S45 的條件描述沿用舊去處字**
severity: minor
- blocking: 否
- 問題:S45 寫「去處寫成向、對、予、隔字的到……」。S45 綁的測試的例句靠客戶、第三方、外部這些名詞仍命中,所以測試不會紅。但條款描述的觸發條件已經不成立。
  - 例:「送出請求後將資料同步到 ERP」有隔字的到,卻不命中,做法 9 天花板也這樣寫。
- 引句:「[S45] 當計劃一行寫「系統會向客戶送出請求」這類去處寫成向、對、予、隔字的到、或寫在送出前面的句子時」
- 歸因:有證據的修復回歸。修前去處字含向對予到,描述成立;r2 改程式後,條款描述沒改。

## 已核對、沒問題的部分

- **去處詞表逐詞**:給、外部、第三方、客戶(不含客戶端)、廠商、供應商、銀行、物流、平台方、partner、vendor、external 都命中。
  - 做法 9 的照算與不算例句,我跑過 35 句,結果全部符合。
  - 天花板列的句子確實不命中。
  - 舊天花板裡「表單送出後通知客戶」其實會命中(客戶),r3 把它從天花板拿掉是對的。
- **子句邊界**:`_PITFALL_SEND_STOPS` 共 65 個碼位且含換行,文件說的數字正確。我對 BMP 全碼位掃過,沒有 NFKC 後成為這幾個標點、卻不在清單裡的碼位。網址的點與冒號不切子句,程式也確實如此。
- **80 字與效能**:文件的效能數字能重現。
  - 100 萬字滿是「請求送出」的單行,經 `_door_keyword_hits` 掃要 2.71 秒(文件寫 2.6)。
  - 400 萬字原始比對 5.17 秒(文件寫 5.2)。
  - 540 萬字不含送出的單行 0.27 秒(文件寫 0.33)。
- **e2e 三種路徑與排除**:
  - `crypto/e2e/a.ts` 仍算 e2e,`server/order.e2e.ts` 是 infra。
  - `src/e2e/cipher.py`、`lib/e2e_encryption.py`、`e2easy.ts`、`db/seeds/x.sql` 不算。
  - `e2e/a.kt` 不算,照掃 claims。
  - `scripts/setup.sh` 是 infra。
  - 這些都跟文件一致。
- **量法程式**:照字面抽出來,以 `git show cd1f9619:scripts/lumos` 當舊版、`scripts/lumos` 當新版跑,可以跑完。輸出「353 份;多出命中 0 份;不做清單略過詞集合變了 0 份;少掉命中且整份再無命中 0 行」。353 份是本 repo 的份數,文件的 357 是加上三個消費專案後的總數,不矛盾。
- **S 條款綁的測試**:計劃裡所有 `[test: …]` 的測試名都存在於 `scripts/test_lumos.py`。`lumos lint Projects/前端知識與風險詞_計劃` 報 0 問題。
- **前端字樣**:`_REQ_FE_WHEN` 認得 Vue3、SvelteKit、front-end、React.js、angularjs、preact10;不誤中 vuex、reaction、nextcloud、Reactor。情境出題的字樣列表與之相容。
- **每輪修補差異派工的 SEE 行**:現為 `SEE:[[Systems/design-loop]]`,有連結,形狀合格。該節點 `about_code` 確實列了 `templates.md`,前端補充與 §7.8 的說明也確實在 design-loop.md。
- **規格閘與雙向門放行**:規格閘金流詞表那格(`_TIMEOUT、_DELAY、_RETRIES、_RETRY_COUNT` 不算,`_LIMIT、_COUNT、_WINDOW` 照算)與程式一致。雙向門放行取捨段的送出說明也一致。
- **舊說法殘留**:`seeds/fixtures` 已改成「不收」。未發現 LIMIT/COUNT 被當成可放行的殘留說法,也沒有「只認 給至往」之外的其他殘留。「向對予至往到」舊去處字只剩 d1 與 S45(見 finding 1、4)。

## 三問

1. **原問題的修復效果**:文件半邊的程式描述(詞表、80 字、e2e 範圍、xargs/kill)大多已跟程式一致,證據是上面的逐項重跑。d1、做法 7 的正規式、S45 這三處還留著 r2 之前的說法。
2. **修補處相鄰路徑**:我只核了文件對程式行為的描述。程式本身的回歸,例如 NFKC 邊界、xargs 二次方、e2e 排除範圍,不在我的鏡頭內,也沒有另行重跑過測試。
3. **新發現在修前、修後各是什麼**:
   - Finding 1、2、4 是修前文件與程式一致、r2 修程式後文件沒跟上。
   - Finding 3 修前就落後,屬原有漏查。
   - 修前版本我只用 `git show` 比對了文件與 `scripts/lumos` 的相關字串,沒有重跑修前的測試。

最嚴重 severity: major,blocking 共 1 條(finding 1)。

臨時目錄 `/tmp/lumos-seat-work/code-前端知識與風險詞/整合-sonnet/` 還留著 `p.py`、`q.py`、`measure.py`、`lumos_old`,我沒刪,由編排者在這輪席報告收齊後依規則清掉。
