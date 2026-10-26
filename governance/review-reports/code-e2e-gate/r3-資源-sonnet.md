severity: major

以下是資源鏡頭的審查結果,實驗用的臨時目錄已用字面絕對路徑刪除。圖譜鏡頭沒有附固定席節點,我沒有補算。

## Findings

**1. 歸屬查表改用前綴後,路徑一深就變二次方,而且整個迴圈幾乎不查截止時間**

severity: major
blocking: 是

引句:「for i in range(1, len(parts) + 1):」
file: `scripts/lumos:41635-41645`(`_e2e_owners`)、`scripts/lumos:41494-41510`(`_e2e_gate_owners`,只在 `i % 1000 == 0` 查截止時間)

- 失敗場景:被推送提交帶很深的目錄。`_e2e_owners` 對每一層前綴都 `"/".join(parts[:i])`,每支檔的成本是深度的平方。
- 迴圈每 1000 支檔才查一次截止時間,所以檔數少於 1000 時等於沒查。
- 單檔深 10 萬層(`depth 100000 5 files`)的量測是 5 支檔 202 秒。
- 重現:用 `git fast-import` 在 `app/src/main/` 下造 150 支檔,路徑深 10000 層,跑 `_e2e_gate_evaluate`。
  - 修前(ce46398a):0.7 秒,擋「沒有查證紀錄」。
  - 修後(bf9dac49):64.8 秒。
- 走 `lumos android-e2e check` 則是 71.1 秒,結果被改講成「判定超過 60 秒還沒算完」。
- 修前的 `any(_e2e_under(f, x) for x in paths)` 只跟 paths 條數成正比,沒有這個深度平方。
- 歸因:有證據的修復回歸。修前 0.7 秒、修後 64.8 秒,同一輸入。

**2. 功能對照表的 flows 去重是二次方,沒有截止時間**

severity: major
blocking: 是

引句:「dup = sorted({n for n in names if names.count(n) > 1})」
file: `scripts/lumos:40380`(`_e2e_paths_err`,被 `_e2e_gate_fps` 對被推送提交的 e2e 段呼叫)

- 失敗場景:被推送提交的 e2e 段 flows 很多。這一段是純 Python,不看 60 秒預算。
- 直接量 `_e2e_paths_err`:3 萬條 flow 要 10.6 秒。
- 走完整 check:

| flows 條數 | 設定檔大小 | check 耗時 |
|---|---|---|
| 2 萬 | 0.47MB | 5.4 秒 |
| 6 萬 | 1.4MB | 50.1 秒 |

- 外推 10 萬條約 2 分鐘,16MB 的單檔上限內可以更多。
- 修前、修後這一行完全一樣,所以修補沒有動到它。
- 歸因:有證據的原有漏查。這個二次方在基底 0701350 就有,但這輪修的是「大輸入吃光預算」,它同一個類型卻漏掉。

**3. 判定改到的檔是否在範圍內,每支檔掃一遍 flows 和 app_dirs,與修補的目標同形**

severity: minor
blocking: 否

引句:「files = [f for f in _nodehome_split_z(raw) if _e2e_scope_hit(f, e2e, dirs)[1]]」
file: `scripts/lumos:41480`(`_e2e_gate_need`)、`scripts/lumos:40611-40618`(`_e2e_scope_hit` 裡的 `any(_e2e_under(p, m) for m in mats)`)

- 失敗場景:一次改很多檔,設定檔裡 flows 很多。
- 純函式量測:2000 條 flow 配 10 萬支範圍外的檔要 14.1 秒;1 萬條要 69.8 秒。
- 完整重現:主線設定 6000 條 flow,分支改 1 支 App 檔加 10 萬支 docs 檔。
  - 完整 check 要 46.8 秒。
  - 同樣條件只有 50 條 flow 是 1.8 秒。
- 這個迴圈沒查截止時間。條數要到幾千才有感,所以只給 minor。
- 歸因:有證據的原有漏查。修補只改了 owners 那一段,同形的 scope 這段沒動。

**4. `--ack` 把「沒讀到的份數」丟掉,和 [S41] 對不上**

severity: minor
blocking: 否

引句:「pend = dict(_e2e_ai_pending_all(root, budget=60)[0])」
file: `scripts/lumos:41864-41870`(`_e2e_ack_targets`)

- 失敗場景:紀錄超過 500 份。`--ack --all` 只標前 500 份,卻回 rc 0,只印「標好了 500 份」,完全不提還有幾份沒讀。
- 重現:造 503 份各含一筆 AI 放行,把 `_confirm_tty` 換成 True 後呼叫 `_e2e_waive_ack`,輸出就只有「標好了 500 份」。
- [S41] 白紙黑字寫 doctor、`waive --ack` 與開場提示三處「沒讀到的份數講出來」。doctor 和掛鉤有講,只有 `--ack` 沒有。
- 修前版本根本沒有份數上限,這輪修補才引入上限,但 `--ack` 這邊漏接。
- 歸因:有證據的修復回歸(修補引入的上限,沒有接到 `--ack` 的輸出)。

**5. 開場掛鉤的 3 秒是固定值,沒從外層 10 秒扣已耗時間**

severity: minor
blocking: 否

引句:「end = _t.monotonic() + _E2E_RECORD_SCAN_SEC」
file: `scripts/hooks/claude/lumos-entry-hook.py:325`(`_e2e_ai_line`),對照 `lumos-entry-hook.py:176`(`_inner_budget`)

- 失敗場景:`enforcement` 卡住時,先吃滿它自己的 7 秒內層預算,再掃 3 秒紀錄。
- 重現:用假的可信 lumos(sleep 30)加 500 份各 1.8MB 的紀錄跑掛鉤,整支 10.07 秒。外層註冊表寫的是 10 秒,超過就被砍掉,連核心提醒也一起沒了。
- 3 秒沒有走 `_inner_budget` 扣已耗時間,和同檔其他段的做法不一致。
- 只有 enforcement 卡住且紀錄很多這兩件事同時發生才會撞到。
- 歸因:有證據的原有漏查。修前的掛鉤完全沒有時間上限,修補補了上限,但沒和 `_inner_budget` 連動。

**6. 單份紀錄寫回沒有大小上限**

severity: minor
blocking: 否

引句:「rec, err = _e2e_load_json(p, scrub=False)」
file: `scripts/lumos:40932`(`_e2e_record_update`,`waive <fp>` 與 `--ack` 共用)

- 失敗場景:掃描端把超過 2MB 的紀錄略過,閘門讀提交樹時也有 16MB 上限,但 `waive <指紋>` 寫回時整份讀進來,沒有檢查大小。
- 量測:一份 160MB 的紀錄做一次 `_e2e_record_update`,耗時 37.9 秒,峰值記憶體約 4.8GB。
- 要有人刻意對那個指紋放行才會走到,所以 minor。
- 歸因:有證據的原有漏查,修補沒有碰這個函式。

**7. 提交樹裡的 JSON 巢狀太深時,擋下的訊息講成「內部出錯」**

severity: minor
blocking: 否

引句:「except (ValueError, UnicodeDecodeError):」
file: `scripts/lumos:41386`(`_e2e_tree_json`)

- 失敗場景:被推送提交的 macrobench.json 巢狀 100 萬層。`RecursionError` 不是 `ValueError`,跳到最外層的 `except Exception`,擋下訊息變成「判定內部出錯(RecursionError…)」,記的是 `evaluation_error`,而不是「讀不懂」。
- 重現:0.9 秒,仍然擋下,走的是 fail-closed,逃生用的環境變數也有效。
- 同檔的 `_e2e_load_json` 已經把 `RecursionError` 一起接住,這裡漏了。
- 歸因:有證據的原有漏查,修前修後相同。

## 子程序殘留與預算檢查

- git 呼叫一律走 `subprocess.run(timeout=)`,逾時或 Ctrl-C 都會收掉子程序。沒找到殘留孤兒。
- `--ack` 寫入量測:每份 1.7MB 的紀錄約 0.07 秒、峰值記憶體約 61MB,500 份約 37 秒。這部分沒問題。
- doctor 與掛鉤的紀錄掃描:500 份各 1.8MB 時 3 秒預算有生效,掛鉤單獨跑約 4 秒。

## 三問

1. **原問題的修復效果有何行為證據?**
   - 「十萬支檔對上萬條路徑」的線性掃描確實拿掉了:100 萬檔(原文寫 10 萬)、20 條功能的 owners 迴圈只要 0.4 秒。
   - 掛鉤與 doctor 的 3 秒上限、份數 500、單份 2MB 都有實測生效。
2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
   - 正常路徑成立。
   - 相鄰路徑出了問題:owners 前綴迴圈引入深度二次方(finding 1);`--ack` 沒有接上份數輸出(finding 4);掛鉤的 3 秒沒和外層連動(finding 5);同形的 scope 與 flows 去重仍是二次方(finding 2、3)。
3. **新發現在修前、修後各是什麼結果?**

| 發現 | 修前 | 修後 |
|---|---|---|
| 1(深路徑) | 0.7 秒 | 64.8 秒,被誤報成逾時 |
| 2(flows 去重) | 6 萬條要 50 秒 | 同上,沒改 |
| 3(scope 掃描) | 6000 條 flow 配 10 萬檔要 46.8 秒 | 同上,沒改 |
| 4(`--ack`) | 沒有上限也沒有份數 | 有上限,沒講份數 |
| 5(掛鉤) | 沒有時間上限 | 上限 3 秒,疊加後仍達 10.07 秒 |
| 6、7 | 無差異 | 無差異 |

總結:最高等級 major,擋實作的 2 條(finding 1、finding 2)。
