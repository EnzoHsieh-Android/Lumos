severity: minor

整合/知識同步鏡頭,逐節讀完整份凍結審材,並對 `scripts/lumos`、`scripts/test_lumos.py`、Systems 與 Projects 筆記、skills 實查。前掃已修的不重報。以下 6 條都是 minor。已讀、無 finding 的節:§2、§3、§5、§6、§7、§8、§11,以及〈回退〉〈合約候選〉。

### F1 B11 只修 doctor S14,同樣的「做綠後仍顯示紅」在 S12 也有
severity: minor
blocking: 否(只影響健檢提示的讀法,實作者不會做出壞系統)

- spec 段:§10 B11 與條款 [S26]。
- 引句:「不新增欄位、不重跑測試。」
- 引句:「每一列應標明那是規格閘當時的紅數與計劃現在的狀態」
- 問題:spec 認定的症狀是「做綠之後一直顯示『紅 2』」,只處理 S14 那一行。程式裡還有第二處同樣會停在舊值。
  - file: `scripts/lumos:3189-3231`:S12 讀治理帳 `spec-gate-run`,印「最近一次規格閘跑出來的紅綠弱證據 … 紅 N/綠 N/弱證據 N」,說明文字寫「紅=新行為還沒做」。
  - file: `scripts/lumos:9107-9119`:`spec-gate-run` 只在規格閘通過後才寫,失敗的重跑在 9107 就 return。所以實作做綠後,S12 仍顯示規格閘當時的紅數。
- 具體例:風險低計劃規格閘時紅 2,實作後做綠並推上去。照 spec 做完,S14 那列標了「規格閘當時」,S12 那列仍寫「紅 2 … 紅=新行為還沒做」。三個月後接手的人看到兩段互相矛盾。
- 判準:[S26] 只釘 S14,S12 沒有條款、沒有測試。

### F2 spec 說 t_docs_command_count 會抓漏改的每一處,但守衛抓不到 reference.md 的「91 個指令的總目錄」那句
severity: minor
blocking: 否(§1.7 已把那句列為要改的一處,只是守衛保證說過頭)

- spec 段:§1 第 7 點。
- 引句:「會掃全部活文件,漏改哪一處它就紅」
- 問題:file: `scripts/test_lumos.py:31622-31660` 只抓三種寫法:`(\d+) 個頂層命令`、`(\d+) top-level …`、`(\d+) 是頂層命令數`。
  - file: `skills/lumos-project-notes/reference.md:1260` 是「是 91 個指令的總目錄」,三種都對不上。
  - 那句改成 92 或漏改,守衛都綠。
  - 另外四處(ARCHITECTURE.md 三處、reference.md:117)會被抓。
- 具體例:實作者信了「漏了會紅」,只改守衛會報的地方,1260 那句留 91,沒有任何測試發現。
- 修法:spec 改成「1260 那句要人工改,守衛不管」,或順手把守衛的正則補上。

### F3 §1.7 的同步清單漏了列有 summary-line 的幾處
severity: minor
blocking: 否(漏掉只造成文件落後,不影響行為)

- spec 段:§1 第 7 點。
- 引句:「頂層指令數(現在寫 91 的地方:」
- 引句:「照上次改範本的慣例 bump」
- 問題:清單只照「指令數」和「鐵則 2 括號」找,漏了把 summary-line 當成寫入原語列舉的地方。
  - file: `skills/lumos-project-notes/reference.md:117` 的「寫入」列舉有 `summary-line`,沒有 summary-add。
  - file: `README.md:121` 寫「維護摘要可用 `lumos summary-line`」。
  - file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-write.md:41` 的 KEY 寫「8個寫入原語(set/append/remove/new/archive/decision-add/decision-supersede/self-audit)是…唯一安全路徑」,連 summary-line 都不在。同篇 105-109 的指令表也沒有。
  - 沒有守衛會抓這些。
- 具體例:summary-add 上線後,查指令總覽的人在 reference.md 的寫入列舉裡找不到它。

### F4 B2 推翻了已記載的設計裁定,卻沒有決策紀錄,也沒指出程式要改哪一處
severity: minor
blocking: 否(行為方向已明確,只是留痕與落點描述不足)

- spec 段:§10 B2、決策區 d1/d2。
- 引句:「當初只看 doing 是怕放著沒人管的計劃變成擋所有人的地雷」
- 引句:「沒被改到的 done 計劃照舊不查,地雷顧慮不變。」
- 問題一:這個「只看 doing」是已記載的裁定。
  - file: `docs/lumos-toolchain-knowledge/Projects/雙向門放行_計劃.md:211` 寫「計劃仍 doing…(r2 簡化席)」。
  - file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md` 的 PITFALL 說「推送前只挑 doing 且有風險低留痕的計劃」。
  - spec 的 decisions 只有 d1、d2,B2 沒有 d3 或 supersede。照專案規則,有結構、有出處的決策才有挑戰程式碼的效力;之後的人看到雙向門放行那段,會以為 done 被略過是現行設計。
- 問題二:spec 說 B2 是「候選多一種」,但 done 且被改到的計劃其實已經在候選裡。
  - file: `scripts/lumos:9141-9147` 的 `_spec_gate_push_candidates` 已經把 touched 的計劃全收進去。
  - file: `scripts/lumos:9768-9769` 擋住 done 的是 `_spec_gate_push_scan` 的 `full` 條件(`status == "doing"`)。
  - 實作者照字面去加候選會白做,真正要改的是 `full`,而且要確認 `_spec_gate_push_one` 對 done 計劃不再卡別的條件。

### F5 〈名詞〉說明了 S13/S13b,但本篇條款編號與 doctor 段名仍撞號
severity: minor
blocking: 否(措辭層級,上下文大致可分辨)

- spec 段:〈名詞〉健檢段名、驗收條款。
- 引句:「S14=風險低計劃放行統計。」
- 引句:「不是本篇的條款,也不是健檢段名。」
- 問題:前掃只改了 B8 的「S15」。本篇條款 [S8]、[S9]、[S10]、[S14] 與 doctor 段 S8、S9、S10、S14 仍同號,而且條款還直接寫「doctor S8」「doctor S14」:[S23]、[S26]、§10 B11、〈相容〉。
- 具體例:[S14] 是 lint 的「回頭條件已有一模一樣的舊條件組」,[S26] 的「doctor S14」是風險低放行統計。看到孤立的「S14」,分不出是哪個。
- 建議:條款編號加前綴,或健檢段名一律寫成「doctor S14 段」。

### F6 B3 在治理帳新增 spec-gate-record,相關舊說法沒列入更新
severity: minor
blocking: 否(寫回由鐵則 1 覆蓋,只是 spec 沒點名)

- spec 段:§10 B3、〈相容〉、lands_in。
- 引句:「同一筆再寫一筆治理帳事件」
- 問題:這份留痕現在在兩本帳各有一份,但有兩篇現行筆記的說法會變舊,lands_in 與 spec 都沒點名。
  - file: `docs/lumos-toolchain-knowledge/Systems/loop-convergence-recording.md:39` 的 KEY 說「.canary-log.jsonl 多一種 kind=spec-gate」。
  - file: `docs/lumos-toolchain-knowledge/Projects/治理帳例行紀錄分流_計劃.md` 說例行觀察進本機帳、`spec-gate-run` 在 `_GOV_LOCAL_PAIRS`(file: `scripts/lumos:1369-1375`)。
  - 新事件 `("spec-gate","spec-gate-record")` 不在該集合,所以進版控帳。方向正確,我實查過:`hard` 預設 False,但配對不在集合,`_gov_routes_local` 回 False。
  - 但這是第一個把每次放行的完整留痕(測試清單、條款指紋、排除理由)寫進 CI 唯一權威帳的規格閘事件,spec 只在〈相容〉說「要確認不受影響」,沒有條款或測試守住「`lumos gov` 與 doctor 讀治理帳時不會把 spec-gate-record 當成別的事件」。

最嚴重 severity:minor;blocking 共 0 條。
