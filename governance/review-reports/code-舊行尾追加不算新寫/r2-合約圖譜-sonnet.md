severity: major

我只在臨時目錄複製的 repo 裡做改壞實驗,沒動原 repo。本輪新改的測試有幾條已經不會因配對壞掉而變紅,另有幾處筆記內部對不上。

**G1 「現況描述沒寫來源永遠不扣」之後,多條配對測試變成假綠**
severity: major
blocking: 是 — 計劃 S1、S6、S7、S8、S9、S11、S12、S13、S38 綁的測試,配對壞掉時不會紅,違反 Systems/測試假綠形態的合約(前置斷言證明被測路徑真的走到)。
引句:「check("①S6:舊行還在、另一處新寫舊句加括號:照整行查", rc == 1 and "現況描述沒寫來源" in out, out[-600:])」
1. 成因:r2 把這些測試的括號改成 `_TAIL_FIX_NOSRC`,斷言只剩「報了沒寫來源」。這條規則現在永遠不扣,所以配對成不成都會報。
2. 另一半:原本期望「照配、不擋」的用例改帶 `[來源:人工]`(`_TAIL_FIX`)。括號帶了來源,整行本來就沒違規,沒配對也是 rc 0。
3. 改壞實驗一:把 `_ns_is_tail_append` 改成一開頭 `return True`,配對規則全放寬。
   - 指令:`python3.14 scripts/test_lumos.py -k <名稱>`。
   - 輸出:`t_ns_append_bypass` 3 passed 0 failed。
   - 輸出:`t_ns_append_edits` 4 passed 0 failed。
   - 輸出:`t_ns_append_context` 4 passed 0 failed。
   - 輸出:`t_ns_append_rename_binary` 1 passed 0 failed。
   - 輸出:`t_ns_append_push_range` 10 passed 0 failed。
   - 只有靠行號引用判的 `t_ns_append_limits` 變紅(5 failed)。
4. 改壞實驗二:讓 `_notelines_append_pairs` 一進來就 `return {}, None`,等於整個不配對。
   - `t_ns_append_old_line`(S1 主測試)5 passed 0 failed。
   - `t_ns_append_eol`(S11)2 passed 0 failed。
5. `t_ns_append_push_range` 的 S38 ④到⑧是另一種假綠。
   - 起點換成 `_tail_repo(summary=_TAIL_OLD_REF)`,但這幾步仍寫 `_TAIL_OLD + …`,和已推上去的那行文字根本不同,不是「改寫括號」。
   - ④⑤⑧不帶來源,恆擋。
   - ⑥⑦帶來源,恆過。
6. 預期:這些條款的測試在配對過寬或不配對時要紅,每條都該有前置斷言(例如先證明用 REF 版舊行確實配到),且「整行查」那組要用仍會被扣的規則(行號引用)當探針。
7. 對照:`t_ns_append_nfc_clash` 這條沒問題。把 `clash = _ns_append_nfc_clash(d)` 改成 `clash = set()` 後,③④都紅。

**G2 Systems/筆記內容審的 WHY 與計劃、程式不一致**
severity: minor
blocking: 否 — 筆記的描述性錯誤,不影響執行,但下個 session 會被誤導。
引句:「能略過的=check 也判沒涵蓋的(同一個算法;代碼審 r1 邊界席」
1. 計劃〈做法〉4、S45 和 `cmd_note_audit_skip`(`scripts/lumos:30577`)現在都是 skip 比範圍,算法和 check 相同。
2. `docs/lumos-toolchain-knowledge/Systems/筆記內容審.md:37` 的 WHY 還寫「doctor 與 skip 的「判過了」不比範圍(同編號各範圍取最重)」。
3. 這篇 r2 沒改。只有「能不能略過」裡判重的那一步仍不比範圍,其餘已改。

**G3 否定提醒量測的「跳過 relaxed 帳 pairs 記的行」做不到**
severity: minor
blocking: 否 — 影響的是第 8 週人工抽樣的口徑,抽樣只有 30 行。
引句:「2026-10-03 起例外:舊行尾補括號的行正式工具只看補上的那段,量測程式不分,重產時跳過 relaxed 帳 `pairs` 記的行」
1. 否定提醒只在提交前算。計劃〈做法〉3 說推送模式不算提醒。
2. `relaxed` 帳只在推送時記,只記有違規被減掉的行。〈做法〉5 寫明「提交前不記」。
3. 所以被放寬掉提醒的那些行不會出現在 `pairs`,照這句操作會跳不掉。
4. 影響 `否定現況句配回頭條件_計劃.md` 〈做法〉7 的步驟 3 和 S8 的例外句,對應 REVISIT 2026-11-25。
5. 要嘛改成別的辨認法,要嘛把這個例外寫成「量測程式會多算,抽樣時人工剔除」。

**G4 派工詞「第 2 版」內容變了,版本沒升,驗收樣本也換過**
severity: minor
blocking: 否 — 第 2 版還沒推出去,沒有舊清單會被誤判,是記載口徑問題。
引句:「(m._NOTE_AUDIT_PROMPT_VERSION, h) == (2, "416758fba6195791098cdacebcdebe61185aede608541608d6b376aad551125e"),」
1. 只改了雜湊,版本號仍是 2。`scripts/lumos:29591` 的註解寫「範本檔改一個字就升版」,S37 的設計也是這個意思。
2. 計劃〈做法〉4 寫「固定 9 句」,實際是 B 組沒過後換掉樣本再重跑。
3. 沒過的那次有寫(7/9「沒過」),我沒看到把沒過寫成過。
4. 但「兩組門檻都過」是靠換掉樣本的那次。樣本不進 repo,無法重現。
5. 筆記內容審_計劃新加的那一列只有回歸組 68 句的數字(55/0),補括號組的結果在表外的條列。
6. 接線守門讀表時看不到補括號組。
7. 建議在表裡加一欄或一列,並註明「第一次未過、換 B 組後重跑」。

**G5 新測試有牆鐘門檻,會漂**
severity: minor
blocking: 否 — 負載高的機器上可能偶發紅,目前沒看到失敗。
引句:「check("①單一改動段十萬行:一秒內讀完、行數對", dt < 1 and len(got.get("d/n.md", [])) == n, (dt, len(got.get("d/n.md", []))))」
1. `t_ns_append_r1_minor_folds` ①的門檻是 `dt < 1`。
2. `t_gate_event_fit_bisect` ②的門檻是 `dt < 3`。
3. 都是牆鐘時間。S44、S46 的條款也把「3 秒內」「一秒內」寫成驗收。
4. 較穩的做法是改成比較「二分 vs 逐筆」的相對次數,或呼叫次數上限。

**逐項核對結果**
- 計劃抽查 12 條,對得上程式:
  - 做法 1 的常數:`_NS_APPEND_MAX_TAIL`=300、`_NS_APPEND_MAX_LINE`=2000、`_NS_APPEND_BASE_MAX_BYTES`=524288。
  - 做法 1 的常數:`_NS_APPEND_MAX_FILES`=200、`_NS_APPEND_MAX_PAIRS`=20000。
  - `_gate_event_fit` 簽名含 `nodes_cap`。
  - `LUMOS_PUSH_ATTEMPT` 去重。
  - `_NS_FRAG_KEY_RULES` 和 `_NS_REVISIT_RULES`。
  - tail 要 16 碼十六進位。
  - skip 與 check 同一算法。
  - 現況描述沒寫來源永遠不扣(`_ns_append_subtract`)。
  - 條款 S42 到 S46 綁的測試都存在。
- 「現況描述沒寫來源永遠不扣」的說法在以下地方一致:
  - 舊行尾追加不算新寫_計劃的 WHY、做法 2、天花板 1、S1。
  - 筆記內容閘的 WHY。
  - skill 子檔 `03-寫回圖譜.md`。
  - `scripts/lumos` 的 docstring。
  - 筆記形狀擋_計劃 S7 的例外句也一致。
- 這次碰到的 7 篇筆記整篇的 `[test:]`:我逐篇掃過,全部指得到 `scripts/test_lumos.py` 裡的 `def t_*`。S39 是 `[manual:]`,沒問題。
- monkeypatch:`t_ns_append_failure`、`t_note_audit_append_failure`、`t_ns_append_caps` 都在 finally 還原。
- repo 根留檔:新測試沒有。`t_gate_event_fit_bisect` 用 `tempfile.mkdtemp` 沒清掉,但不在 repo 內。
- 前置斷言:`t_ns_append_caps`、`t_note_audit_append_failure` 有,`t_ns_append_nfc_clash` 有。缺的是 G1 那批。
- 新寫或改寫的摘要行都遵守寫筆記規則,是 WHY 加出處,沒有程式碼推得出的現況句。
- 筆記內容審_計劃新加那一列:數字內部一致(55=54+1、13=8+5、回歸組 55 與 0),沒有把沒過的那一次寫成過(7/9 明寫「沒過,不改答案」)。數字本身是 repo 外實驗,無法對。

**固定席節點**
- reversibility-governance-ledger:只改摘要文字,與 `_gate_event_fit` 現況相符,不影響。
- lumos-cli-read、guard-kill、授權與歸屬、pitfalls-code-loop:本 diff 沒碰各自的合約行,不影響。
- bound-tests-gate、design-loop:涉及的 `[test:]` 都真實存在。新增條款 S42 到 S46 都綁了測試,S39 是 manual,不影響。
- 測試假綠形態:受影響,見 G1。

最高嚴重度 major,blocking 1 條
