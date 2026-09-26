severity: major

## F1 引號規則另起一套,沒有沿用 fmt_scalar/fmt_list_item 的既有慣例
severity: major
blocking: yes
引句:「值裡有雙引號就改用單引號包;兩種都有就擋」

專案裡「把一個值格式化成 frontmatter 能讀回來的寫法」一直只有一種手法:`fmt_scalar` 與 `fmt_list_item` 都是「需要引號就用雙引號包、內部雙引號用反斜線跳脫」(`v.replace('"', '\\"')`)。新加的 `_fmt_cond` 卻另外發明一套:優先雙引號、但值裡有雙引號就整個換成單引號包、兩種都有才擋下——這個「單引號當備援」的寫法在全檔案裡是唯一一處(`grep "'" + v + "'"` 只有這一行)。更微妙的是,`_list_key_scalar_to_list` 那邊已經明講「讀的一側不解反斜線」所以改寫時要原封不動保留原引號,等於是已知 `fmt_scalar` 那套反斜線跳脫本身讀不回來、是帶著已知瑕疵在用;這次沒有把這個認知回頭修 `fmt_scalar` 或抽成一支雙方共用的「安全引號」函式,而是關起門來為 COND_KEYS 另開一條新規則。結果同一個檔案裡,同樣是「值要不要加引號、加哪種引號」這件事,純量欄位一套邏輯、`valid_under`/`revalidate_when` 又是另一套邏輯,以後改引號規則要記得改兩處還可能改漏一處。

## F2 欄位不存在時的插入位置寫死找 tags,沒有沿用 edit_fm_scalar 「插在第一個 list/block 欄位之前」的通用規則
severity: minor
blocking: no
引句:「at = struct["tags"][0] if "tags" in struct else len(fm)」

`edit_fm_scalar` 對「這篇筆記還沒有這個欄位」的處理是通用規則:掃過 `fm_structure`,插在第一個 `list`/`block` 型欄位之前(不管那個欄位叫什麼名字)。新的 `_set_conditions_locked` 卻寫死只認 `tags`:`at = struct["tags"][0] if "tags" in struct else len(fm)`。如果一篇筆記的開頭欄位順序是先有別的清單欄位(例如 `related`)才接 `tags`,`edit_fm_scalar` 會把新欄位插在 `related` 之前,這支新函式卻會插到 `tags` 前面(也就是 `related` 之後)——同一個「筆記還沒有這欄」情境,兩支功能定位相同的函式給出不同的插入位置,沒有共用同一條規則。功能上不算錯(兩邊都是合法 YAML),但屬於「有現成寫法卻另開一套」。

已看,無:`_cmd_set_locked` 對純量分支(非 COND_KEYS)照舊呼叫既有的 `edit_fm_scalar`/`fmt_scalar`/`atomic_write_verify`,沒有繞過;`_set_conditions_locked` 用 `load_raw_for_edit` + `fm_structure` + `atomic_write_verify` 這條既有的行級手術管線,寫後自驗也照 `atomic_write_verify(path, ..., key, lambda f: _conds(f.get(key)) == vals)` 的既有慣例(跟 `cmd_set`/`cmd_append`/`cmd_remove` 一樣的三段式:算新內容 → 寫入 → 讀回驗證)。CLI 參數把 `value` 從單一值改成 `nargs="+"`,雖然全庫多值輸入慣例大多是「逗號分隔一個字串」(`--capture-counts`、`--refuted-set`),但 `--folders nargs="+"` 也有先例,且 `set` 本身语意就是給位置參數而非旗標,用 `nargs="+"` 沒有明顯更差,不算違規。錯誤訊息風格(「擋下:發生什麼,檔案沒動(為什麼在意/怎麼做)」)跟全檔數十處 `擋下:` 訊息的既有寫法一致,包含把指令範例放進括號裡這點也有前例(如 `lumos search <關鍵字> 可以找`)。測試命名 `t_set_condition_fields_*`、`t_set_other_keys_single_value_only` 跟鄰近的 `t_set_status_syncs_tag` 命名風格一致,也用了既有的 `mkvault`/`write`/`run`/`check` 測試骨架與 `_load_lumos()` 反射讀內部函式的既有手法。圖譜筆記(計劃節點的 WHY/PRIOR-ART/RETIRE-IF/條款/回退/實務隱患/誠實界線 結構,`lumos-cli-write` 的摘要 WHY 行、commands/03 表格新增一列)都照專案既有格式寫,沒有另創格式。SCALAR_KEYS/LIST_KEYS 兩份既有白名單本身沒被誤動,`COND_KEYS` 獨立成另一個常數也跟既有的 `LINK_KEYS`(LIST_KEYS 的子集、也是 tuple)手法類似,不算新花樣。
