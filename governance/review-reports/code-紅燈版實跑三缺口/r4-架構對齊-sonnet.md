severity: major

(⚠ 兩條都請編排者定奪:第 3 問的 `_tg_ws_keep_strings` 我判 major,理由是它是 `_tg_ident` 掃描迴圈的複製版,不同處只有內層壓法。`cfg_gone` 那條我判 minor,它也可以算成「第二種認冒號的方式」而升成 major。)

## 1. 分層與依賴方向:對齊

- **`cfg_gone`** 放在 `_spec_gate_push_one` 內,跟既有的 `bad_plat`、`gone` 同一個函式、同一層。它只呼叫手邊的 `methods_for(default)`、`_esc_clean`、`_sh_quote`,都是這個函式本來就在用的。沒有跨層直呼。(`scripts/lumos:16007-16014`;對照 `scripts/lumos:16026-16032`)
- **`_tg_ws_keep_strings`** 放在 `_tg_ident` 正下方,由 `_tg_statements` 呼叫,依賴方向不變。(`scripts/lumos:49042`、`49055`、`49410`)
- **`_ENV_MISSING_WHYS`** 留在 `_RAN_EVIDENCE` 旁邊那一區,從 `_ENV_MISSING_EVIDENCE` 的值導出。它被 `_spec_gate_push_one` 讀取,跟舊常數 `_ENV_MISSING_WHY` 的讀取關係一樣。(`scripts/lumos:68562`、`16044`)
- **`_spec_gate_push_match`** 整支拿掉,`fill.get(t)` 直接取代它,少了一層。這是對齊的方向。

## 2. 命名與錯誤處理:大致對齊,有一處措辭不一致

- **`_ENV_MISSING_WHYS` 與 `_tg_ws_keep_strings`**:`_ENV_MISSING_WHYS` 沿用 `_AGP_DEVICE_MISSING`、`_ENV_MISSING_EVIDENCE` 的具名欄位寫法,`_tg_` 前綴也跟 `_tg_ident` 一致。這兩個名字沒問題。
- **`cfg_gone` 與 `bad_plat` 的結構**:擋與降成提醒的兩分支形狀相同,都是 `not done` 回擋下訊息,`done` 則 `notes.append` 後從清單剔除。
- **`cfg_gone` 與 `bad_plat` 的差別**:
  - `bad_plat` 在迴圈裡邊解析邊收集,迴圈後才判。`cfg_gone` 是迴圈前預先算好,提前 return,並改寫 `tests`。
  - 擋下訊息的句型也不同。`bad_plat` 是「…不在 .lumos/config.json 裡(改名或刪了?);照現在的設定…重跑」。`cfg_gone` 是「…在測試索引找不到;名字帶冒號,多半是…——照…再重跑」。
  - 這些屬於不一致,但結構對,見下面第一條 finding。

## 3. 第二種做法:有 1 條 major、1 條 minor

**Finding 1:壓字串外空白又多一支,掃描迴圈是 `_tg_ident` 的複製版**

severity: major
引句:「        out += [re.sub(r"\s+", " ", text[last:mo.start()]), mo.group(0)]」
佐證:file: `scripts/lumos:49410`

- `_tg_ident` 已經是「用 `_C_STRIP_PAT` 逐個認字串、字串原樣保留、字串外壓空白」的函式。(file: `scripts/lumos:49397-49407`)
- 新函式的逐字結構相同:同一個 `finditer`、同一個略過註解的判斷、同一個 `out`/`last` 收尾。只有內層壓法不同,`_tg_ident` 用 `_tg_ws_fold`,新函式用 `re.sub(r"\s+", " ", …)`。
- 同層的 `_tg_stmt_at` 已經用 `_tg_ident` 當「敘述身分」。(file: `scripts/lumos:49394`)現在斷言敘述走另一支。同一個 `_tg_` 層出現兩套敘述正規化規則:標點兩側空白拿掉,對標點兩側空白原樣保留。
- 鄰居已有的做法是讓 `_tg_ident` 內層壓法可換,或直接沿用。docstring 自己寫「同 `_tg_ident`」,等於承認是同一支掃描。
- 判成 major 的條件是「引入第二種做法」。不判 major 的理由:內層壓法確實不同(`_tg_statements` 原本就用純 `\s+`→空格),不是逐字重寫。⚠ 請編排者定奪。

**Finding 2:單平台下用 `":" in t` 判留痕名字,命名與措辭跟鄰居不一致**

severity: minor
引句:「    cfg_gone = [t for t in tests if not split and ":" in t and t not in methods_for(default)]」
佐證:file: `scripts/lumos:16007`(對照 `scripts/lumos:6484`、`scripts/lumos:6496`、`scripts/lumos:16031-16035`)

- 全庫認「平台:名字」的規則只有 `_split_test_ref_ex` 一處,它在單平台下明講「整串就是名稱,不切冒號」。(file: `scripts/lumos:6484`)新碼在單平台下另外把「名字帶冒號」當成特徵。這不是切冒號,但是另一處讀這個形狀。
- 「找不到」這件事,既有的 `gone`(用 `k == "dangling"` 判,訊息「留痕裡的測試找不到」)是第一條路。`cfg_gone` 預先用 `methods_for(default)` 再判一次,訊息改成「留痕記的測試在測試索引找不到」。提醒文字同事不同寫法(「設定改過?」對「改名或刪了?」)。
- 這是人裁換形狀時刻意取的做法,結構上仍在同一函式內,所以我判 minor。⚠ 它也可以算成「第二種認冒號的方式」而升成 major,請編排者定奪。

## 沒找到不對齊的部分

- `_ENV_MISSING_WHY` 換成集合 `_ENV_MISSING_WHYS`:推送前拿 why 字面比對本來就是舊做法,只是單值變集合。
- 測試新增案例是延伸既有 `cases` 與 `_mp_repo` 套路,沒有新寫法。

不對齊共 2 條
