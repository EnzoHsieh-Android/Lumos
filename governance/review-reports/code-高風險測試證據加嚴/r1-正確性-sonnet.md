severity: major

我逐 hunk 讀完整份 diff,也跑了相關測試(`-k expected`、`push_check_expected`、`spec_gate` 共 410 支、`door_rule_version`、`nogo_skip_logic`、`gov_stats`、`signoff`、`confirm_tty`),全部綠。沒有找到會做出錯行為的實作缺陷。三條 finding 都是測試抓不住改壞。mutation 實驗都在 `/tmp/lumos-seat-work/code-高風險測試證據加嚴/正確性-sonnet/` 的副本做,完成後已刪。

## Findings

### 1. 推送前「這次改到計劃檔的 done 計劃」要簽,沒有任何測試守
severity: major
blocking: 是
引句:「if n is not None and _live(prel, n):」
file: `scripts/lumos:16548`(`_spec_gate_push_scan` 末段新迴圈);測試端 `scripts/test_lumos.py` 的 `t_push_check_expected_unsigned` 與 `t_push_check_expected_scope`

- **被保護的行為**:驗收條款 S7 明寫「推送前規格閘挑到的 doing 計劃(或這次改到計劃檔本身的 done 計劃)是要簽的計劃,…應回 1」。
- **測試缺口**:S7 全程用 `status: doing`。S9 只測「done 而且這次沒改到計劃檔 → 不擋」。「done 且被改到 → 要擋」那一格沒有任何測試。
- **改壞的具體做法**:把新迴圈的條件換成只認 doing:
  ```python
  if n is not None and str(n.fields.get('status')) == 'doing':
  ```
- **結果**:`python3.14 scripts/test_lumos.py -k push_check_expected` 仍是 20 passed, 0 failed。
- **後果**:風險高計劃在同一次推送裡從 doing 改成 done(或完成後才碰它),不用簽核就能推出去。

### 2. 擋下標題「原因混雜」的第二種開頭沒有測試
severity: minor
blocking: 否
引句:「return f"{len(bad)} 份計劃沒過(風險低計劃的留痕與測試、風險高計劃的預期值表簽核):"」
file: `scripts/lumos:16578` 附近(`_spec_gate_push_bad_head`)

- **現況**:`[帳]` 開頭的分支由 S11 守住(它斷言不出現「風險低計劃沒過」)。預期值表開頭的分支沒有任何斷言。
- **改壞的具體做法**:刪掉整個 `_EXPECTED_PUSH_TAG` 分支,預期值表原因會退回「N 份風險低計劃沒過」。
- **結果**:`-k push_check_expected`(20 passed)、`-k spec_gate`、`-k expected_`(112 passed)全綠。
- **為什麼只算 minor**:驗收條款沒有規定這個標題字面。
- **旁證**:三種標題實際上不會「混雜」。帳讀不到時 `_spec_gate_push_scan` 先回 `[帳]` 訊息就返回了,跑不到預期值表迴圈。`_expected_push_one` 自己那條 `治理帳讀不到` 備援只在 `_spec_gate_gov_index` 與 `_gov_vc_gate_events` 兩次讀帳結果不同時才會走到,實務上走不到。

### 3. 存進治理帳的表指紋算法沒有固定值的測試
severity: minor
blocking: 否
引句:「return _hl.sha256(_j.dumps(data, ensure_ascii=False).encode("utf-8")).hexdigest()」
file: `scripts/lumos:14357` 附近(`_expected_table_sha`)

- **測試現況**:S3、S5、S7 都用同一支函式算出預期值,或只比「相同或不同」。
- **改壞的具體做法**:改成 `ensure_ascii=True, separators=(",",":")`。
- **結果**:`-k expected_`(112 passed)、`-k push_check_expected`(20 passed)、`-k signoff_expected`(14 passed)全綠。
- **後果**:指紋是寫進版控帳、之後要重算比對的持久值。算法一變,升版後所有已簽的表都變成「還沒簽」,測試卻不會紅。
- **缺的東西**:一組固定輸入對固定 sha 的釘子,或在事件裡帶算法版本。
- **為什麼不算 major**:驗收條款沒有要求跨版本相容。

## 其餘鏡頭結論

**邊界、例外、新舊互讀:沒找到會壞的輸入。**
- 生效日當天與前一天:`day < _expected_since()` 用「不早於」判斷,S10 守住當天。
- `created` 缺或格式壞:忽略它,只看 git 日期;兩個都沒有就當生效日之後(設計如此,且文件有寫)。
- 表格只有表頭、含 `\|`、全形條款欄、NFC/NFD、多列同條款:逐項走過,行為都合規格。
- 帳裡同 sha 但別份計劃、別種事件、別的閘:S7 三種都有測。
- 非物件行、`plan` 或 `table_sha` 型別錯:S11 守住。
- 舊帳沒有 expected-signed 事件:判沒簽,對生效日前的計劃不影響。
- `_GOV_FIELD_TYPES` 新增 `plan`、`table_sha`、`origin` 為字串型:我沒找到既有事件用非字串寫這三個欄位。
- 簽核寫到一半被中斷:`_ledger_tail_needs_newline` 補換行,讀端跳過壞行,救法訊息的指令可用。
- 計劃改名後要重簽:`天花板三` 已明寫。
- rebase 或壓提交讓第一次進 git 的日期變新、舊計劃被當新計劃:`天花板五` 已明寫「寧可多查」,我不另標。
- 簽核和推送前檢查讀的是工作目錄、不是提交內容:`天花板一` 已明寫。

**其他守衛抓錯**:我另試了幾個合理的改壞,測試都會紅。
- 改壞後 S10 會紅:`max` 改 `min`、淺複製誤用 git 日期、改名追蹤失效。
- 改壞後 S5 會紅:簽核逾時 300 秒。
- 改壞後 S6 會紅:`--by`、`--ref` 互斥。
- 改壞後 S7 會紅:plan 比對、gate 比對、kind 比對。
- 改壞後 S8 會紅:AI 簽的提示。

**版本號**:`_NOGO_SKIP_LOGIC_VERSION` 8、`_DOOR_RULE_VERSION` 16 與兩個釘子測試(`t_nogo_skip_logic_version_pin`、`t_door_rule_version_pin`)一致,都綠。

## pitfalls manifest(55 條)
全是本 repo 既有寫法的風格或雜訊,沒有真隱患。repo 沒有 ruff 設定檔,整支測試檔本來就有 3903 條。

| 規則 | 條數 | 判斷 |
|---|---|---|
| RUF005 | 31 | 測試裡 list 串接,風格 |
| E702 | 17 | 分號連寫,跟既有測試同寫法 |
| RUF059 | 5 | 解包後沒用到的變數 |
| RUF001 | 2 | 刻意測全形條款欄 `Ｓ３`,是誤報 |

## 圖譜鏡頭(六篇必答)
- **Systems/規格閘**:已寫入預期值表的 WHY、PITFALL。第 19、39 行的 KEY「風險高只印不擋紅綠、回退節照擋」對紅綠仍成立,表格檢查是另一道,不衝突。`-k spec_gate` 410 支全綠。
- **Systems/bound-tests-gate**:★INVARIANT★ 管 code-loop 對固定席合約綁定測試的逐支真跑。本 diff 沒碰 code-loop 與 impact,不影響。
- **Systems/reversibility-governance-ledger**:新事件是追加寫入,且不在 `_GOV_LOCAL_PAIRS`,走版控帳,與該節點「治理帳追加、唯讀彙整」一致。不影響。
- **Systems/lumos-cli-read**:該節點的 ★INVARIANT★ 在 `search`、`contracts` 等唯讀指令,本 diff 沒碰。不影響。
- **Projects/規格落成可驗收條件_計劃**:條款句式與回退節判法沒變,`_h2_section_lines` 多的是選用參數。不影響。
- **Projects/雙向門放行_計劃**:風險低留痕路徑沒動,`door_now` 只在重判後多存一份。唯一的相互作用是 `_expected_requirement` 對所有 live 候選多做一次門判定,測試 `t_spec_gate_push_scan_reads_ledger_once` 仍綠。不影響。
- **其餘固定席**:名單上其他節點我沒有逐篇細讀。

總結:全份最高 major
