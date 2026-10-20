severity: major

固定席筆記:這次沒附(鏡頭計算超時),沒有固定席條目可逐條答。我手動看了這份 diff 動到的圖譜節點:`Systems/bound-tests-gate`、`lumos-cli-read`、`pitfalls-code-loop`、`test-quality-cli`、`情境出題`、`規格閘`,加上新的 `安全證據閘` 與 `資安威脅類別表`,以及兩篇計劃和 `commands/06`、`08`。「沒有被這份 diff 破壞」只限於下面兩項。第一,每條 `[S]` 條款綁的 `[test:]` 都真的存在,兩篇計劃的 `spec-gate` 匯總是 63 條與 22 條全綠(我在 detached worktree 實跑)。第二,威脅類別表的漂移測試 `-k sectt` 9 項全綠,表格正本與程式裡的鏡像常數一致。其餘破壞見下面的條目。

**1. 核可鏈的主線前綴保護:主線鏈沒有任何 ok 筆(含只是過期)時,推送版可整條換掉,只印一行警告**

severity: major
blocking: 是

引句:「主線版的鏈從第一筆起就沒有任何有效金鑰」

計劃〈核可鏈〉的驗證步驟 2 把「整條換掉」限定在「主線版從第一筆起就沒有有效金鑰」(第一次釘金鑰時壞掉)。〈工具的天花板〉另寫「全部金鑰都遺失或過期時,工具沒辦法自救」。

file: `scripts/lumos:9327` 的實際條件是 `main_chk` 裡沒有任何一筆 status 為 `ok`。`approvers_init` 到期後 status 變成 `approval_expired`,不算 ok。所以 730 天沒續期之後,主線鏈就被當成「從沒有效過」。

重現(我寫的 `exp1.py` 呼叫 `_secapr_verify`,金鑰用 ssh-keygen 現造):
- 主線鏈:使用者的 `approvers_init`,到期日 2025-12-01,今天 2026-10-20。
- 推送鏈:另一把金鑰 `ai` 自簽的 `approvers_init`。
- 輸出:
  - `main alone: [(1,'approval_expired')]`
  - `diverged: False entries: [(1,'ok')] keys: ['ai'] warn: [...推送版整條換掉(第一次釘金鑰的信任前提)]`
- 結果:`approvals_diverged` 沒有擋下,推送版換成 AI 自己的金鑰並成為唯一有效金鑰,之後它自簽的例外和 gate_setting 都算數。

這跟文件的保證相反:文件說到期之後誰都簽不了,實際是任何人都能把整條鏈換掉。只有一行警告,不擋。

**2. `security approvals payload` 自己印的簽法說明,照做會得到 `approval_signature_invalid`**

severity: minor
blocking: 否

引句:「`lumos security approvals payload <type> <target>`（唯讀）印出要簽的那一筆」

`commands/06` 的那一列有寫 `--out <檔>`,計劃〈怎麼加一筆〉沒寫。工具 stderr 印的是「簽這一份:`<上面那份存成的檔>`」,讀起來像是把 stdout 轉存成檔就行。

重現:
- 把 stdout 轉存(`> p.json`)的檔會多一個結尾 `\n`,用 `--out` 寫的檔沒有。
- 簽前者再跑 `code-loop security-approval-add`,輸出「擋下:這一筆接上之後驗不過(approval_signature_invalid),不寫入」,exit 1。
- 簽 `--out` 的檔,同一個金鑰就成功追加。
- 錯誤訊息列了常見原因,但沒有「結尾換行」這一項。

**3. 文件給的操作寫法或格式不完整,照寫會失敗,或要翻程式碼才知道怎麼寫**

severity: minor
blocking: 否

引句:「`security approvals payload approvers_init approvers --key <公鑰檔>…` 印出內容」

file: `scripts/lumos:64192-64205`。實際必填 `--signer` 與 `--expires-on`,`--key` 的格式是 `<principal>=<公鑰檔>`。照計劃的寫法跑,exit 2 並說「要帶 <type> <target> --signer…」,但沒提 `--key` 格式。

另外三處:
- 計劃寫「另有四份不在圍欄裡的受版控檔,格式也在本篇定」,但 `.lumos/security-tools.json` 的格式沒有文件。程式要求頂層 `{"schema_version":1,"tools":[…]}`,每列必填 `name,category,version,install_source,verify,decision_ref,budget,allowed_targets`。`category` 的值是程式內部 id(`test_runner`、`fault_injection`、`load_test`…),`coverage_proof` 的值是 `sarif_invocation`、`semgrep_paths_scanned` 等,`min_requests` 是以腳本路徑為鍵的物件。這些 id 在計劃、`Systems/安全證據閘` 與 `commands/06` 都查不到,只有類別中文名。寫錯時的錯誤只說「工具類別不認得」。
- 核可鏈每筆的鍵清單(「不准有未列的鍵」)沒有 `outcome`,但程式對 `consideration` 會寫 `outcome`,not_applicable 的 180 天上限就靠它。
- `exception`、`human_review` 的 payload 內容是從 HEAD 提交算的,所以要先提交;`target` 也有固定寫法(`<護欄id>#<kinds排序>`)。`commands/06` 兩樣都沒講。

**4. 計劃寫 `junit()` 改用 iterparse,實作與另一篇筆記都說不是**

severity: minor
blocking: 否

引句:「JUnit 的 `junit()` 改成用 `xml.etree.ElementTree.iterparse` 邊解析邊數深度」

file: `scripts/test_quality.py:159-236` 實作是 `ET.XMLParser(target=_JUnitStream())`。`Systems/test-quality-cli` 同次新增的一節寫「C 版解析器的 iterparse 不收自訂 builder,所以不用 iterparse」,跟計劃正文直接矛盾。計劃正文(〈二〉、〈四〉要跟著改的地方)應改成 XMLParser target。

**5. 加了第五道閘,但「四道/四個獨立判定」的敘述沒跟著改**

severity: minor
blocking: 否

引句:「OK/BLOCKED + 原因,四個獨立判定」

這句在 `commands/06` 的「我現在推得上去嗎」那一列,是這次沒改的 context 行,同列還寫「`--keep-going` 四道都判完」。同樣沒改的還有:
- `Projects/推送前一次列出全部擋下原因_計劃` 的「四道判定(合約測試、表態、新增告警、代碼審留痕)都跑完」。
- `skills/lumos-code-loop/SKILL.md:13`、`reference.md:612`。
- `Systems/pitfalls-code-loop.md:241`。
- `Systems/bound-tests-gate.md:152`。

`commands/01-進場查脈絡.md:11` 的 `security list` 一列也沒提 `--all`、`--questions` 或格子。

**6. 兩篇計劃的現況描述過期,跟自己的狀態、決策與實作矛盾**

severity: minor
blocking: 否

引句:「這份只寫設計，不寫程式、不改 CI 或推送行為、不在任何專案安裝工具、不執行故障或壓測」

- 主計劃 `status: doing`,條款全綠,卻仍寫「只寫設計」。
- 主計劃的決策編號說明寫「本篇自己的決策寫 d1–d10」,實際到 d16。
- 主計劃〈二〉的〈表還沒核可時〉仍寫類別表是「設計提案」、「`scripts/lumos` 還沒有鏡像常數,2026-10-20 查」,並說閘門照宣告判、不擋。這跟 `Systems/資安威脅類別表`(`status: done`、d1 已核可)以及程式的 `_SECTT_APPROVED={1}` 矛盾。
- 同一計劃的 REVISIT 結案句稱「只宣告 behavior 的真實樣本見測試…」,但那是合成 repo 的測試,不是真實樣本。
- 姊妹計劃也有同類殘留:「這份只寫設計,不改程式」、Q2 寫「12 類」(實為 14)、「實作時從本篇〈二〉搬過去」。

**7. 給消費專案的 doctor CI 範本只加 tag 觸發與一個工作,沒提其他工作也會被 tag 觸發**

severity: minor
blocking: 否
⚠ 未能重現(沒有真實 CI 可跑)

引句:「其他工作加 `if: github.ref_type == 'branch'`，因為現有 code-loop gate 步驟的 `BEFORE` 在新 tag 是全零、語意沒驗過」

計劃自己承認這是必要措施。file: `scripts/lumos:51283-51302` 的 `_SECEV_CI_STEP` 範本只教加 `tags: ['*']` 與 `security_tag`。消費專案照貼之後,它既有的 push 工作會對每個 tag 以全零 BEFORE 跑,範本沒提醒要給那些工作加 `if`。

**8. `Verification/2026-10-20_安全證據閘與資安格子實作驗證` 的「殺傷力抽查 12 種壞改動、11 種翻紅」沒有可回查的清單**

severity: minor
blocking: 否

引句:「對閘門造 12 種壞改動(例如同種類好的證據蓋掉壞的、JUnit 不數深度、核可鏈不驗前綴),11 種有測試翻紅」

只列了三種例子,沒有指向帳或腳本,三個月後無法重驗,也無法確認「格子吃交叉積是等價改動」這個判斷。

**Lens 3(「擋/核可」句子有沒有對應程式路徑)**
- 其餘「擋」的宣稱我都對到了程式路徑與測試:
  - gate 設 warn 要有核可鏈上的 `gate_setting`(S45)。
  - `--security-only` 非 0 一律擋(S32/S60)。
  - 沒登記的專案輸出不變(S1)。
  - 判定出錯或逾時走 `evaluation_error`/`evaluation_timeout`、不放行(S42/S60)。
  - 例外的 30 天上限與過期(S23/S25)。
  - 核可鏈的重放、刪筆、跨專案(S48,以及我自己跑的前綴實驗)。
- 條目 1 是唯一「宣稱擋得住、實作漏了」的路徑。
- S32 的 CI 半邊只用字串比對檢查 `ci.yml` 的形狀,沒有真實 CI 跑過。這點 Verification 的「沒驗到的」已誠實列出,所以我沒另立條目。

最嚴重:major,blocking 共 1 條。
