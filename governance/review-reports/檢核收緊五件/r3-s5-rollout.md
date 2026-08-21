# r3 s5-rollout 對抗審計

角色鏡頭:本 PR 自我合規段(rollout self-compliance)、退場條件表可量測性、`_KNOWN_GATES` 遷移。
逐項對真碼/真資料查證(`scripts/lumos` ~15,100 行,`scripts/test_lumos.py`)。

---

## F1(blocker)— S1 測試 #7 對 `_strip_fences_text` 未閉合圍欄行為的宣稱與真碼相反

引句：「含未閉合圍欄不吞下文——沿 `_strip_fences_text` 既有測試語意」

文件宣稱:未閉合圍欄「不吞下文」,且這是 `_strip_fences_text` 的「既有測試語意」。

**與真碼相反**。`_strip_fences_text`(`scripts/lumos:1559-1566`)呼叫 `_visible_lines`
(`scripts/lumos:1535-1556`)——逐行 toggle:遇到一個 ``` 標記就切換 `in_fence`,不成對比對。
未閉合(奇數個 ``` )時,`in_fence` 從那行起翻 True 且**永不翻回**,之後所有行(直到 EOF)
一律被視為「圍欄內」而剝掉。直接執行驗證:

```
text = "正常文字 靠自律\n```\n未閉合圍欄開始\n這裡面有 honor-system\n沒有結尾也有 無機械守衛"
_strip_fences_text(text) → '正常文字 靠自律'
```

`honor-system`、`無機械守衛` 兩處承認句字面上都在「未閉合圍欄之後的真散文」,結果被整段吞掉。

而且這不是我這次臨時發現的行為,是**既有、經過測試釘死**的語意——恰與文件所稱的「既有測試
語意」矛盾:
- `t_unclosed_fence_never_leaks_into_graph_or_evidence`(`scripts/test_lumos.py:11989-12053`)
  的整個存在理由就是「未閉合圍欄之後的內容不得被當成可見文字處理」(wikilink 不進圖、測試名
  不進合約鏈)。
- `t_search_multiword_fallback_r1_three_majors` 的 fixture(`scripts/test_lumos.py:12174-12191`)
  明白寫著:「未閉合圍欄之後才出現「戊己」——主迴圈視為 code(搜不到)」,並且斷言單獨搜尋
  必須是 0 篇。

也就是說,「未閉合圍欄後的文字被吞掉、當作看不見」正是這支函式家族的**設計目的**(防幽靈連結
/假合約佐證),不是意外行為。v3 這條測試把因果寫反了:如果照文件字面實作測試 #7,執行時會
直接翻紅(因為真行為是吞、不是不吞);如果實作者為了讓測試綠燈而依樣改寫斷言去配合真行為,
後果是 Check A 在「文件前面某處不小心留了一個未閉合的 ``` 」的情境下,**之後全篇的承認句都
會被靜默豁免、完全不報**——這正是本輪 seat-common.txt 特別要求嚴打的「hard gate 靜默不觸發」
模式,且發生在 S1 這道「防止宣稱有守衛、實際沒有」的閘本身。

**正確規則**:測試 #7 應改為斷言「未閉合圍欄**之後**的內容視同圍欄內,不參與掃描(維持
`_strip_fences_text` 既有、被兩支獨立測試釘死的行為)」,而不是宣稱「不吞下文」。若要真正保護
「未閉合圍欄後的真散文」不被豁免,S1 需要額外機制(例如 doctor 對「奇數 ``` 」本身開一條獨立
硬檢查,逼人先修正圍欄),而不是假裝 `_strip_fences_text` 已經解決了這件事。

---

## F2(major)— r2 F6(`_KNOWN_GATES` 遷移撞既有漂移釘)在 v3 完全未處理,「審計修正紀錄」未列入

引句：「`_KNOWN_GATES` +4、`LIST_KEYS` +1;code-loop 留痕 JSON 新增選填鍵」

r2 輪(`governance/review-reports/檢核收緊五件/r2-s5-rollout.md:107-126`,標為 major、編號 F6)
已明確指出:`t_gov_stats_gate_drift`(`scripts/test_lumos.py:3047-3060`)有**兩道**斷言,不只
「新 gate 要在 `_KNOWN_GATES`」這一道——第二道釘死「全檔『`"gate":` 後面不是字串字面值』的位置
恰好 1 處」(`scripts/lumos:2994` 讀側 passthrough)。實測:

```
dyn = re.findall(r'"gate": [^"]', src)
len(dyn) == 1   # 目前唯一動態寫點是 cmd_gov 的讀側 passthrough(scripts/lumos:2994)
```

r2-F6 指出:文件全篇施工哲學是「別重造、抄既有骨架」(S1 自己就主張抄 `check_regen_provenance`
雙入口範本),若 4 個新 gate(check-a/ratchet/ratchet-ack/external-waived)的寫入點依此哲學收斂
成一個共用的「寫治理帳」helper(參數化 `gate` 名),helper 內部勢必寫成 `{"gate": gate, ...}`
(變數而非字面值)——一旦落地,`dyn` 從 1 變 2,直接打紅這條既有回歸釘;若反過來為了不撞釘而
堅持 4 處各自硬寫字面值字典,又跟文件自己的「別重造」哲學衝突。

**v3 對此毫無回應**。比對 v3「遷移」段全文——只講「`_KNOWN_GATES` +4、`LIST_KEYS` +1;code-loop
留痕 JSON 新增選填鍵(loop/range/tier/external_ok/waiver/class),舊讀者 `.get` 不炸;check 對
舊留痕...視同無效」,完全沒提到第二道「動態寫點恰 1 處」的釘,也沒有二選一的決定。「審計修正
紀錄」段落 r2 panel 的處置清單(S3 移到 push 檢查點、skip 破窗制、撤 `--no-loop`/`external-absent`、
S2 run 改定義、S1 加 H 型…)裡**沒有任何一條對應 F6**,也沒有被列進 minor 的「外家 6 條中 2 條
省略號不採信」名單。這是一件 r2 判定為 major、明確要求「兩條路二選一」的既有發現,在 v3(本
FINAL round 的送審版本)裡既未修、也未被記為「已折入」或「已否決」——是一項未收斂就消失的 r2
發現,直接影響「本 PR 怎麼過自己的規則」一節聲稱的「code-loop pass --loop 檢核收緊五件」能否
乾淨綠燈上線。

**正確規則**:遷移段須補一句明確裁定——4 個新 gate 的寫入點要嘛全部各自硬寫字面值字典(不共用
帶 `gate` 參數的 helper),要嘛連帶更新 `t_gov_stats_gate_drift` 的 `len(dyn) == 1` 為對應新值
並說明新增的動態寫點是什麼;測試策略段(22 條)也要補一條測到這件事。

---

## F3(major)— ratchet / ratchet-ack 的治理帳 dedup key 不含 `detail`,導致「去重筆數」在同 commit
同節點多源時會靜默漏計,且 ratchet-ack 寫入連「哪個 gate 被 ack」都沒留

引句：「append 時寫 `{"gate": "ratchet-ack", "kind": "acked", "hard": false, "nodes": [stem]}`」

`cmd_gov` 的去重鍵(`scripts/lumos:3030`):

```
k = (r["commit"], frozenset(r["nodes"]), r["gate"], r["kind"], r.get("token", ""))
```

不含 `detail`。ratchet 事件的設計本身用 `detail` 存「來源 gate」(文件:寫
`{"gate": "ratchet", "kind": "promoted", ..., "nodes": [stem], "detail": "<source gate>"}`)。
若同一個 commit(=同一次 doctor/CI run)裡,**同一個節點**的兩個不同來源 gate(例如文件自己
Growth-test 段提到「check-e1 現仍有 5 組 (gate,node) 超 20 次」——上線基線重算時,同節點若同時
被 check-s 與 check-e1 兩者都判定滿足連續 20 次)在同一 commit 各觸發一次促升,兩筆事件的
`(commit, nodes, gate="ratchet", kind="promoted", token="")` 五元組**完全相同**——只有
`detail` 不同,而 `detail` 不參與去重鍵。`cmd_gov` 的 dedup(`seen`/`k in seen`)會把第二筆
當「重複」直接丟棄,`_render_gov_stats` 的「去重後筆數」欄位因此**少算 1**。這正好是 S2 退場
條件表用來當分母/分子的那個數字(`ratchet`=0 判退場候選、`ratchet-ack`/`ratchet` ≥0.5 判門檻
重議),文件標榜「兩者同為 (gate,stem) 事件粒度,r2 s5-F3 尺度問題以「每鍵每 run 最多一筆」解」
——但「每鍵每 run 最多一筆」只保證**寫入端**不重複寫,沒有處理**讀取端**的 dedup key 把
「不同鍵、同 commit/同節點」的兩筆事件錯誤合併成一筆這件事,兩者是不同層次的問題,r2 s5-F3
的解法並未涵蓋這裡。

同一段落更直接的問題:ratchet-ack 的寫入 `{"gate": "ratchet-ack", "kind": "acked", "hard": false,
"nodes": [stem]}` **完全沒有 `detail` 欄**,對照 ratchet 促升事件自己都知道要用 `detail` 存
「來源 gate」——ratchet-ack 這行治理帳連「這次 ack 的是哪個 gate」都無從得知(除非另外去翻
`ratchet_acks` 這個 LIST 鍵本身,但那不是 `gov --stats`/`gov --full` 在讀的來源)。這使得
「ratchet-ack/ratchet ≥0.5」這個比例,分子端(ratchet-ack)在同 commit 同節點多鍵 ack 時**連
去重前的原始語意都分不清是哪一鍵**,遑論去重後可比。

**正確規則**:ratchet 與 ratchet-ack 兩個寫入都應把來源 gate 放進 `detail`(ratchet-ack 目前
完全沒有,ratchet 有但沒進去重鍵),且 `cmd_gov` 的去重鍵在這兩個 gate 上需要額外鑑別子(例如
比照 canary 的做法,用 `token` 帶 `f"{source_gate}:{stem}"`),否則「兩者同為 (gate,stem) 事件
粒度、去重後可比」這個前提不成立。

---

## F4(major)— S3 退場條件依賴的 `class=emergency` 是否落在 `gov --full` 的 50 字元截斷內未定義

引句：「必帶 `--class false-positive|emergency`,否則 rc2;留痕 `class` 欄」

S3 退場條件表:`gov --since 90 --full` 逐行計 `[code-loop/skipped]` 且 `detail` 含
`class=emergency` 的筆數。但 `gov --full` 的逐行輸出格式(`scripts/lumos:3046` 與 `:3077`,
兩處皆同)是:

```python
f"{r['ts'][:10]} [{r['gate']}/{r['kind']}/{mark}] {','.join(r['nodes']) or '-'}  {r['detail'][:50]}"
```

`detail` 被截斷到**前 50 字元**。而 `code-loop skip --note`(`scripts/lumos:14683`)的 `--note`
無長度限制、預設空字串,說明文寫「理由(pass/skip 必填習慣;進治理帳)」——是慣例而非強制,使用
者可以寫任意長度的中文理由。`_codeloop_gov_log`(`scripts/lumos:14021-14045`)目前把
`"detail": note` 原樣寫入,不做任何格式化。文件說「`_codeloop_gov_log` 的 detail 帶
`class=…`」,但沒有指定 `class=<值>` 要放在 `note` 前面還是後面、用什麼分隔符組合。若實作把
`class=emergency` **附加在 note 之後**(對「先寫理由、附帶分類」這種很自然的寫法而言是合理選
擇),只要使用者的 `--note` 超過約 35~40 個中文字(中文在 UTF-16/字元計數下每字佔 1 個
`str` 索引,不是位元組,50 字元大致對應 40~50 個中文字視內容而定),`class=emergency` 就會被
`[:50]` 切掉,`gov --full` 的逐行輸出裡完全看不到它,S3 退場條件表描述的「逐行計…(detail 含
class=emergency)」這個量測方法會**系統性低估**分子,而不是邊角案例——這種「先寫一段理由再帶
分類標記」的用法在既有治理帳裡並不罕見(參照本檔案內 canary/kill 等來源的 `detail` 組裝方式,
多半是先放主要內容、標記類欄位附加在後)。

**正確規則**:`_codeloop_gov_log`(或其呼叫端)在組裝 `detail` 時,`class=<值>` 必須放在
**最前面**(例如 `f"class={cls} {note}"`)以保證落在 50 字元截斷之前,並在測試策略里補一條
「`--note` 超長 + `--class emergency` 組合後,`gov --full` 該行仍可 grep 到 `class=emergency`」
的回歸測試;文件目前完全沒有規定組裝順序,是留給實作自由發揮的一個洞。

---

計 4 個發現(1 blocker / 3 major)。
