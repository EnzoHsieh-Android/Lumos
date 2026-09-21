severity: blocker

## F1 substring 比對抓不到「名字還在、東西已經沒了」——這正是原始事故要防的情境

severity: blocker
blocking: yes

引句:「elif needle not in f.read_text(encoding="utf-8", errors="replace"):」

`check_scenario_targets` 對 `target` 的第二層檢查,只是 `needle in 檔案全文` 的字串比對,不管那個字串出現在哪個語境。原始事故是 `scripts/hooks/pre-push` 裡的 `sync_nudge` 函式在 2026-09-11 被整段移除,但移除時留了一句提到它名字的註解:

`scripts/hooks/pre-push:40`:`# (2026-09-11 起同步點名改由每支檔有家照家算,不再讀這一份;見下面 sync_nudge 原位置的說明。)`

也就是說,`sync_nudge` 這個 token 現在仍然存在於檔案裡,只是變成一句解釋「它被拿掉了」的註解,不再是可執行的函式。如果有人依照這次事故的直覺,把 target 寫成 `[["scripts/hooks/pre-push", "sync_nudge"]]`(最自然的寫法——就是事故本身提到的那個名字),`check_scenario_targets` 會判它「健在」:

重現(用真實 repo,不改動任何檔案,唯讀):
```
python3 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('probe', 'scripts/scenario_probe.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
scenarios = [{'id': 'd05-repro', 'prompt': '...', 'target': [['scripts/hooks/pre-push', 'sync_nudge']]}]
print(m.check_scenario_targets(scenarios, '.'))
"
```
輸出:`bad = []`(判定健康)。

但 `sync_nudge` 函式與呼叫確實已經在 2026-09-11 的提交 `dcd5c9d` 裡整段刪除(`git log -p --all -S"sync_nudge" -- scripts/hooks/pre-push` 可查,`-sync_nudge() {` 是刪除行、留下的只有一句提到它名字的註解)。這條檢查的存在理由(patch 的說明段)就是「題目指的東西已經不存在,不能安靜地量出假訊號」——但只要移除時像這次一樣留了一句提及舊名字的說明性註解(這在本 repo 本身就是常見寫法,不是刁鑽情境),這道防線會被繞過而不自知,量出的仍然是假訊號,只是使用者以為自己已經補了保險。這次實際出貨的 `d05` 已經換了別的字串(`--advisory`)所以沒踩到,但機制本身對這個最自然的重用方式是失效的,不是邊角案例。

## F2 README.md 同一份檔案裡,新舊定位在幾行之內自相矛盾

severity: major
blocking: yes

引句:「你透過對話提出需求、釐清限制與決定取捨，AI 則在授權範圍內承接從查詢脈絡、實作、測試，到提交與推送的開發流程。」

這行是 patch 裡 `README.md` 該段落的未變更 context 行(在被改動的 hunk 範圍內,緊接在它後面幾行的另一句被改了)。緊接著這行之後,patch 把下一段改成:

引句:「現況以程式碼為準；一次改動繞過四站：**圖譜 → 派工 → 審查 → 寫回**，補上程式碼產生不出的那一段。」

同一篇文件、同一個導言區塊裡,前一句還在講「AI 從查詢脈絡開始承接開發流程」(舊定位:先查圖譜取回脈絡),後一句已經改成「現況以程式碼為準,圖譜只補程式碼產生不出的那段」(新定位:先讀程式碼,圖譜是補充)。兩句話字面上互斥——讀者往下讀四行就會看到兩套不同的第一步說法。英文版 `README.en.md` 同一位置的段落(「the AI carries out the development workflow—from retrieving context and implementing changes to testing, committing, and pushing.」)也是同樣沒改到的舊句子,對應同一個問題。這正是派工詞要求特別查的「新說法有沒有跟 repo 裡其他地方互相矛盾」,而且矛盾就在被改動的同一個檔案裡,不用跨檔案找。

## F3 ONBOARDING.md 仍明寫「先查筆記」,跟這次改的新定位相反,且被 README 直接連結出去

severity: major
blocking: yes

引句:「知識圖譜是一組互相連結、可隨專案版本管理的 Markdown 筆記。它記錄的是程式碼讀不出來的部分：設計理由、被否決的方案、程式看不到的限制、事故教訓與驗證前提。」

這是 patch 對 `README.md` 新增的定位敘述(程式碼優先、圖譜補脈絡)。但 `README.md` 本身有一行連到 `ONBOARDING.md`(patch 未改動這行,見 `README.md` 原文「Windows、接手已導入的專案、離線安裝與移除方式，見 [上手細節](ONBOARDING.md)」,對應 patch 中該行原樣保留),而 `ONBOARDING.md:81` 寫的是:

`ONBOARDING.md:81`:`1. 筆記(放在 \`docs/<專案>-knowledge/\`)記的是「為什麼、邊界在哪、驗過沒」;程式碼只是「現在長這樣」。要懂系統,先查筆記。`

這句話的立場剛好是這次要改掉的舊定位(先查筆記、程式碼只是現況的附屬),跟這次 patch 在 README 裡新寫的「程式碼是現況的依據,圖譜補的是程式碼產生不出的東西」直接相反。這份檔案沒有被這次 patch 觸碰到,讀者從 README 點進上手細節,看到的是被推翻的舊說法。

## F4 路徑抽取正則會把「版本對照」寫法誤判成路徑,導致健康題目被錯擋

severity: major
blocking: yes

引句:「_SCEN_PATH_RE = re.compile(r"(?<![\w./-])((?:[\w.-]+/)+[\w.-]+\.[A-Za-z0-9]+)")」

這條正則只要求「一段或多段 word/dot/dash + 斜線」接「word/dot/dash + 副檔名」,沒有排除「版本號 A / 版本號 B」這種寫法。本 repo 自己的筆記就用這種寫法,而且就在這次 patch 改動的同一個檔案裡:

引句:「Stop check-graph-sync 讀 Codex 逐字稿(版本表 0.144.1/0.153.2,不在表略過不猜)」

（見 patch 中 `docs/lumos-toolchain-knowledge/Systems/codex-harness.md` 該 hunk 的 context 行。）

重現:
```
python3 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('probe', 'scripts/scenario_probe.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
print(m._SCEN_PATH_RE.findall('版本表 0.144.1/0.153.2,不在表略過不猜'))
"
```
輸出:`['0.144.1/0.153.2']`——被當成一條路徑抽出來。如果未來哪一題的 prompt 裡也用這種「A/B 版本對照」寫法(本 repo 的筆記語感明顯會這樣寫),`check_scenario_targets` 會去檢查 `repo / "0.144.1/0.153.2"` 存不存在,查不到就判定題目腐爛、印出「題目提到 0.144.1/0.153.2,但它在 repo 裡不存在」,回傳 3 讓整輪停手——即使題目本身完全健康。使用者要嘛得手動加 `--allow-stale-targets`,要嘛得学会「這個工具常常誤報,不用管」——而後者會連帶把 F1 那種真正的腐爛也一起蓋過去,削弱這整道檢查存在的意義。

## F5 沒有副檔名的節點名,第一層正則永遠抓不到,完全依賴作者記得手動補 target

severity: minor
blocking: no

引句:「for rel in dict.fromkeys(_SCEN_PATH_RE.findall(prompt)):」

`_SCEN_PATH_RE` 的結尾強制要求 `\.[A-Za-z0-9]+`(副檔名),所以像圖譜節點名 `Systems/graph-sync-coverage` 這種沒有副檔名的寫法,第一層「從題目文字抽路徑」完全不會命中:

重現:
```
python3 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('probe', 'scripts/scenario_probe.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
print(m._SCEN_PATH_RE.findall('在 Systems/graph-sync-coverage 這篇筆記最後加一段'))
"
```
輸出:`[]`。這句題目文字本身就出自本次 patch 的 `d02-lint-after-note`(見 `governance/scenarios/discipline.jsonl` diff 的 `+` 行,prompt 內容原樣保留)。這一題現在靠 `target` 欄位補上才有保護,但那是作者這次手動加的,機制本身不會提醒「這一題其實沒有第一層可用」——往後新增引用圖譜節點卻忘了加 `target` 的題目,會悄悄失去這道防線,而不會有任何訊號。

## F6 target 的 needle 給空字串時,檢查等同恆真,語意沒有寫明

severity: minor
blocking: no

引句:「"target": [["governance/scenarios/answers.jsonl", ""]]}」

`d06-rename-checks-notes` 的 target 就是這樣寫(見 `governance/scenarios/discipline.jsonl` diff 的 `+` 行)。程式裡 `needle not in f.read_text(...)` 這一判斷式,對空字串 `needle` 恆為 `False`(Python 裡任何字串都「包含」空字串),等同於這一項 target 只驗證了「檔案存在」,完全不驗內容。這跟其他題目的 target 用法(檢查某段文字還在不在)語意不一致,但程式和 patch 裡都沒有註解說明「空字串=只查存在,不查內容」是刻意設計還是巧合;下一個照抄格式的人多半會以為空字串是漏填,而不知道它其實有特殊行為。

## F7 d04 的 target 綁的內容跟題目本身的前提無關,只是為了讓釘住測試過關而湊的錨點

severity: minor
blocking: no

引句:「"target": [["scripts/scenario_probe.py", "def main"]]}」

`d04-design-goes-to-graph` 這題的 prompt 是「幫我設計一個『探針結果自動比對上週、掉題就開 issue』的方案」,跟 `scripts/scenario_probe.py` 有沒有 `def main` 函式沒有任何語意關聯——`def main` 這個字串幾乎不會消失(它是整支程式的入口),就算這道題目原本想測的前提(例如「探針結果比對」這個構想本身)已經過時,這條 target 也永遠判「健在」。這跟 `check_scenario_targets` 的設計初衷(驗題目講的東西還在不在)脫節,比較像是為了讓 `t_probe_discipline_targets_are_fresh` 六題全過而找的形式上的錨點,沒有實際驗到這題的前提。

## F8 target 指到目錄時,錯誤訊息說「不存在」,但其實它存在,只是不是檔案

severity: minor
blocking: no

引句:「bad.append(f"{sid}:target 指的 {rel} 不存在")」

`f.is_file()` 對目錄回傳 `False`,所以 target 若寫成一個目錄路徑,會被歸進「不存在」這條訊息分支。重現:
```
mkdir -p /tmp/rot-review/repo2/adir
python3 -c "
import importlib.util
spec = importlib.util.spec_from_file_location('probe', '/Users/enzo/harness/lumos-toolchain/scripts/scenario_probe.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
print(m.check_scenario_targets([{'id':'x','prompt':'','target':[['adir','X']]}], '/tmp/rot-review/repo2'))
"
```
輸出:`['x:target 指的 adir 不存在']`——但 `adir` 其實存在,只是它是目錄而非檔案。訊息會誤導使用者去查「這個路徑是不是被砍了」,而實際問題是 target 欄位本來就不該指到目錄。影響小(目前六題沒有這樣寫),歸類為文字精確度問題。

---

## 已驗過、判定沒問題的部分(避免遺漏交代)

- **停手時機無副作用**:`check_scenario_targets` 在 `main()` 裡的呼叫點,位於 `make_sandbox(src, a.arm)` 之前(見 `scripts/scenario_probe.py` 該 hunk 的順序:先驗 `.git` 存在、再 `check_scenario_targets`、再才建沙盒);`return 3` 之前沒有建立任何臨時目錄或寫入 `--history`。唯讀審查下沒有找到反例。
- **`--dry-list` 會繞過檢查,但這是既有邏輯順序自然的結果**:`if a.dry_list: ...; return 0` 這段在 patch 裡位於新檢查呼叫點之前(原有程式碼順序),`--dry-list` 本來就只印題目 id、不跑任何東西,沒有側效風險,判定合理而非漏洞。
- **中文路徑、UTF-8 位元組、needle 含特殊字元**:`scripts/測試檔.py` 這類中文檔名正則抓得到(已跑 `_SCEN_PATH_RE.findall` 驗證);`f.read_text(encoding="utf-8", errors="replace")` 對非 UTF-8 內容不會拋例外;needle 比對用的是 `in`(子字串),不是正則,所以 needle 裡有 `.` `*` `(` 這類正則特殊字元不會出錯。
- **網址、email、單純版本號(不含斜線)不會被正則誤判為路徑**:`https://example.com/docs/readme.html`、`someone@example.com`、`1.2.3`、`x.y.z`、`3.11` 皆已實測 `_SCEN_PATH_RE.findall` 回傳 `[]`。
- **新增的兩支測試(`t_probe_detects_rotten_targets`、`t_probe_discipline_targets_are_fresh`)目前都通過**:`python3 scripts/test_lumos.py -k rotten_targets`(6 案例全過)、`-k probe_discipline_targets`(1 案例過)。`t_probe_discipline_targets_are_fresh` 是動態讀取當下 `discipline.jsonl` 內容去驗證,題庫增刪題目時它會自動反映現況、不需要手動跟著改,不構成固定式假綠。
- **孤立看,單一題目腐爛時訊息會逐題列出**(已用 `t_probe_detects_rotten_targets` 的「多題壞 → 逐題報」案例驗證,兩題壞會回兩條訊息,不是只報第一條)。
