severity: major

## F1 decisions 的 decided/ended 空字串沒套上這輪新加的「寫了卻空要報錯」規則,跟 created/updated 兩套邏輯不一致

severity: major
blocking: no

這輪的 PITFALL 說法是「日期寫成空字串會繞過日期規則與既有的建立日切點」,對治法是在 `_NOTE_DATE_FIELDS` 迴圈裡新增一段:

引句:「if k in n.fields and (v is None or str(v).strip() == \"\"):」

引句:「out.append(f"{k} 寫了卻是空的——填年-月-日(例:2026-09-25),不需要就整行拿掉")」

但緊接在下面、同一支函式裡驗 decisions 的 `decided`/`ended` 那段沒有跟著補這條防呆,還是原本「空字串直接跳過、不報錯」的寫法:

引句:「if v is not None and str(v).strip() != \"\" and not _note_date_ok(str(v)):」

這是同一種資料(欄位裡的日期字串)、同一支函式(`_lint_new_rules`)裡的兩段幾乎相同的驗證邏輯,這輪修了其中一段卻沒同步另一段,形狀正是任務說明點名的「補丁與原文接縫處的新不一致」。翻紅重現(在 /tmp/lumos-review,已 apply 這份 r2 patch 的複本):

```
cat > testvault/Systems/decisiontest.md << 'EOF'
---
type: system
status: doing
created: 2026-09-25
updated: 2026-09-25
tags:
  - type/system
  - status/doing
scope: platform
aliases: []
decisions:
  - content: test decision
    decided: ""
    ended: ""
    valid: "true"
summary: |-
  KEY:test
---
# decisiontest
EOF
python3 scripts/lumos --vault testvault lint decisiontest
```
實際輸出:`0 error / 2 warning`——`decided`/`ended` 寫成空字串完全沒被抓到,跟同一輪對 `created`/`updated` 空字串「一律報錯」的承諾矛盾;而且 decisions 的 decided/ended 正是「翻案時序比對會讀它」的欄位(patch 註解自己也這樣講),空字串一樣會悄悄套錯規則,風險不比 created/updated 低。

修法:把「寫了卻空」那段判斷抽成一個小函式(或至少把兩處判準寫成同一份),decisions 迴圈也呼叫它,而不是各自維護一份幾乎相同又會走鐘的邏輯。

## 其餘:兩處重複的 isinstance 判準,已看過、不夠格單獨開條

`run_doctor` 的 S6 總索引段這次為了修 type 寫成清單會丟例外的舊坑,在兩個地方各自加了同一句 `isinstance(_ty, str) and _ty in _scope` 的判準(迴圈裡的 `if` 一次、`ok()` 訊息裡重算計數一次):

引句:「if not isinstance(_ty, str) or _ty not in _scope:   # type 寫成清單時拿去查集合會丟例外(代碼審 r1 邊界席順帶抓到的舊坑)」

引句:「isinstance(n.fields.get('type'), str) and n.fields.get('type') in _scope])} 篇節點都列到了」

這個「迴圈判準 + 訊息裡重算同一判準」的雙寫形狀在改動前就存在(改動前兩處都是 `n.fields.get('type') in _scope`,只是沒有 isinstance 保護),這輪只是把新加的防呆同步套進兩處,沒有讓重複本身變嚴重,也沒看到任何一處漏加。實測(見下)兩處保護都生效、算出來的數字一致,不升級成一條發現——但如果以後要再改這個判準,提醒作者記得兩處都要動。

引句:「if not isinstance(_ty, str) or _ty not in _scope:」

## 已驗過、沒問題的部分

`_vault_repo_root` 換掉 `_repo_root_from_env`(圖譜在 repo 根/monorepo 深層兩種佈局)、健檢 L 段對單篇例外的 try/except、`type` 寫成清單時 `_lint_collect` 直接把它當成一條錯誤而不是丟例外、`_note_lint_config` 改回傳字典跟 `_nodehome_config` 同形狀、設定檔整份不是物件時的新警告分支——這幾處都在 /tmp/lumos-review(乾淨複本,已 `git apply` 這份 r2-snapshot.patch)裡實跑過 `python3 scripts/test_lumos.py -k note_lint`(24 案例全過)以及上面 F1 的重現指令驗過行為,沒有另外發現多餘或重複的防呆。`except Exception` 這種寫法在 `scripts/lumos` 全檔出現 163 次,是既有慣例,這輪新增的那一處(doctor L 段)不算新增的複雜度模式。

引句:「except Exception as _ex:   # 一篇讀不懂的筆記不能讓整個健檢當掉——列成那篇的錯(代碼審 r1 邊界席)」
