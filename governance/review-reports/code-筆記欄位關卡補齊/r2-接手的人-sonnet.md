severity: clean

## 審查範圍與方法
在 `/tmp/lumos-r2-review`(`git clone /Users/enzo/harness/lumos-toolchain`,基底 80a2a6da,即第一輪九席折入後的版本)套用 `r2-snapshot.patch`,對每一個「翻紅釘」宣稱做真的突變測試(改回舊寫法、跑對應測試、確認真的翻紅,再還原),不只是讀 patch 相信作者的話。也在乾淨臨時目錄手造壞筆記重現關鍵路徑。全程沒有對 `/Users/enzo/harness/lumos-toolchain` 做任何寫入。

## F1 三個翻紅釘全部驗證屬實(已驗過,沒問題)
- 找根修法:把 `_vault_repo_root(env)` 改回 `_repo_root_from_env(env)`(兩個呼叫點),`t_note_lint_gate_repo_root_layouts` 的②③確實從綠翻紅(monorepo 深層與圖譜即 repo 根兩種佈局讀不到開關,被當 warn)。
  引句:「root 判定=_vault_repo_root(向上找 .git;r2 否決席:vault.parent 在 docs/ 兩層」
- type 寫成清單防呆:拿掉 `_lint_collect` 裡 `if t is not None and not isinstance(t, str):` 那段防呆,`t_doctor_note_lint_survives_malformed_note` 的③(單篇 `lumos lint`)確實丟出未捕捉的 `TypeError: cannot use 'list' as a dict key`,②(`lumos doctor`)因為健檢 L 段自己包了 `try/except Exception` 而沒有當掉——兩層防呆各自獨立生效,不是同一份程式碼重複算兩次分。
  引句:「except Exception as _ex:   # 一篇讀不懂的筆記不能讓整個健檢當掉——列成那篇的錯(代碼審 r1 邊界席)」
- 日期空字串:拿掉 `_lint_new_rules` 裡「寫了卻是空的」那個早退分支,`t_lint_empty_date_is_error` 的②(created 空白 / updated 空白)從擋(rc1)變成 0 問題(rc0),證明原本的 `v is not None and str(v).strip() != ""` 寫法確實會把空字串悄悄放過。
  引句:「if k in n.fields and (v is None or str(v).strip() == \"\"):」
- 設定檔整份非物件:拿掉 `.lumos/config.json` 整份非 dict 的判斷、退回 `data.get("note_lint") if isinstance(data, dict) else None`,`t_note_lint_config_not_object_warns` 三種形狀(`null`/`[1, 2]`/`3`)全部從「當沒設並警告」變回「靜默吃掉、不警告」,證明這條警告不是空話。
  引句:「cfg[\"warnings\"].append(\".lumos/config.json 整份不是物件,筆記欄位新規則用預設(只提醒)\")」

## 已驗過的其他路徑
- `_note_lint_config` 回傳形狀從 tuple 改成 dict(`{"mode":..., "warnings":...}`)後,全 repo 只有兩個呼叫點(`run_doctor` 與 `cmd_lint`),兩處都同步改成 `_nlc["mode"], _nlc["warnings"]`,`scripts/test_lumos.py` 沒有任何測試直接呼叫這支函式期待舊的 tuple 形狀——不會有殘留的舊解包方式讓某條路徑悄悄拿到字典當字串用。
  file: `scripts/lumos:1210-1211`、`scripts/lumos:4835-4836`
- 用真實的 557 篇圖譜跑 `python3 scripts/lumos doctor --ci`(套上 r2 patch 的複本),沒有當掉、L 段照跑,跟 `.lumos/config.json` 現場 `note_lint.gate: on` 一致,收工時是「✓ 圖譜健康 — 0 issues」。
  引句:「本 repo 開關 on,558 篇零違規,健檢多花約 0.1 秒 [test:t_doctor_note_lint_gate_on_blocks]」
- 開頭欄位規則新舊兩批的判定路徑(`_lint_collect` 原有規則 + `_lint_new_rules` 新規則)在 `lumos lint` 與健檢 L 段共用同一份函式,沒有另外抄一份可能各自維護、對不齊的邏輯。

## 我查過但沒有升成發現的一點
健檢 L 段對「讀這篇時出錯」有整段 `try/except Exception` 保底,但 `cmd_lint`(單篇 `lumos lint <節點>`)沒有對等的保底——目前唯一已知會炸的形狀(`type` 寫成清單)已經在 `_lint_collect` 本身修掉,兩條路徑因此都安全,但這是「靠那一處防呆同時頂住兩邊」而不是「`lumos lint` 本身有防護」。我試著另外造壞形狀(`tags` 寫成純量 `5`)想證明還有別的洞會讓 `lumos lint` 崩但 `lumos doctor` 撐住,結果沒有炸(frontmatter 解析層會把它安全吸收)。沒有找到第二個能實際重現的崩潰輸入,所以沒有把這點列成正式發現。
