severity: minor

我沒找到會讓資料壞掉或讓閘放過阻塞題的洞。下面 7 條都是 minor,全部不擋。我實跑過 `python3.14 scripts/test_lumos.py -k qfm`,100 passed、0 failed。後端計劃搬遷後的 `lumos lint` 是 0 問題,逐題對照舊正文也一致(S7)。

我的實驗和重現腳本都在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/正確性-sonnet/`,用 `fx.py` 建臨時庫。

1. 空字串引號值通過嚴格讀法。
   - 重現:`text: ""` 或 `class: ''`(`class: "   "` 也一樣)。規格閘照常擋這題,印出 `• Q1 [需求/待人] ` 後面是空的。`lumos lint` 一個字都不報。
   - 路徑:`_strict_scalar` 在 `v[0]` 是引號時直接 `return inner, None`,沒查 `inner` 是否為空。`pq_parse` 的必有鍵檢查只看 `k not in it`。
   - 結果:計劃寫明 `text`、`class` 必有且非空,但手寫的空字串不會被擋。`question-add` 和 `question-set` 能擋空值,所以只有手改或 Obsidian 改過的檔會踩到。
severity: minor
   - blocking: 否
   - 引句:「            return inner, None」
   - file: `scripts/lumos:6927`

2. 超大題號會讓 `--stage` 崩潰。
   - 重現:手寫 `id: Q` 加 5000 個 9。`_PQ_ID_RE` 接受,`pq_parse` 回 `errs=[]`。
   - 結果一:`pitfalls <計劃> --stage 需求` 丟出未捕捉的 `ValueError: Exceeds the limit (4300 digits)`,印 traceback,rc=1。
   - 結果二:`question-add` 回「擋下:Exceeds the limit…」,訊息莫名其妙,只能用編輯器救。
   - 規格閘和 lint 仍判定可讀,四處對同一份清單的判定不一致。
severity: minor
   - blocking: 否
   - 引句:「return (not q.get("blocking"), not q.get("irreversible"), int(q["id"][1:]))」
   - file: `scripts/lumos:7144`

3. 「結了」判定對題數是平方級。
   - `_pq_settled` 每題都走 `_pq_decision_state`,後者每次重新 `parse_decisions(fm)` 掃整份開頭欄位。
   - 實測:全部「已決並指到 `#d1`」的題,`decisions:` 放在題後面。500 題 spec-gate 1.6 秒;1000 題 4.4 秒;2000 題 15.1 秒(lint 同樣 15.0 秒)。每翻一倍約 3.4 倍。
   - 真實計劃只有個位數到幾十題,所以只是遇到大清單才慢。
severity: minor
   - blocking: 否
   - 引句:「    for d in parse_decisions(fm):」
   - file: `scripts/lumos:7066`

4. 拼錯欄位名的偵測,遇到頂格長空白行會平方級回溯。
   - `re.sub(r"""^["']|["']?\s*:.*$""", ...)` 的第二個分支沒有錨點。
   - 實測:頂格一行 `"x" + 空白×N + "y"`,沒有冒號,`pq_parse` 的耗時是:

     | N | 耗時 |
     |---|---|
     | 10000 | 0.66 秒 |
     | 20000 | 1.9 秒 |
     | 40000 | 6.5 秒 |

   - 每份筆記的 lint 都會跑這條,另外 `_pq_push_remind` 每個計劃跑兩次。計劃〈緣起〉把這類平方級回溯當成原做法被撤出的原因之一。
   - 觸發條件很窄:要頂格、整行沒有冒號、有幾萬個連續空白。
severity: minor
   - blocking: 否
   - 引句:「elif re.sub(r"""^["']|["']?\s*:.*$""", "", s).lower().startswith(key[:-1].lower()):」
   - file: `scripts/lumos:6943`

5. 題目清單後面緊接的頂格鍵,如果名字有空格或點,整份清單被誤判讀不懂。
   - 重現:`pending_questions` 的題目後面接 `related notes: x`(Obsidian 允許屬性名帶空格)或 `a.b: x`。`pq_parse` 回錯誤「這行頂格寫了 'related notes: x',不是鍵也不是題目」。
   - 結果:規格閘回 1「無法判定」,lint 也報。
   - 計劃文法寫的是「到下一個頂格、不是空行也不是註解的行為止」,實作卻只認 `^["']?[\w-]+["']?\s*:` 才收尾。訊息說它「不是鍵」,是錯的。加引號也救不了,因為引號內不允許空格。
severity: minor
   - blocking: 否
   - 引句:「            if _PQ_TOP_KEY_RE.match(raw):」
   - file: `scripts/lumos:6960`

6. 推送前提醒會在計劃檔被刪掉時誤報「題號不見了」。
   - 重現:在臨時 repo 提交一份帶 Q1 的計劃,再刪檔提交,跑 `spec-gate --push-check HEAD~1..HEAD`。印出「Q1 在 HEAD~1 那一版有、這一版不見了(題目不刪,改成延後或已決…)」。rc 仍是 0。
   - 原因:`git show head:path` 對已刪的檔回 `""`,`nq` 空,舊版每題都算「不見」。
   - 搬檔用 `git diff --name-only` 只會列新路徑,所以不受影響。只有整份刪除或歸檔會踩到。
severity: minor
   - blocking: 否
   - 引句:「            if q["id"] not in now:」
   - file: `scripts/lumos:8019`

7. 測試判準與文件的小問題,合併一條。
   - `t_qfm_absent_field_unchanged` 的 ① 只比 n0、n1、n2 三份輸出彼此相等。如果新碼讓「所有計劃」的規格閘或 `--stage` 輸出都變了,三份仍相等,測試不會紅。② 只斷言 JSON 的鍵。這跟它宣稱的「跟現行相同」不同,沒有和程式改前的輸出對照。
   - 引句:「    check("① 三種寫法的規格閘、lint、--stage 結果相同", outs["n0"] == outs["n1"] == outs["n2"], outs)」
   - file: `scripts/test_lumos.py:56329`
   - `t_qfm_strict_parse_fail_closed` 實跑 77.7 秒,超時上限 180 秒,餘裕只有 2 倍。機器忙時有假紅風險。
   - `_pq_commit` 裡「寫完讀回來不一樣」的 `RuntimeError` 沒有任何測試走得到。
   - 〈順手處理〉第一條仍寫「重做時改成不帶待決問題縮寫的名字」,但程式和〈做法〉都繼續用 `PQ_STAGES`。`_qo_plan` 的 `decisions` 參數也仍沒人傳。
   - 引句:「新的題目欄位會共用它,重做時改成不帶待決問題縮寫的名字(代碼審 r4 架構席)」
severity: minor
   - blocking: 否

**圖譜鏡頭(四篇必答)**

- `Systems/lumos-cli-read.md`(★note_lint.gate 那條 RULE):沒有牴觸。新規則 `_nl_rule_pending_questions` 掛在 `_lint_new_rules`,所以擋不擋照 `note_lint.gate`,原有錯誤規則不受影響;本 repo 開關是 on,所以讀不懂的清單會擋提交。
  - 該 RULE 行(`lumos-cli-read.md:22`)的新規則清單只列到 `lands_in`,沒有 `pending_questions`;新段落另寫在檔案後段。RULE 帶 `[confirmed:2026-09-25]`,仍有效力,清單缺一條會誤導下個會談。影響小,補一句即可。
  - 本鏡頭 findings 4 和 5 的代價也落在這條規則上,因為它對全圖譜每篇筆記都跑。
- `Systems/lumos-cli-write.md`(寫入原語與 `atomic_write_verify` 不變式):原子換名、拒 BOM/CRLF、可重入鎖都符合。
  - 但兩支指令傳 `lambda _f: True` 當 `expected_check`,「re-parse 斷言該 key 寫成目標值」這一半由記憶體裡的 `pq_parse(new_fm)` 前置代替,沒有真的讀回檔案。我查過寫入文字就是 `"\n".join` 那份清單,所以實質等價。不變式的字面說法需要註明例外。
  - 第 114 行「其餘六個…走 `atomic_write_verify`」現在實際是八個,屬計數陳舊。
- `Systems/規格閘.md`:新前段在判門後、條款前提早回 1,不經 `_spec_gate_record`,所以被擋時不留痕,這點對。「管到的檔」那段沒列 `_spec_gate_pending`、`_pq_push_remind`,屬文件缺漏,不影響行為。推送前路徑只提醒,不影響風險低計劃的留痕判定,與設計一致。
- `Systems/pitfalls-code-loop.md`:`--stage` 新增「清單無法判定回 2」和 JSON 多鍵。該篇段落末句「階段寫錯、或跟 `--diff` 一起用回 2」沒列新的回 2 情形,但測試 ④⑤ 有釘。`--diff` 模式不受影響。

其餘牽連的家只列名:bound-tests-gate、guard-kill、lumos-cli-lifecycle、授權與歸屬、測試假綠形態、design-loop、loop-convergence-recording、reversibility-governance-ledger、節點範圍與索引守衛。

最高等級 minor,blocking 0 條。
