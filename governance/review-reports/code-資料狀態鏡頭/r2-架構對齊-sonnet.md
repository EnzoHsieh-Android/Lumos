severity: clean

檢查範圍:完整讀 r2-snapshot.patch(251 行),對照 scripts/test_lumos.py 既有寫法(`t.split("## 7.8", 1)[-1].split("\n## ", 1)[0]`、`_re.findall(r"```[a-z]*\n(.*?)```", text, _re.S)`、t_tension_doc_sync/t_marker_doc_sync/t_security_seat_doc_sync/t_templates_security_seat_section 的檔案讀取與 `_SrcOnly` 慣例)、templates.md §3/§7 既有結構、python-idioms。

上一輪兩個洞的修法都逐字核對過:
- `scripts/test_lumos.py:40182` `sec = templates_text.split("## 3. Code-loop reviewer", 1)[-1].split("\n## ", 1)[0]` —— 跟 `scripts/test_lumos.py:41249`(`## 7.8`)、`:41253`(`## 7.7`)、`:43769`(`## 7.6`)同一種純字串切法,前綴匹配風格也一致(不含括號註解)。
- `scripts/test_lumos.py:40253` `s7 = tt.split("## 7. 平行 panel 派工", 1)[-1].split("\n## ", 1)[0]` —— 同上,且與既有寫法一樣只在 `"## 7. 平行 panel 派工" in tt` 成立時才切。
- `scripts/test_lumos.py:40183` `_re.findall(r"```[a-z]*\n(.*?)```", sec, _re.S)` —— 跟 `scripts/test_lumos.py:8006` 完全同一組正則參數,沒有另組寫法。

修訂輪常見的「自己引入新不一致」與「上輪角落」都額外查過,沒發現新洞:
- `import re as _re` 寫在函式內部(非模組頂層)是本檔既有慣例,全檔 67 處都這樣寫(如 `scripts/test_lumos.py:41,7554,7712`),新函式 `_code_reviewer_prompt`/`_correctness_lens_missing` 沿用同一寫法,不是另一種 import 風格。
- 新模組常數 `_CORRECTNESS_LENS_ITEMS`(`scripts/test_lumos.py:40169`)緊鄰它專屬的測試定義,跟既有 `_NOT_LUMOS_PROGRAMS`(`scripts/test_lumos.py:7661`)就近宣告的慣例一致,不是集中到檔頭的另一種擺法。
- 新測試用 `repo = Path(__file__).resolve().parent.parent` 直接讀 skills/*.md,不繞 `_load_lumos_inproc()`——這跟 `t_tension_doc_sync`(`scripts/test_lumos.py:40151`)、`t_security_seat_doc_sync`(`scripts/test_lumos.py:41219`)同層次(純讀 markdown 文件,不是測 lumos CLI 行為),沒有跨層直呼。
- `t_data_state_lens_doc_sync` 只查 skills/*.md 三份、不含知識圖譜節點——原以為跟 `t_tension_doc_sync` 的「檔案清單含 kg/」不同,但核對後 `t_marker_doc_sync`(`scripts/test_lumos.py:6873`)、`t_security_seat_doc_sync`(`scripts/test_lumos.py:41219`)兩個更常見的先例也都只查 skills 檔,「含 kg 節點」只是 tension 那一支的個案,不是普遍慣例,不算第二種做法。
- templates.md §7 新增那句承認「靠編排者照做,沒有機械擋」(`skills/lumos-design-loop/templates.md:362`)沒有附 REVISIT——查了 `skills/lumos-design-loop/SKILL.md:16`「這道判斷目前靠你自己誠實,沒有機械擋」,本檔本來就有這種不掛 REVISIT 的坦承句先例,新句照抄既有寫法,不是新開一種坦承方式(是否合 CLAUDE.md 鐵則4 不在本輪「一不一致」判準內)。
- `_correctness_lens_missing` 用 `_re.match(r"\s*·\s*([^：:]+)[：:]", ln)` 解析逐行標頭,雖然全檔多數用 `startswith`/純字串比對,但逐行前綴抓正則本檔也有先例(`scripts/test_lumos.py:28004`),且這題(從九個變動子題裡挑出缺哪個)本身需要抽取變動內容,不是硬套第二種平行解法去做同一件事。
- reference.md 的 refute framing 新增「資料狀態:新舊互讀、寫一半、衍生資料、時間、不可逆」是精簡名詞版,templates.md §3 才是帶例句的完整版——這跟該段既有的「邊界/資源/例外/冪等」四題就是精簡版對完整版的關係一致,沒有另外複製一份完整內容造成雙源。
- wiki 連結格式 `[[Projects/代碼審資料狀態鏡頭_計劃]]`、`[[Issues/輕量設計審手冊叫人記處置帳但工具不收]]` 都不含 `.md` 副檔名,跟本 patch 其他既有連結、以及 t_tension_doc_sync 引用的 `[[Projects/兩席相反時端出張力_計劃]]` 一致。

總結:不對齊共 0 條,其中 major 0 條。
