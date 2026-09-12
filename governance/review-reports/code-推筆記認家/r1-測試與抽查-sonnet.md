severity: major

審查範圍:`governance/review-reports/code-推筆記認家/r1-part-audit.patch`(home_audit.py 新檔 184 行)、
`r1-part-tests.patch`(test_lumos.py 774 行改動,約 20 支新測試)。對照 `r1-snapshot.patch` 的 scripts/lumos、
scripts/hooks/claude/{impact-hook.py,check-graph-sync.py}。全部發現皆在
`/Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh`(HEAD=09567f39,working tree clean)以 mutation testing 實跑
`python3 scripts/test_lumos.py -k <關鍵字>` 驗證,改完都已還原(`git status --short` 乾淨)。

---

1. `t_impact_home_moves_out_of_lane` 的③是假綠——它宣稱驗證的「搬進必推、從參考道拿掉」那段程式碼在這個測試場景裡完全沒被執行到。前提①用 `src/hub.py` 查出「守衛面的家」落在參考道,但②③改查 `src/pay.py`——是完全獨立的另一次 impact 呼叫、另一份 `lane_raw`。因為「守衛面的家」body 用反引號寫了 `` `src/pay.py` ``,它在查 `src/pay.py` 時本來就直接靠 body-inline-code 進了 `results`(kind=direct、因 RISK 合約 pinned=true),從沒進過那次呼叫的 `lane_raw`,所以 `_impact_mark_home` 裡 `lane = lane_by.get(node)` 永遠是 `None`,`lane_raw.remove(lane)` 那整段從沒跑到。實測:把 `lane_raw.remove(lane)` 那行拿掉,`python3 scripts/test_lumos.py -k impact_home_moves_out_of_lane` 仍 3/3 全綠(①②③都過)。
引句:「被分到「守衛面參考」那條道的節點,如果是這支檔確認過的家 → 搬進必推名單,\n    而且從參考道拿掉(同一篇只出現在一個地方)。」
file: `scripts/lumos:21571`(`lane_raw.remove(lane)` 那行——mutation 拿掉後測試仍全綠)
severity: major
blocking: 是

2. `home_audit.py` 的錯誤率算法分母對、分子沒驗:`tally --ruling` 把人裁檔裡 `wrong` 清單的 id 直接當分子,從不檢查那些 id 是否真的出現在這批 `rows` 裡。實測:用一份 ruling.json 塞入不存在的 id(`p999`、`p998`)混一個真 id,對 2 對配對算出「錯誤率…= 3 對 ÷ 總共 2 對 = 150.0%」——比對照組(全 repo 已經產出的 `governance/review-reports/推筆記認家-v2/home-audit-verdicts-r1-作廢.json` / `-r2.json` 兩輪批次同時存在)來看,重複用錯輪的人裁檔正是這個工具日常會發生的操作失誤,而它會被腳本無聲吃下、印出一個超過 100% 但看起來正常的數字,不會報錯。`t_home_audit_tally_counts` 只用了 ruling 裡本就存在的 id,完全沒測過這個情況。
引句:「rate = len(wrong) / len(rows)」
file: `governance/eval/home_audit.py:149`
severity: major
blocking: 是

3. `home_audit.py` 呼叫主程式 `_nodehome_homes(None, _SideFromEnv(env))` 時把 `repo_root` 硬寫成 `None`,而全部其他真正呼叫端(`_nodehome_ledger`、`cmd_home_check`)都傳真正的 repo 路徑進去;目前這個參數沒被用到所以無害,但只要 `_nodehome_homes` 未來開始真的用它(例如比對受版控清單濾掉未提交的路徑——這正是本次改動在別處新增的 `_impact_repo_files(repo_root)` 已經在做的事),`None` 不會報錯,只會靜默算出跟真實行為不同的答案。實測:在 `_nodehome_homes` 裡加一段「repo_root 給了就用 `_impact_repo_files` 濾掉未受版控的路徑」的合理擴充,對同一批**未 commit** 的節點,真呼叫端算出 `{}`(0 個家),而 `home_audit.py` 因為傳 `None` 照樣算出 3 對——兩邊分岔,但 `governance/eval/home_audit.py` 與 `scripts/test_lumos.py` 裡沒有任何一支測試比對「這支腳本算出來的家對照表」跟「真呼叫端用真 repo_root 算出來的家對照表」是否一致(`t_impact_home_uses_nodehome_definition` 只比對 `_nodehome_homes(root,...)` 對 `_impact_home_map(env)`,兩邊都不是 home_audit.py 那條路)。
引句:「homes, _own = m._nodehome_homes(None, _SideFromEnv(env))」
file: `governance/eval/home_audit.py:75`
severity: major
blocking: 否

4. `lumos doctor` 的 S11 健檢裡「舊帳:已存在節點管了某支檔卻連檔名都沒提到」那一段完全沒有測試覆蓋——這段程式跑在 `_nodehome_ledger`(掃全部已提交的 Systems 節點),跟 `t_nodehome_new_home_unmentioned_reminds` 測的 `_nodehome_evaluate`(只掃 pre-commit 這次新增的家)是兩份獨立實作。實測:把 `_nodehome_ledger` 裡算 `unmentioned` 的那一小段整段拿掉,`python3 scripts/test_lumos.py -k home` 仍 310/310 全綠;另外自己造一個「about_code 列了 src/d.py、正文完全沒提到 src/d.py」的已提交節點跑 `lumos doctor`,確認正常版真的會印「⚠ 有 1 對「管了這支檔、卻連檔名都沒提到」」——功能本身是對的,純粹是沒有任何測試釘住它。
引句:「有 {len(_nhl['unmentioned'])} 篇是從程式重建出來的,卻一支檔都沒管、也沒寫負責範圍」
file: `scripts/lumos:18643`(`_nodehome_ledger` 算 `unmentioned` 那段——整段拿掉後 `-k home` 310/310 仍全綠)
severity: major
blocking: 是

5. `t_impact_home_confirmed_is_entry_and_pinned` 的②有一半是死檢查:斷言用 `by.get("Systems/沒提到的家", {})`(漏了 `.md`)去查 `pinned`,而 `by` 的 key 全部帶 `.md` 副檔名,這個 key 永遠查不到、永遠回傳 `{}`,`not {}.get("pinned")` 永遠是 `True`——這半句斷言跟程式碼實際行為無關,單獨拿掉 `_home_confirmed` 的分兩級邏輯(讓它永遠回傳 `True`)也不會讓它翻紅。不過同一條斷言的另一半(用正確 key 查 `home`)有正確接住;而且「未確認的家不進必推」這個行為已經被 `t_impact_home_unconfirmed_not_pinned` 用正確的 key 完整驗過,所以不構成漏測,只是這條斷言本身有名不副實的死碼。
引句:「not by.get("Systems/沒提到的家", {}).get("pinned") and not by.get("Systems/沒提到的家.md", {}).get("home")」
file: `scripts/test_lumos.py`(對照 `r1-part-tests.patch` 該行,`by.get` 的 key 少了 `.md`)
severity: minor
blocking: 否

6. `home_audit.py sample --n` 給負數時沒有任何防呆,直接讓 `random.Random(seed).sample(picked, args.n)` 丟出未捕捉的 `ValueError` 印出完整 traceback,而不是像其它輸入錯誤(空母體、沒有 pairs)一樣印一句話再 `return 2`。實測:`python3 governance/eval/home_audit.py sample --vault docs/lumos-toolchain-knowledge --seed 1 --n -1` 直接炸 traceback。兩份 patch 都沒有任何測試餵過負數或者「--n 大於母體」以外的邊界(--n 大於母體時目前的行為是回全部,沒有測試釘住這一點,也沒說明是否故意)。屬於內部審查工具的輸入防呆缺口,不是產線熱路徑,不影響本案主功能正確性。
引句:「picked = random.Random(args.seed).sample(picked, args.n)」
file: `governance/eval/home_audit.py:105`
severity: minor
blocking: 否

---

其餘用 mutation testing 逐一驗過、確認會真翻紅、判 clean 的關鍵行為(不逐條展開,只列已核實項目):
`_home_confirmed` 分兩級(反引號唯一裸檔名 / 完整路徑)、`_impact_mark_home` 的大檔門檻(≥8 篇不當入口)、
必推排序(事故→家→其餘,家內照分數/篇名)、`_nodehome_evaluate` 的 `regen-no-home`(含「沿用舊文字不算交代」
`_resp_rewritten` 判定與同篇不重報的去重)、pre-commit 的 `home-unmentioned` 新增提醒、
`dispatch-lens`(diff 模式與 spec 模式)把「家」標出來且排序正確、`_home_map_from_notes` 的
type/status 過濾(只算 Systems 的 doing/done/stale)。這些逐一用「拿掉/反轉該段程式碼→原測試翻紅」的方式
現場驗證過,不是憑讀碼判斷。
