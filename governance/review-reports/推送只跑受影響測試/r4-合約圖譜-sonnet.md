severity: major

以下逐條回答合約與圖譜一致這個立場。

**已讀,無 finding 的部分**
- `pitfalls --json` 新增欄位不會破壞既有消費者。
  - CI prep 只讀 `suite`、`suite_reason`、`suite_graph`。
  - `_codeloop_pitfalls_tier` 與表態閘只取第一行 `{` 開頭的 JSON 再讀指定鍵。
  - 掛鉤現有的讀法都是 `grep` 加固定鍵。
  - 證據:`.github/workflows/ci.yml:93`、`scripts/lumos:70912`、`scripts/lumos:71060`、`scripts/hooks/pre-push:545`。
- [[Systems/bound-tests-gate]] 的 INVARIANT 是 `code-loop check` 逐支真跑合約綁的測試,跟本機跑哪個測試套件無關。降級不影響它,掛鉤第 591 行的 advisory 邏輯也獨立於 `_suite_this`。
- CI 的 `pull_request` 一律全套、`concurrency` 的形狀與計劃「現況」所述一致。證據:`.github/workflows/ci.yml:4-21`、`.github/workflows/ci.yml:83`。
- 回退的主要項目逐處對應:掛鉤降級分支、S1/S3/S6 測試、說明文字、S7、重簽基準。

**Finding 1**
severity: major
blocking: 是(照字面實作會讓所有消費專案的紀律區塊宣稱一件它們做不到的事,屬漏掉合約)
- spec 段落:做法 4 與 S7。
- 問題:紀律範本會 vendor 進所有消費專案,但本計劃的前提(推功能分支不跑全套、PR 的 CI 全套照跑、合併一律走 PR)只在本 repo 成立。
  - 本 repo 的 `ci.yml` 是唯一的 workflow,範本沒有附 CI。
  - 消費專案的 CI 與 PR 流程由各自決定。
  - 範本改成「全套由 PR 的 CI 跑」後,沒有 CI 或不走 PR 的消費專案,`lumos update` 一重新注入就拿到錯誤指引。
  - spec 的 S7 只驗本 repo 的 `CLAUDE.md` 與 `AGENTS.md` 跟範本一致,沒有驗消費端。
  - 做法 4 沒有說明範本的寫法該怎麼限定在本 repo,也沒有說這句話只在掛鉤已升版時成立。
引句:「用 `lumos update` 重新注入 `CLAUDE.md` 與 `AGENTS.md` 的紀律區塊」
佐證 file: `scripts/test_lumos.py:98641`(「範本會 vendor 進消費專案」)、`.github/workflows/ci.yml`(`git ls-files` 只有這一支 workflow)

**Finding 2**
severity: minor
blocking: 否(措辭層的內部矛盾;照做法 1 實作的行為本身是 spec 另一處明寫接受的)
- spec 段落:範圍「做」第 ③ 條與實務隱患「主線判定查候選失敗」。
- 問題:範圍說算不出主線時照全套,但做法 1 沿用的 `_note_reread_mainline_names` 在查候選失敗或逾時時只回固定名集合,不吐「算不出」的訊號。
  - 實務隱患那條也說這種情況會被當成功能分支。
  - 該函式的合約是「不擋:只影響這次算不算推主線,不算的照功能分支走」,方向對筆記重讀閘是放寬,對本計劃(失敗要走全套)是反向。
  - 所以「算不出主線時照全套」做不到,而且「算不出來的方向」那一條沒有列這個例外。
引句:「算不出範圍、算不出主線時照全套」
引句:「只剩 `main`、`master` 兩個固定名;預設分支叫別的名字(例如 develop)時那次會被當功能分支」
佐證 file: `scripts/lumos:53734`(函式 docstring)

**Finding 3**
severity: minor
blocking: 否(文件同步清單不全,屬文件精度)
- spec 段落:做法 4「說明文字同步(逐處)」。
- 問題:清單漏了幾處仍宣稱「CI 會跑全套當後盾」或「推送前的全套」的現存字樣,降級上線後會變得不準:
  - `scripts/hooks/pre-push` 的兩句使用者訊息,講的是 light 且關鍵字沒對到的情境。降級後這兩句在沒有 PR 的功能分支上為假,並且會跟做法 3 的新訊息一起印出。
  - `scripts/test_lumos.py` 把其中一句釘成斷言,要改訊息就得動這支測試。
  - `.claude/hooks/session-start.sh` 的註解和 [[Systems/雲端工作階段開場設定]] 的 WHY 都寫「推送前的全套測試依賴它」,功能分支降級後不再成立。
  - 清單只列了 `_suite_word` 一句,沒列這兩行訊息。
引句:「掛鉤 `_suite_word` 的說明句」
佐證 file: `scripts/hooks/pre-push:894`、`scripts/hooks/pre-push:963`、`scripts/test_lumos.py:80228`、`.claude/hooks/session-start.sh:2`、`docs/lumos-toolchain-knowledge/Systems/雲端工作階段開場設定.md:19`

**Finding 4**
severity: minor
blocking: 否(驗收條款可寫性問題,不影響閘的方向)
- spec 段落:做法 1 的 `suite_computed` 與 S5。
- 問題:`suite_computed` 為 false 的兩個情境在現行程式幾乎出不來。
  - `_pitfall_diff_collect` 先跑 `git diff -U3`,範圍有問題時直接印「擋下」並回 None,`pitfalls` rc2、stdout 沒有 JSON。S5 的測試用壞範圍造不出 `suite_computed: false`。
  - 實測 `pitfalls --diff deadbeef..cafebabe --json` 得到 rc=2、沒有 JSON。
  - 只剩 `git diff --name-only` 單獨失敗或 OSError 才會出現 false。
  - `_test_suite_for_range` 回傳的 dict 沒有「算得出」旗標,只能靠 `reason` 字串區分。spec 沒說要在回傳 dict 加欄位,也沒說守衛檔早退算 computed true。
引句:「當範圍算不出來時,`pitfalls --json` 應 回 `suite_computed: false`;算得出時 應 回 true」
佐證 file: `scripts/lumos:61801`、`scripts/lumos:61705`

**Finding 5**
severity: minor
blocking: 否(回退描述不完整)
- spec 段落:回退。
- 問題:回退第一條只寫拿掉做法 2 的降級分支與多帶的旗標,沒有點出要一併拿掉做法 3 的新訊息,也沒說若 Finding 3 補了兩行訊息的改寫,回退時要還原。另外 S1 與 S6 共用同一支測試,回退時刪的是整支。
引句:「拿掉做法 2 的降級分支與多帶的旗標(推功能分支回到本機全套);刪 S1、S3、S6 的測試(S2 留著)。」
佐證 file: `scripts/hooks/pre-push:891`(light 分支的訊息是現行程式,回退時要確認還在)

總結:最高等級是 major,會擋的問題 1 條,其餘 4 條為 minor 不擋。
