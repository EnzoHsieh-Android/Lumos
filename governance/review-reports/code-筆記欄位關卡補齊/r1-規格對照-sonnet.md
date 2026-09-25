severity: clean

# 規格對照:筆記欄位關卡補齊_計劃 vs r1-snapshot.patch

比對範圍:spec〈條款〉[S1]–[S14]、〈做法〉一~五;diff = `governance/review-reports/code-筆記欄位關卡補齊/r1-snapshot.patch`(618 行,sha256 已核對相符)。逐條裁定如下,14 條全部已實作,無縮水、無未實作、無多做。

## 已實作條款總表(全 14 條)

- **[S1]** 開關 `on` 時,健檢 L 段對整個圖譜跑 lint 錯誤等級規則(原有+新增),有錯擋下並列篇名;L 段原本的解析指紋檢查不變。diff 對應 `scripts/lumos` L 段擴充,新增迴圈於原本的解析指紋 `warn()` 之後、獨立跑 `_nl_bad`。
  引句:「有 {len(_nl_bad)} 篇筆記沒通過 lint 的錯誤等級規則:」
  實跑驗證:`t_doctor_note_lint_gate_on_blocks` 3 案例全過(乾淨圖譜 rc0、新規則抓到擋+列篇名、原有規則(type 不認得)也擋+列篇名)。

- **[S2]** 沒設或 `warn`:新規則提交前只提醒,L 段擴充只提醒不影響退出碼,印篇數與打開方式。
  引句:「整理完可以打開:把 .lumos/config.json 的 note_lint.gate 設成 on,之後推送前就會擋」
  實跑驗證:`t_note_lint_gate_default_warns` 通過(None/warn 兩種情境各驗 lint rc0+提醒、doctor rc0+提示文字)。

- **[S3]** `off`:新規則不跑,L 段印一行說被關了。
  引句:「筆記欄位規則被關了(.lumos/config.json 的 note_lint.gate 是 off),每篇跑 lint 規則這一步不跑」
  實跑驗證:`t_note_lint_gate_off` 通過。

- **[S4]** 值看不懂當 `on` 並印警告;讀不了/JSON壞/捷徑檔/note_lint 非物件當沒設並警告。`_note_lint_config` 逐一對應這幾種壞情境,結構照 `_nodehome_config`(spec〈PRIOR-ART〉指名借用的形狀)。
  引句:「設定檔的 note_lint.gate={g!r} 看不懂(只認 {'/'.join(_NOTE_LINT_GATE_VALUES)}),已用 on」
  實跑驗證:`t_note_lint_gate_bad_config` 通過(看不懂值擋+警告、JSON 壞掉/note_lint 是清單皆當沒設+警告)。

- **[S5]** 帶碰到清單跑,L 段結果與不帶時相同(不讀 `--touched-from`),預告合約段不受影響。L 段擴充迴圈固定跑 `sorted(notes.items())` 全圖譜,不接觸 touched 參數。
  引句:「不讀碰到清單:整個圖譜跑,不動預告合約那段靠 --touched-from 的擋法(r1 接手席)」
  實跑驗證:`t_doctor_note_lint_ignores_touched_list` 通過。

- **[S6]** status 必填(四類型;空白也算沒填),報錯訊息帶允許值,值域與既有 `_STATUS_ENUM` 完全一致(system/project/issue/verification 四組集合逐一比對相同)。
  引句:「沒填 status(寫成空白也算),篩選與健檢各段都靠它判狀態」
  實跑驗證:`t_lint_status_required` 6 案例全過。

- **[S7]** created/updated/date/decided/ended 需年-月-日且是真日期(`_note_date_ok` 用 `date.fromisoformat` 擋 13 月 40 日這類假日期)。
  引句:「而且是真的日期;你寫的是 {str(v)!r}——工具拿它比先後,寫錯會悄悄套錯規則」
  實跑驗證:`t_lint_date_fields_format` 4 案例全過。

- **[S8]** decisions.valid 有寫只能 true/false(不分大小寫),沒寫不算錯。
  引句:「第 {i} 條 decisions 的 valid 只能是 true 或 false,你寫的是 {str(v)!r}」
  實跑驗證:`t_lint_decision_valid_boolean` 3 案例全過(no→錯、FALSE→過、沒寫→過)。

- **[S9]** about_code 每項要是磁碟上的檔且不在圖譜資料夾裡,單一字串當一項(`as_list` 處理),共用 `_about_code_path`(跟寫入指令同一判法,做法段明講要一致)。
  引句:「「{v}」在圖譜資料夾裡,是筆記不是程式檔——要連結別篇就寫進 related」
  實跑驗證:`t_lint_about_code_must_exist` 5 案例全過。

- **[S10]** type=project、檔名以「_計劃」結尾、created ≥ 2026-09-12 要有 lands_in,每項 `Systems/<名>` 純字串(`_lands_in_bad` 共用處置閘那支),指到還不存在的節點不算錯,`_調研`與更早計劃不受影響。
  引句:「計劃沒寫 lands_in(現況要寫進哪幾篇 Systems)——用 lumos append <計劃> lands_in Systems/<名稱> 補上,還沒開的篇也可以先寫」
  實跑驗證:`t_lint_plan_requires_lands_in` 5 案例全過。
  ⚠ 判不準的細節(不影響裁定,附註供參考):實作對「created 欄位本身格式壞掉/缺漏」也視為要補 lands_in(`or not _note_date_ok(created)`),spec 條款只寫「created ≥ 2026-09-12」,沒有明講建立日缺漏或格式錯時怎麼判。這是保守 fail-safe(寧可多驗一次也不漏檢),方向與 S10 精神一致、未見對應測試專門覆蓋此分支,但也沒有其他 spec 條款被違反,故不計入縮水/多做。

- **[S11]** `lumos set responsibility` 用新開節點同一支 `_nodehome_resp_ok` 判斷,不過就擋、檔案不動,不看開關(在 `_cmd_set_locked` 裡先擋,擋在 `_vault_write_lock` 之後、真正寫檔之前)。
  引句:「負責範圍跟新開節點用同一支判斷、同樣擋」
  實跑驗證:`t_set_responsibility_min_length` 通過(太短擋下且檔案原封不動、夠長才寫入)。

- **[S12]** 本 repo 圖譜全篇通過 lint 原有+新增規則,測試不經開關直接跑規則。筆記修正(9 篇 lands_in + 1 篇 Issue about_code)依做法段規定放在獨立提交 `f3a06bab`(已存在於本 repo,先於本次程式提交 `80a2a6da`),不混進本 diff,屬設計刻意安排(回退時筆記不隨程式退)。
  引句:「本 repo 開關 on,558 篇零違規,健檢多花約 0.1 秒」
  實跑驗證:`t_repo_graph_passes_note_lint` 通過(`每一篇都通過`,bad=[])。

- **[S13]** 開關 warn/off 時,lint 原有錯誤等級規則照舊擋(`_lint_collect` 的結果不受 `mode` 影響,只有 `_lint_new_rules` 的結果受 mode 控管)。
  引句:「這次新增、擋不擋看開關的欄位規則(筆記欄位關卡補齊_計劃 S6–S10)」
  實跑驗證:`t_note_lint_gate_does_not_relax_existing_rules` 通過(warn/off 兩種情境下 type 不認得都照舊擋)。

- **[S14]** `lumos append about_code` 與 `new --code` 寫入圖譜資料夾路徑會被擋、檔案不變/不建檔,共用 `_about_code_path`。
  引句:「有一篇 Issue 就是用 append 把一篇筆記路徑寫進 about_code」
  實跑驗證:`t_about_code_writer_rejects_vault_path` 通過(append 擋下+檔案不變、new --code 擋下+沒建檔)。

## 做法段補充查證(非條款,但影響信度)

- 做法三「本 repo 在自己的 `.lumos/config.json` 設 on」:diff 對 `.lumos/config.json` 的變更確實加了 `"note_lint": {"gate": "on"}`。
- 做法五「筆記修正放獨立一個提交」:核對 `git log`,`f3a06bab`(9 檔,8 篇 _計劃 補 lands_in + 1 篇 Issue 把 about_code 改成 related)與程式提交 `80a2a6da` 確實分開,不在本 diff 內,屬 spec 明文要求的安排,不算漏做。
- 開關說明依做法「誠實界線」要求寫在 lint 的家 `Systems/lumos-cli-read.md`:diff 中該檔新增一段 `RULE:[since:2026-09-25]…` 完整涵蓋開關三值、四類 status、日期、valid、about_code、lands_in 規則與 retire 條件,格式符合 CLAUDE.md 對 `RULE:` 行 `[since:]`/`[retire:]`/`[confirmed:]` 的要求。

## 測試實跑總結

以下測試在本機對本 repo 實跑(非讀報告、非憑記憶),全數通過:
`t_lint_status_required`(6)、`t_lint_date_fields_format`(4)、`t_lint_decision_valid_boolean`(3)、`t_lint_about_code_must_exist`(5)、`t_lint_plan_requires_lands_in`(5)、`t_note_lint_gate_default_warns`、`t_doctor_note_lint_gate_on_blocks`、`t_note_lint_gate_off`、`t_note_lint_gate_bad_config`、`t_doctor_note_lint_ignores_touched_list`、`t_note_lint_gate_does_not_relax_existing_rules`(2)、`t_set_responsibility_min_length`(2)、`t_about_code_writer_rejects_vault_path`(2)、`t_repo_graph_passes_note_lint`——共 17 個子斷言(用 `-k note_lint` 一次跑到)+ 逐一單獨重跑 S6–S11、S14 對應測試,合計皆 0 failed。

縮水+未實作共 0 條。
