severity: minor

整合席結論:這份文件修補跟 47434676 版程式對得上,沒有 major。我只找到 1 條 minor,是文件內部數字自相矛盾。

## 1. Verification 筆記裡同一件事有兩個不同的耗時數字
severity: minor
blocking: 否

引句:「核可鏈恰 2000 筆全驗章 23.8 秒、82 MiB」

同一篇 `Verification/2026-10-20_安全證據閘與資安格子實作驗證.md` 裡有兩個數字:
- 這份修補新增的段落寫 2000 筆全驗章 23.8 秒。
- 該篇沒動的上一段(patch 的 context 行)仍寫「2000 筆最壞約 13 到 20 秒,留其餘判定的時間」。

`scripts/lumos` 的 `_SECAPR_MAX_ENTRIES` 上方註解也還是「約 13 秒」。

- 影響:23.8 秒超出舊段的 13–20 秒。後面的 REVISIT 又以「單次超過 30 秒」為門檻,讀的人分不清哪個才是現況。上限本身 2000 沒有錯。
- 歸因:未判定。我只讀文字,沒有重跑效能量測。這是這一輪新增的段落跟舊段落不一致。
- 查證:`git show 474346765e:docs/lumos-toolchain-knowledge/Verification/2026-10-20_安全證據閘與資安格子實作驗證.md`,grep「13 到 20」與「23.8」,兩處都在。引句已回 `r3-repair-docs.patch` 用 grep 確認逐字相同(含標點),命中 1 處。

## 已驗主張
- **`[test:]` 綁定**:三篇筆記(驗收閘計劃、提問分階段計劃、`Systems/安全證據閘`)共 82 + 24 + 25 個 `[test:]` 名稱,在 `scripts/test_lumos.py` 裡全部找得到。驗收閘計劃的 S1–S66 每條都有 `[test:]`,提問計劃 S1–S22 同樣。
- **lint 與健檢**:五篇改到的節點 `lumos lint` 都是 0 問題。`lumos doctor` 是 0 issues(917 篇)。d17、d19 的決策欄位用 yaml 解析正常,`lumos decisions` 也讀得到。
- **文字對程式**:
  - 核可鏈筆數上限 2000(`_SECAPR_MAX_ENTRIES`),超過整道判 `read_incomplete`。
  - 新增的判定代碼 `receipt_source_unmapped`、`fault_unrelated`、`receipt_source_changed`、`approval_backdated` 都在程式的代碼表裡。
  - S64、S65 的判定邏輯跟 `_secev_tq_source_problems`、`_secev_tq_relevance` 一致。
  - `payload` 的旗標 `--outcome`(只收 `risk_accepted` 與 `not_applicable`)、`--reason`、`--content-file`、`--commit`、`--key`、`--out` 都存在。到期上限也對:`risk_accepted` 30 天、其餘 `consideration` 180 天。
  - 互動終端:`security-approval-add` 要求 stdin 與 stdout 都是終端,驗鏈通過後才問確認碼。`sk-` 開頭的提醒也是照程式寫的。
  - 「五道」跟 `code-loop check --keep-going` 的實作一致(安全證據、合約測試、表態、新增告警、代碼審留痕)。
  - `junit()` 用 `XMLParser` 自訂 target、不用 iterparse,跟 `scripts/test_quality.py` 一致。
  - 核可日不准回填、主線鏈「有過有效筆(含已到期)就只能追加」,跟 `_SECAPR_EVER_VALID` 與 `_secapr_verify` 一致。
  - `security evidence` 與 `security approvals verify` 都會印有效金鑰指紋。
  - golden README 描述的結構(`s1`、`s59`、`s59_ok`、`s8` 底下有 `plan_text`、頂層有 `source_commit`)跟 `golden.json` 實際一致。
- **筆記規則**:承認風險有回頭條件。「待使用者裁」那段附 `REVISIT:2026-11-30`,golden 的撤除條件接到 `Systems/安全證據閘` 的 `REVISIT:2027-04-30`。摘要行前綴都符合。
- **跨筆記矛盾**:確認碼只擋 `security-approval-add` 這件事,在 d17、d19、計劃〈工具的天花板〉、Systems、skill `commands/06`、程式註解與 `limitations` 的說法一致。我 grep 全庫沒有殘留「確認碼擋得住刻意偽造」的舊說法。

## 未驗範圍
- Verification 筆記裡的測試項數(`-k secev_` 520 項等)、各項耗時與記憶體,以及「翻紅 25 種」,我都沒有重跑,不能證明。
- S38 的符號連結測試只覆蓋背書檔、核可鏈檔、`.lumos/` 三種。`docs/` 層是連結的情況沒有測試,文字說「任何一層」。這是覆蓋範圍,不是行為錯誤。

## 三問
- 原問題修復效果:文件層面的行為證據是 S64、S65、S66 等新增條款各有存在的 `[test:]`,條款文字跟程式實作吻合。我沒有重跑這些測試,所以不能說「測試通過因此問題解決」。
- 修補處相鄰路徑:非互動、單端終端、符號連結先於確認碼、`consideration` 的 30/180 天分流,文字跟程式對得上。
- 新發現的前後對照:發現 1 是文件內部不一致,修補前後我沒有各跑一次,歸因未判定。

我沒有碰那把鎖(`dispatch-lens/af483a76….json.warming`,內容 PID 5918)。我的臨時 worktree 已移除。

最嚴重 severity:minor,blocking 共 0 條。
