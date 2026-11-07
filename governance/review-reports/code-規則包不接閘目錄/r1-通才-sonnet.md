severity: major

## F1 SARIF 實掃只認 ruleId,新增告警閘真正要讀的欄位沒驗
severity: major
blocking: 是
引句:「return {res.get("ruleId") for run in runs for res in (run.get("results") or []) if isinstance(res, dict)}」
佐證:`check.py:732`(新增的 `sarif_rule_ids`);對照新增告警閘實際讀法 `scripts/lumos:42321-42370`
失敗場景:
- 新增告警閘解析 SARIF 時有三項要求。run 要有 `tool.driver.name`,否則整個 run 被 `continue`。每筆 result 要有 `locations[0].physicalLocation.artifactLocation.uri`,缺了就 `except (KeyError, IndexError): continue`。訊息取 `message.text`。
- 上面兩個 `continue` 都不報錯,所以 ast-grep 換版後只要改掉其中一項,閘讀到零筆告警,等於靜默放行。
- 這支探針正是為了在換版時讓 CI 變紅而加的(check.py 註解:「換 ast-grep 版本時工具鏈 CI 會紅」),卻只看 ruleId,所以照綠。
- 最小重現:我寫了假 `sg`,對 sarif 只吐 `{"runs":[{"results":[{"ruleId":"kt-livedata-setvalue-background","message":{"text":"x"}},{"ruleId":"kt-value-assign-background"}]}]}`,這份 SARIF 沒有 tool、也沒有 locations。呼叫 `check.sarif_rule_ids(假sg, cfg, 樣本)`,兩組 `SARIF_PROBES` 都回傳含目標 ruleId 的集合,探針判通過,新增告警閘卻會把兩筆都丟掉。
- 新增的測試只改壞「ruleId 是別條」和「讀不懂」這兩種,沒有「ruleId 對但 locations 或 driver 缺」的案例。

## F2 型錄統計「被會擋的規則守到的列數 129」沒跟著降
severity: minor
blocking: 否
引句:「告警帶寫法=未接(規則在 rules-unwired/:型錄這列出處不全) | 規則 kt-statein-lazily-or-no-timeout、kt-whilesubscribed-no-timeout」
佐證:`skills/kotlin-idioms/checks-catalog.md:882` 與 STATE-9 列(約 235 行)
失敗場景:
- STATE-9 的通電批次從「批一…」改成「未接」,實測欄仍列 `rules/` 底下會擋的 `kt-statein-lazily-or-no-timeout`。
- 照統計行自己的定義重算:舊版 4785338d1 是 129,新版是 128,差的就是 STATE-9。這個 diff 沒動該統計行,仍寫 129。
- 這行是手寫的,沒有測試守它,所以紅不起來。
- 後果是型錄的統計與實際不符。這個數字是看有多少列真的被擋停守到的,多算了一列。

## F3 新增的 `review_ids` 納入 rules-unwired,沒有任何測試覆蓋
severity: minor
blocking: 否
引句:「review_ids = {r["id"] for r in rules if r["dir"] in ("rules-review", "rules-unwired")}」
佐證:`check.py:799`;`samples/good/` 下八條 unwired 規則都沒有 `review-fp-*` 樣本(我實查,結果 0 支);既有的 `review-fp-` 測試(`scripts/test_lumos.py:126380-126399`)只對會擋的規則
失敗場景:
- 把 tuple 改回只剩 `"rules-review"`,現有測試應該全綠,因為沒有 unwired 的 review-fp 樣本能讓它翻紅。我沒有實跑變異,未能重現,所以只列 minor。
- 之後有人替 unwired 規則加已知誤報樣本時,這條豁免是否還在,沒有任何東西會告訴他。

## F4 新增的 sgconfig-unwired.yml 在內文用反引號寫了,但 Systems/kotlin規則包 的 about_code 沒列
severity: minor
blocking: 否
引句:「+- `configs/ast-grep/kotlin-android/sgconfig-unwired.yml`:不接閘的規則(`rules-unwired/`,任何等級)」
佐證:`docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md` 的 about_code(第 8 到 14 行)只有 `sgconfig.yml`、`sgconfig-hints.yml`、`sgconfig-review.yml`。`lumos impact --file …sgconfig-unwired.yml` 只回報 body-inline-code 關聯。
失敗場景:
- repo CLAUDE.md 鐵則 5 寫「每支程式檔要有一篇管它的 Systems 節點(about_code 列了它)……節點只准用反引號寫自己家的檔」。
- 計劃範圍也承諾要補。同層的 hints、review 設定都列在 about_code,只有 unwired 漏了。
- 後果是這支檔在圖譜裡沒有正式的家,只靠內文引用被認到。
- yml 是否算「程式檔」要看 doctor 怎麼判,所以降為 minor。

## F5 `sarif_rule_ids` 又複製一份逾時與例外處理
severity: minor
blocking: 否
引句:「r = subprocess.run([sg, "scan", "--config", str(HERE / cfg), "--format", "sarif", str(target)],」
佐證:`check.py:716-734`;與 `scan`(685)、`loaded_count`(737)的 `subprocess.run` 加 `TimeoutExpired`/`_TIMED_OUT`/`OSError` 流程同形
失敗場景:
- 同一段「跑 ast-grep、逾時就設旗標」現在有三份。之後要改逾時語意(例如逾時要區分哪一步),三處要一起改,漏一處就行為不一致。
- 可以抽成一支小的 `_run_sg(args)`。

## 其餘角度
- 逐行、被刪行為、跨檔:`_DIR_SEVERITY` 的 unwired 等級、`catalog_problems` 缺 `dir` 鍵、`message_problems` 的提示文字都沒找到錯。八條規則逐字搬移,內容沒變。
- 實跑:`-k kt_rulepack_unwired` 8 項過;`-k kotlin_rulepack` 38 項過;`-k kotlin_catalog` 59 項過。

## manifest
- 內建風險型樣「共享狀態有沒有鎖保護」命中 `rules-unwired/coroutines.yml` 第 11 行。這是 `kt-mutex-reentrant` 規則檔裡的 `$M.lock()` 字樣,屬併發類題目,此 repo 判範圍外,標誤報。

## 固定席判定
- `Systems/kotlin規則包`(無合約):`about_code` 漏列 `sgconfig-unwired.yml`,見 F4。其餘 `lumos lint` 0 問題。
- `Systems/測試假綠形態` ★INVARIANT★(還原翻紅釘要配前置斷言):新測試 `t_kt_rulepack_unwired_dir` 有「★前置★ 型錄有出處不全的列」,⑥ 有 `refs and …` 非空保護;SARIF 改壞案例以 `len(hit)==2` 證明假 `sg` 真的被叫到。本 diff 未違反合約。F1 屬翻紅釘覆蓋面不足(缺 locations/driver 的改壞),不是前置斷言缺失。
- 其餘節點:只是改到超大測試總檔連帶推出,沒有新的判定。

暫存清理:實驗只在 `/private/tmp/lumos-seat-work/code-規則包不接閘目錄/通才-sonnet/` 建了假 `sg`,已用字面絕對路徑 `rm -rf` 刪掉。該目錄本身已空,未刪。

總結:最高等級為 major,blocking 共 1 條
