severity: minor

## F1 空的 rules-unwired/ 在 git 裡留不住,目錄一消失自檢就紅
severity: minor
blocking: 否
引句:「+ruleDirs:」
佐證: `configs/ast-grep/kotlin-android/sgconfig-unwired.yml:1-2`、`configs/ast-grep/kotlin-android/check.py:787`(迴圈 `for d, cfg in CONFIGS` 逐一核對載入條數)
失敗場景:`sgconfig-unwired.yml` 是追蹤檔,它指向的 `rules-unwired/` 目錄裡一旦沒有 yml,git 就不會留住這個空目錄。我在暫存複本重現:
- 只刪 `rules-unwired/*.yml`、目錄還在時,自檢不報這四項(只剩我複本缺 `scripts/lumos` 的那一項,是我造成的)。
- 連目錄一起刪掉時,自檢多報 4 項:`sgconfig-unwired.yml 讀不到載入條數`,以及 `掃 samples/bad`、`掃 samples/good`、`掃 samples/ancestor-named-test` 跑不起來。
- 計劃說這個目錄會收「還沒量過的新規則」,規則來來去去,清空是遲早的事。clone 下來沒有目錄,報錯訊息是「掃描逾時或 ast-grep 跑不起來」,看不出原因。
- `t_kotlin_rulepack_samples` 的「規則目錄全空」測試只 `unlink` 檔案、不刪目錄,蓋不到這條路徑。
- 建議:目錄放 `.gitkeep`,或自檢在目錄不存在時給明確訊息。
- 目前 8 條都在,實況不紅。

## F2 sgconfig-unwired.yml 沒登記進 Systems/kotlin規則包 的 about_code,節點卻用反引號寫它
severity: minor
blocking: 否
引句:「+- `configs/ast-grep/kotlin-android/sgconfig-unwired.yml`:不接閘的規則(`rules-unwired/`,任何等級)」
佐證: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:8-13`(about_code 只列 `sgconfig-hints.yml`、`sgconfig-review.yml`,新檔沒加)、`docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:64`
失敗場景:我跑 `lumos impact --file configs/ast-grep/kotlin-android/sgconfig-unwired.yml`,它只因 `body-inline-code` 才關聯到這個節點,而不是 about_code。同層的 hints、review 兩支 sgconfig 都有登記,這支新檔沒有,違反「每支檔有家」的慣例,以後改這支檔不會被家的 RULE 與 WHY 推到眼前。`lumos lint` 目前 0 問題,沒機械擋。

## F3 RULE 行字面改了,`[confirmed:]` 被順手改成今天,沒有人重新確認的依據
severity: minor
blocking: 否
引句:「[retire:人裁] [until:2027-05-05] [confirmed:2026-11-08]」
佐證: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:24`
失敗場景:RULE 要靠「最近半年有人確認過」才有效力(CLAUDE.md 第 3 條)。這次的 diff 把句子從「降提示級」改成「降提示級、搬 rules-unwired/ 或改形狀」,同時把 `[confirmed:]` 從 2026-11-05 改成 2026-11-08,但看不到這句新版本是誰確認的。
- 效果:重新確認的日期被蓋成今天,等於替人表態。
- 兩種處理擇一:保留舊的 `confirmed`,或在計劃或卷證寫明 11-08 的人裁出處。
- 旁證:`WHY` 行的 `[出處:]` 仍引 11-05 使用者的話,但結論已經從「只准提示級」改成「只准 rules-unwired/」,出處與現行結論不完全對應。

## F4 SARIF_PROBES 寫死規則 id,規則改名或搬走時錯誤訊息會誤導
severity: minor
blocking: 否
引句:「SARIF_PROBES = (("sgconfig-review.yml", "kt-livedata-setvalue-background"), ("sgconfig-hints.yml", "kt-value-assign-background"))」
佐證: `configs/ast-grep/kotlin-android/check.py:704-707`、`configs/ast-grep/kotlin-android/check.py:821-826`
失敗場景:`kt-value-assign-background` 若日後被搬到 `rules-unwired/` 或改名,`check()` 會報「SARIF 掃壞例樣本沒有 kt-value-assign-background 的結果」。這句看起來像是 ast-grep 的 SARIF 壞了,實際是探針指錯規則。探針 id 沒有對照 `load_rules()` 驗證。
- 本版兩條規則都存在,自檢 0 問題,實況不紅。
- 輸入走查(`sarif_rule_ids`):空輸出、`null`、頂層是 list、`runs` 是 null、`runs` 是 dict、`runs` 含 null、`results` 是整數、`ruleId` 是 list、BOM 開頭、rc=2,都回 `None` 或空集合,沒有例外。
- 多行 JSON 與 `ruleId` 為 null(得 `{None}`)也不崩。
- 這一節沒有 finding。

## 型錄格子改寫(`behavior_value`)
- 8 列的格子改成「告警帶寫法=未接(規則在 rules-unwired/:型錄這列出處不全)」。
- `behavior_value` 只讀「行為測試或正向約束=」這一段,與「告警帶寫法=」前綴無關。
- 格子裡沒有分號,不會被切壞;`check.py` 與 `-k kt_rulepack_unwired`(8 項)、`-k kotlin_rulepack_samples`(25 項)都綠。
- 規則搬移的 `---` 分隔、`# T14`、`# T35` 註解都跟著走,未見漏分隔。載入條數 hints 42、unwired 8 由自檢通過間接佐證。

## pitfalls manifest
- 分級命中的「共享狀態有沒有鎖保護」(指向 `rules-unwired/coroutines.yml` 第 11 行)是**誤報**。
- 第 11 行是 ast-grep 規則文字 `- pattern: $M.lock()`,不是會跑的併發程式碼。這份 diff 沒有新增任何 Mutex 使用或共享狀態。
- 併發類在這個 repo 判範圍外,所以標誤報即可。
- 這屬於 `Issues/Kotlin規則包代碼審放行的小問題` 已記的「推送閘把規則包內容當產品碼」那一族,只是這次是規則檔而不是樣本檔。

## 固定席判定
- `Systems/kotlin規則包`:
  - 無合約。
  - 行為面沒新增矛盾:`rules-unwired` 放行任何等級只在 `_DIR_SEVERITY` 一處,出處不全的檢查改成「不在 unwired 就報」,測試 ①②⑤ 涵蓋缺 `dir` 與錯目錄。
  - 落差見 F2(新檔沒進 about_code)與 F3(RULE 確認日期)。
- `Systems/測試假綠形態 ★INVARIANT★`:
  - 新測試 `t_kt_rulepack_unwired_dir` 逐條標了翻紅釘,輸入造的是假規則,不用被測函式算預期。
  - SARIF 那項只驗了失敗路徑(空結果、讀不懂),沒驗成功路徑「讀得到且 rid 在內」會真綠。成功路徑靠真 `check()` 跑到 0 問題間接覆蓋。我沒能造出假綠,所以不判違反。

總結:最高等級為 minor,blocking 共 0 條
