severity: major

**問 1 分層與依賴方向**
- 新複合動作放在 `.github/actions/test-tools/action.yml`。呼叫它的只有 ci.yml 裡 prep 的文件子集那步和 shards 的安裝那步,方向單純:工作呼叫動作,動作不反過來呼叫任何東西。
- prep 判範圍、shards 跑全套的分工沒有被打亂。prep 只多了一步「裝工具(文件子集)」,有 `if: steps.suite.outputs.suite == 'docs'` 把關,shards 仍然只在 `needs.prep.outputs.suite == 'full'` 時跑。
- 沒有跨層直呼。這個 repo 原本沒有 `.github/actions/` 目錄(ls 只有 workflows),這是第一個。
- 這一問沒有找到不對齊。

引句:「        if: steps.suite.outputs.suite == 'docs'
        uses: ./.github/actions/test-tools」,這兩行拿來對照 `.github/workflows/ci.yml:84`(prep 的範圍判定步驟)和 `.github/workflows/ci.yml:131`(shards 的 `needs: prep`、`if: needs.prep.outputs.suite == 'full'`)。

**問 2 命名與寫法**

3. 筆記 PITFALL 行的欄位跟鄰居一致。它帶了 `[出處:]` `[根因:]` `[修法:]` `[repro:]`,同檔 PITFALL 用的是 `[出處:]` `[根因:]` `[修法:]` `[test:]`/`[防回歸:]`,別篇如 `docs/lumos-toolchain-knowledge/Systems/規格閘.md` 用 `[repro:]`。依 CLAUDE.md,`[test:]` `[repro:]` `[防回歸:]` 三選一,所以結構上沒問題。
4. responsibility 句式跟鄰居一致。新句子是「負責…;不負責…」,和其他 Systems 節點同式(例如 android-arch-template 的 responsibility 行,以及 Kotlin 規則包那篇的「負責…;不負責…」)。
5. 動作檔名與 name 的寫法沒有明顯偏離。步驟用中文 name,風格與 ci.yml 一致,例如 `裝釘版本的 detekt` 對照 ci.yml 原有的同名步驟。

**finding 1:複合動作與 ci.yml 內檔案頂層註解的出處標法略有差異**
severity: minor
blocking: 否
- 新動作檔開頭的註解把日期事件寫成括號內說明:「(2026-11-08 純文件推送第一次撞到…」。ci.yml 鄰居的寫法是「(2026-10-03 第一個 PR 實際踩到)」,位置在句尾,出處標在計劃節點之後。兩者格式大致相同,差別很小。
- 另一個不一致:ci.yml 的 prep 新步驟註解寫「(2026-11-08 #178 合併後撞到)」,用 PR 編號當出處。ci.yml 其他步驟的出處都是 `Projects/…_計劃` 節點或日期,沒有用 `#編號` 的先例。
引句:「文件子集裡也有要外部工具的測試(例:t_detekt_compose_rules_shared_config),CI 上沒裝會判紅(2026-11-08 #178 合併後撞到)」
file: `.github/workflows/ci.yml:57`(鄰居是「(2026-10-03 第一個 PR 實際踩到)」,沒有 `#編號` 寫法)

**問 3 第二種做法**

**finding 2:引入「複合動作」這個第二種重用步驟的方式**
severity: major
blocking: 是
- 專案既有的重用方式是「複製步驟,加註解說明各處都要自己做」。證據:
  - 「PR 事件補上本機 main」這一步在三個工作各複製一份,位置在 `.github/workflows/ci.yml:57`、`.github/workflows/ci.yml:141`、`.github/workflows/ci.yml:198`,註解明寫「工作之間不共用機器,每個工作都要自己補」。
  - `actions/checkout@v4` 與 `actions/setup-python@v5` 也都是每個工作各寫一次。
  - ci.yml 裡其他處的重用寫法是「照上一步」「照全套那步補」,見 `.github/workflows/ci.yml:120` 與 `.github/workflows/ci.yml:297`。
- 原本 detekt 步驟的註解寫「★CI 第一個非 pip 的工具下載,以後別的工具照這步抄★」,這就是專案對重用的明文規定:照抄。
- 這個 patch 把那條規定改了:註解被搬進新動作檔,但「照這步抄」的做法在同一份 patch 裡被複合動作取代。ci.yml 的現況是步驟複製(其他工作)與複合動作(這三支工具)兩種做法並存。
- 沒有圖譜裡的決策紀錄(`decisions:` 或 WHY 行)交代「為什麼這次例外、其他重複步驟為什麼不一起改」。新增的 PITFALL 只講修法,不是 WHY。
- 判準的依據:嚴重度錨說「引入第二種做法」就是 major。⚠ 不確定的地方:複合動作的好處(版本與雜湊只寫一處)是真的,而且 PR 補 main 那步只有三行,複製成本低,和三支工具的下載腳本不同量級。這是「該不該破例」的判斷,交編排者裁。我依錨判 major,不替它降級。
引句:「測試要的外部工具(ast-grep、detekt、compose-rules 外掛)的版本與雜湊只寫在 .github/actions/test-tools/action.yml,」
file: `.github/workflows/ci.yml:57`、`.github/workflows/ci.yml:141`、`.github/workflows/ci.yml:198`(複製步驟的既有做法),以及 `.github/actions/test-tools/action.yml`(patch 內,新增)

**finding 3:搬家後遺留的「照這步抄」指引跟現況不一致**
severity: minor
blocking: 否
- 新動作檔裡仍保留「★CI 第一個非 pip 的工具下載,以後別的工具照這步抄★」。但這條指引的前提是「複製步驟」,而工具現在已經在複合動作裡。下一個讀的人會不知道該複製這一步,還是加進動作檔。這是上一條第二種做法造成的後果,與 finding 2 同根。
引句:「  # ★CI 第一個非 pip 的工具下載,以後別的工具照這步抄★:下載 GitHub 發布檔 → 比對寫死的 sha256(不符整步失敗)→ 解開 → 放進 PATH。」

不對齊共 3 條,其中 major 1 條

**補充:對圖譜與測試的順帶確認**
- 我查了 `scripts/test_lumos.py` 裡讀 ci.yml 的測試。沒有任何一支依賴原本寫在 ci.yml 裡的 `DETEKT_SHA256` 或 `裝釘版本` 字樣(grep 無結果)。所以抽出動作不會讓既有守衛測試變紅,只是「改版本要同步」這類新的接線也沒有測試守。
- 表態記錄裡的 `py-*` 各題全是 `na`,與這份 patch(CI 設定與筆記,沒有 Python 程式改動)不衝突。我沒有發現可以反駁它們的地方。
