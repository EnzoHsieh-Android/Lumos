severity: minor

整合席結論:文件對 7655a12d 版程式的主要主張,抽查後都對得上。我找到 5 條 minor 的不一致,沒有 major,也沒有擋推送的項目。

## 1. 計劃的核可鏈筆數上限寫 10000,程式與驗證筆記是 2000
severity: minor
blocking: 否

引句:「單檔照證據的 16 MiB 上限、筆數上限 10000。」

- 這句是計劃〈核可鏈〉驗證步驟 1,在差異裡是未改動的上下文行。
- 同一份差異新增的 Verification 段寫「核可鏈上限從 1 萬筆降到 2000 筆…超過上限整道判 read_incomplete」。
- 程式也是 2000:`scripts/lumos:9305` 是 `_SECAPR_MAX_ENTRIES = 2000`,`9383-9384` 超過就丟 `_SecaprTooLong`。
- 這一輪把上限改成 2000,卻只改了 Verification,沒回頭改計劃那一句。
- 計劃也沒寫超過上限會整道判 `read_incomplete`。
- 重現:`grep -n "筆數上限 10000" Projects/安全主張驗收閘_計劃.md` 對 `grep -n "_SECAPR_MAX_ENTRIES" scripts/lumos`。
- 歸因:有證據的修復回歸。修前版 b99f52c8 上限是 1 萬,文件當時是對的;這次降上限沒同步文件。

## 2. 五道關卡的說法沒改完:`--keep-going` 說明文字與一篇系統筆記仍寫四道
severity: minor
blocking: 否

引句:「五道都判完、每道擋下各印各的,最後多一行」

- 這是 `06-代碼審與推送.md` 新寫的句子。
- 程式的 `--keep-going` 說明(`scripts/lumos:65559`)仍寫「四道判定都跑完」,函式說明文字(`62856`、`63472`)也是四道。
- `Systems/棧別提問表態閘.md:101` 同樣寫「四道都判完」。
- 實際行為是五道:安全證據在 `kg.hit(_codeloop_security_step…)`(`62883`),排最前。
- 重現:`grep -n "四道判定都跑完" scripts/lumos`。
- 歸因:有證據的原有漏查。這批文件只改了掛鉤與 skills,這幾處是更早就沒同步的。

## 3. `security approvals payload` 的旗標只文件化一半
severity: minor
blocking: 否

引句:「到期上限靠它分 30 天或 180 天;這一欄也在簽章範圍內」

- 這句出自新增的 `outcome` 欄位說明。
- 程式有 `--outcome {risk_accepted,not_applicable}`、`--content-file`、`--reason`、`--commit` 旗標(`scripts/lumos:64596-64600`)。
- 計劃〈怎麼加一筆〉和 `06` 的核可列都沒提 `--outcome` 與 `--content-file`,只有 suppression 缺 `--reason` 時錯誤訊息會提示。
- 影響:`consideration` 不帶 `--outcome` 時,鏈層上限落在 180 天。閘門在 `_secev_consideration_counted` 會用格子列的 outcome 再驗一次 30 天,所以不會誤放行,只是使用者從文件不知道怎麼指定。
- 歸因:未判定。修前版有沒有這些旗標我沒有逐版比。

## 4. S50 與 S55 條款沒跟上本輪新增的行為
severity: minor
blocking: 否

引句:「放寬允許目標或刪掉某工具類別的最後一個工具,而核可鏈上沒有有效的 tool_list_change 時」

- 這是 S55 在差異裡的上下文行。
- 計劃本文這輪改成「主線有、推送版沒有的工具名(刪掉或改名)」都算變弱,而 S55 條款仍只寫刪掉某類別最後一個工具。
- S50 條款寫「驗得過時應寫入」,但 d17 規定非互動一律擋下、要手打確認碼。
- 測試其實是對的:`t_secev_s50_first_key` 用 `_sg_pty_run` 照抄確認碼。
- 改名繞過另有 `t_secev_r1_tool_rename_is_weakening`,但只掛在 Systems 筆記的 WHY 上,計劃沒有對應條款。
- 因此「條款全綁測試」的說法成立,但條款字面不涵蓋這輪的新行為。
- 歸因:有證據的修復回歸。

## 5. Verification 的子集與全套數字是修補之前的,狀態仍寫 pass
severity: minor
blocking: 否

引句:「對修正後全綠。「跟改動前逐字相同」的三支(S1、S8、S59)改成比固定的 golden」

- 同一篇的「子集結果(拆函式之後重跑)」「第二次全套 18875 過、0 紅」都是修補前量的。
- 這輪改了 `scripts/test_quality.py`、bundle 指紋和 pre-push,正好觸發該篇 `revalidate_when`,卻沒標出哪些數字已過期。
- 我在 7655a12d 上跑了 `-k prepush_cl_reason`(5 項)、`-k secev_r1_junit`(3 項)、`-k docs_command`(4 項),全綠。
- 沒跑全套,也沒驗 anchor 簽名。
- 歸因:未判定。

## 已驗主張(對 7655a12d)
- 兩篇計劃與 Systems 筆記裡的 `[test:]` 名稱,在 `scripts/test_lumos.py` 全找得到(缺 0 個)。
- 計劃判定代碼表與 `_SECEV_CODES` 逐項對上,`approval_backdated` 也在。
- 這些子指令與旗標的寫法同程式一致:
  - `--signer`、`--expires-on`、`--out`、`--key <principal>=<公鑰檔>`
  - `--security-only`
  - `security list` 的 `--all`、`--questions`、`--plan`、`--limit`
- d17 的行為與程式一致:stdin 與 stdout 都要是 tty、要手打確認碼、所有型別都適用、`sk-` 只提醒。
- 工具清單的檔案格式(兩個頂層鍵、必填鍵、類別 id、覆蓋證明值)與程式一致,改名算變弱也與 `_secev_tool_freeze` 一致。
- 主線只讀主線 tip 版設定、只收 `refs/remotes/`,以及「全部候選取歷史最長分岔點」,都和 `_secev_mainline*` 一致。
- 掛鉤第五句 `資安護欄的證據不合格(或判不清)` 與 `_PPC_KIND_SENTENCES`、計劃正本逐字相同;`_sec_done` 快取只判一次、舊版 lumos 提醒一句,皆與註解和文件一致。
- 其餘幾項也對得上:
  - `junit()` 拒 DTD 只在 `NoDtdTreeBuilder`,丟 `JUnitRejected("report_unparseable")`。
  - bundle 指紋與 `test_quality.py` 的 sha256 相符。
  - CI 的 `security_tag` 工作存在。
  - 兩篇計劃的條款數 63 與 22 屬實。
  - golden 檔存在且 `source_commit` 為 d42840cf。
- 7 篇筆記 `lumos lint` 全為 0 問題。
- 新增的 REVISIT 格式合規,CHANGELOG 的「不留未發布區塊」也屬實。

## 三問
1. 原問題的修復效果:文件面的修補多數有程式與測試佐證,見「已驗主張」。這裡只驗到文件與程式一致,沒有重跑修前版做行為對照。
2. 修補處的相鄰路徑:正常與錯誤路徑都沒有發現被破壞,但只跑了上述三個子集;全套與 anchor 簽名未驗。
3. 新發現:5 條都是文件層的不一致,在修前版與修後版都不會讓測試紅,也不影響閘門判定。

最嚴重 severity:minor,blocking 共 0 條。
