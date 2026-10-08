# 前置掃描:殺傷力配方失配提醒_計劃

被掃:negguard/docs/lumos-toolchain-knowledge/Projects/殺傷力配方失配提醒_計劃.md
程式:negguard/scripts/lumos(下面 L: = scripts/lumos)、negguard/scripts/test_lumos.py(T:)

## 速覽(各節條數)
① 未定義的詞:5 條
② 壞引用:0 條(2 條備註)
③ 範圍自相矛盾:4 條
④ 機械宣稱驗語意:12 條(其中嚴重 5 條)

---

## ① 未定義的詞

1. 「專案根」(做法1「收(專案根、配方)」、S1/S5)。程式裡有三個不同的根,計劃沒選:`_repo_root_from_env`(docs 的上一層,L:11586)、`_vault_repo_root`(往上找 .git,L:8099)、各平台的 `root`(`load_platforms` 回 `(repo_root/root_str).resolve()`,L:約 6000 一帶,見下 ④-1)。doctor 內 P 段用的 `repo_root` 是 Check C 裡 for 迴圈找 docs 祖先設的區域變數(L:1583-1586),找不到會是 None。
2. 「工作目錄」(做法2「讀工作目錄的檔」、誠實界線「讀的是工作目錄的檔」)。可指 cwd、可指專案根的工作樹(對比 guard kill 的 HEAD 隔離工作樹)。測試都是 `cwd=root`,但程式 kill-add 完全不看 cwd。
3. 「合約 KEY 前 40 字」(做法3 輸出格式)。配方裡存的是 `invariant`(KEY 行的子字串,使用者給的片段),不是完整 KEY;既有 `cmd_guard_kill` 輸出用 `r.get('invariant','')[:30]`(L:約 13340)。「前 40 字」取 invariant 還是回節點找 KEY 行?沒講。
4. 「回頭重讀那次抽出的共用路徑守衛」(做法1)。是指代碼審「回頭重讀」專案,沒有 `[[連結]]`,下一個 session 的 AI 要自己猜;程式碼端 `_repo_path_unsafe` docstring 有「回頭重讀代碼審 r2 架構對齊席 F2」可對上,但計劃沒給節點。
5. 「活節點」(S2)。做法3 定義成「status 不是 superseded/stale」,但 P 段實際還跳過 `type == verification`(L:2887-2889);計劃說「理由同 P 段」卻沒列這條,「活」到底含不含 verification 型沒定。

## ② 壞引用(計劃明說新做的不算)

無壞引用。已驗存在:
- `[[Systems/guard-kill]]` 存在(docs/.../Systems/guard-kill.md;about_code 列 scripts/lumos)。
- `[[Issues/存量筆記漂移三種機制_rtb根因回饋]]` 存在。
- `_kill_read_recipes`(L:12850)、`cmd_guard_kill_add`(L:12886)、`cmd_guard_kill`(L:13143)、`_repo_path_unsafe`(L:26519)、doctor 的 P 段(L:2877)、Check N(L:3012 一帶)、`warn_soft`(L:1354)都在。

備註(不算壞引用):
- a. rtb 端的 `governance/audits/2026-10-01-drift-sweep/findings.md`、`Issues/存量筆記漂移等工具修復〈形狀與修法〉`、rtb 提交 df6ff87 在本 repo 無法驗證;計劃當外部來源引用,尚可,但建議依 CLAUDE.md 加 `[來源:外部]` 性質的說法或把 10 條配方數字就地抄一份。
- b. 計劃寫的 `t_guard_kill` 在程式裡存在(T:20368),但計劃新增的四個測試名(t_guard_kill_add_rejects_drifted_recipe 等)尚未存在——屬新做,不算。

## ③ 範圍自相矛盾

1. 〈範圍·做〉只列三件:抽共用判斷、kill-add 驗、doctor 一段。但〈做法 1〉與 S4 要改 `cmd_guard_kill` 的內部。〈範圍·不做〉也沒寫「不改 guard kill 的判定」。需把「改 cmd_guard_kill 呼叫共用函式、判定與輸出不變」列進〈做〉。
2. 〈回退〉「不提供略過旗標」vs〈實務隱患·既有測試〉「測試要補目標檔」:實際受影響的不只「目標檔不存在」,還有**刻意寫失配配方來測 drifted 的整批測試**(見 ④-9)。沒有略過旗標,這些測試就得改成直接手寫 frontmatter,計劃只說「補目標檔」是不夠的;且〈回退〉也說「擋錯了人…不提供略過旗標」,對「想先登記、之後才改程式」的合法流程(目標檔還沒產生)是死路,只能 revert 整個實作。矛盾點:S1 一刀擋 `outside`/`missing`,但既有測試明確把「宣告不擋,跑時擋」當設計(T:20474 `check("esc kill-add rc0(宣告不擋,跑時擋)"…)`),計劃沒說要推翻這個既有設計裁定。
3. S1 要求 kill-add 對「路徑跑出專案」也拒寫,S4 要求 guard kill「判定與輸出不變」。但 guard kill 對逃逸是 verdict `error`+「逃逸」,不是 drifted(L:約 13262-13266);共用判斷若把 kill 的逃逸也歸成 `unsafe`,輸出會變(見 ④-4)。計劃沒講 kill 端是否先用自己的圍欄再呼叫共用函式。
4. 〈做法 1〉「檔不存在或讀不了 → missing」與「讀不成 UTF-8 的檔算 missing」vs S4「檔開不了的判定與輸出相同」:現有 kill 遇到非 UTF-8 檔會直接崩(見 ④-3),不是 missing/drifted。「相同」與「新增 missing 原因」在這點不可能同時成立(崩潰→drifted 本身就是輸出改變),S4 要明寫例外。

## ④ 機械宣稱驗語意

標 ★ 者為嚴重。

### ④-1 ★ kill-add 驗「專案根」的檔,但配方的 `file` 是相對「配方平台的工作樹」
- 計劃原句:「`lumos guard kill-add` 在寫入筆記之前,對要寫的這一條配方跑共用判斷(讀工作目錄的檔)」;做法1「收(專案根、配方)」。
- 程式實際:CLI 說明寫 `--file` 是「要弄壞的檔(相對配方平台 root)」(L:40130)。`cmd_guard_kill` 是對 `pentry["root"]` 所在 git repo 建工作樹 `git -C proot worktree add --detach wt`,再 `os.path.join(wt, r["file"])`(L:13235-13262);平台由 `r.get("platform") or platform_override or default_plat` 決定(L:13186)。`load_platforms` 多平台時 root 是 `(repo_root/root_str).resolve()`,平台可指向另一個獨立 repo(測試 T:59858-59866 的 `other/` 就是這樣)。kill-add 有 `platform` 參數但目前完全沒讀 config。
- 後果:多平台專案(rtb、有 Android/iOS/Node 多根的專案)用專案根去讀,會把「平台 root 底下才有」的檔誤判 missing 而擋下合法配方;或對不同平台同名檔誤判 ok。S1 的 `unsafe`/`outside` 判斷也要用平台 root 才對。
- 建議改法:做法1 改成「收(平台根、配方)」,平台根 = `load_platforms(repo_root)["platforms"][配方.platform or default_platform]["root"]`;kill-add 要在 config 讀不了(ValueError)、平台不在 config 時定義行為(見 ④-9 的 `zz` 平台測試:現行允許寫入,擋下會讓 T:59877 之後的斷言翻紅)。doctor 段同理逐條取各自平台根,config 壞了就整段退回「這一段算不出來」的 warn_soft 形狀(L:2627 慣例)。另在〈誠實界線〉補一句 kill 讀 HEAD 檢出、本段讀工作樹。

### ④-2 `cmd_guard_kill` 數原文那段的實際寫法
- 計劃原句:「`cmd_guard_kill` 裡那段『開檔、數次數、判 drifted』改呼叫它數次數(工作樹路徑與圍欄照舊由 guard kill 自己管),判定結果與輸出不變。」
- 程式實際(L:13264-13276):
  ```
  with open(target, encoding="utf-8") as _tf: src = _tf.read()
  except OSError as ex: verdict "drifted", detail f"file 開不了: {ex}"
  cnt = src.count(r.get("old", ""))
  if cnt != 1: verdict "drifted", detail f"old 命中 {cnt} 次(需恰 1——配方漂移,重寫)"
  ```
  接著 `src.replace(r["old"], r["new"], 1)` 寫回。數次數發生在 baseline 跑完之後、且每條配方各自一次。
- 要保留的字面:drifted 的 detail 兩種字串「file 開不了: {errno 文字}」「old 命中 N 次(需恰 1——配方漂移,重寫)」;測試 T:20486-20487 斷言 `"命中" in detail`。
- 計劃的共用函式回「(狀態、說明)」,hits 說明「帶實際次數」——若共用函式自己組句,字面會跟 kill 現行不同,S4 就破。建議改法:共用函式只回 (狀態, 次數/錯誤物件),由兩邊各自組句;或明寫 kill 端沿用共用函式的說明字串且該字串逐字等於現行兩句,並在 `t_guard_kill_drift_verdict_unchanged` 逐字比。

### ④-3 ★ 「讀成 UTF-8」與 S4「不變」衝突:現行遇非 UTF-8 會崩潰
- 計劃原句:「讀檔照 guard kill 現在的做法用 UTF-8;讀不成 UTF-8 的檔算 `missing`」+ S4「檔開不了的判定與輸出應跟改之前相同」。
- 程式實際:`except OSError` 只接 OSError。`UnicodeDecodeError` 是 ValueError 子類,不被接住,會整個 `cmd_guard_kill` 拋例外(工作樹由 finally 清掉,但 kill-log 沒寫、其他配方都沒結果)。另外 `open(..., encoding="utf-8")` 是文字模式,會把 `\r\n` 正規化成 `\n`;`old` 含 `\r\n` 的配方永遠 0 次。共用函式必須用同樣的文字模式 `open()` 才「同一支判準」,用 bytes 或 `newline=""` 會與 kill 分歧;同時 kill 的 `_tf.write` 也走正規化,所以兩邊必須一致。
- 另:NUL 字元路徑讓 `open`/`read_text` 拋 ValueError(`Path.is_symlink` 則吞掉回 False),非 OSError。
- 建議改法:S4 加例外說明「非 UTF-8 現行為崩潰,改為 drifted(說明含原因)屬刻意修正」,並在測試釘;共用函式 `except (OSError, ValueError)`(UnicodeDecodeError、含 NUL 路徑)都歸 missing;明寫「文字模式 open、不 newline=''」。

### ④-4 ★ 「沿用 `_repo_path_unsafe`」:參數、回傳能用,但語意比 kill 的圍欄嚴,且不能直接用在 kill 端
- 計劃原句:「`file` 解析後不在專案根底下,或路徑任一層是符號連結 → `unsafe`(不讀檔;沿用…`_repo_path_unsafe`)」;「工作樹路徑與圍欄照舊由 guard kill 自己管」。
- 程式實際(L:26519-26537):簽名 `(root, rel, dirs=False)`,回 `None`(安全)或 `(種類, 出問題那層的 Path)`,種類 `symlink`/`notdir`/`outside`;**OSError 往上拋、呼叫端自己處理**;不存在的層不算錯。可以這樣用,但:
  1. 回傳是 tuple 不是字串,共用函式要自己把 kind 轉成說明;
  2. 計劃沒寫 OSError(`resolve()` 遇 symlink loop、權限)要接;不接 doctor 會整支崩(計劃本身也沒有 try/except 包段落——比照 L:2627/2678 的「這一段算不出來,先跳過」);
  3. kill 的圍欄是 `os.path.realpath(join(wt,file))` 要在 `wt_real+os.sep` 之下(L:13262-13266),**允許** repo 內的符號連結(只要解析後仍在工作樹內);`_repo_path_unsafe` 則**任一層符號連結一律擋**。如果 kill 把「專案根」換成 wt 去呼叫共用函式,repo 內的符號連結配方會由「正常數次數/改寫」變成 unsafe——判定與輸出改變,違反 S4;
  4. 逃逸時 kill 現行 verdict 是 `error`(detail「file 路徑逃逸 worktree(圍欄擋下)」),T:20476、20498 斷言 `"逃逸" in detail`。
- 建議改法:共用函式拆兩段——純「數次數」函式(給 kill 用,收已解析好的路徑)、與「帶 `_repo_path_unsafe` 的完整檢查」(給 kill-add、doctor 用)。S4 只約束第一段。S5 的測試也要寫「符號連結在 repo 內但指向 repo 內」這個差別。

### ④-5 `cmd_guard_kill_add` 的流程與既有判重/covers 更新:計劃沒指定插入點,會改變既有錯誤訊息優先序
- 計劃原句:「寫入筆記之前…跑共用判斷;不是 ok 就印『擋下:<說明>,配方沒有寫入』、rc2」;「只是更新既有配方的 `--covers`…也照驗」。
- 程式實際流程(L:12886-13018)依序:old==new 擋 → covers 清單驗證 → `env.find` → `load_raw_for_edit` → 找 KEY 行(多命中/沒命中擋)→ 解析綁定測試(0/多個擋)→ 組 recipe dict → `_kill_read_recipes`(壞則擋)→ 用 `_kill_recipe_key(str(rel), invariant, file, old)` 逐條比對判重;重複且 `same_rest` 且帶 covers → `updated`(只換 covers),否則「已經有了」擋下 → append → 重寫 frontmatter → `atomic_write_verify`。
- 影響:
  - 驗證點放判重**之前**:重複配方若原文已失配,訊息由「已經有了」變成「原文…」,T:59829-59849 的「④沒帶 --covers 的重複 → 照舊擋下並含『已經有了』」目前原文命中 1 次所以不受影響,但優先序要明定;
  - 放判重**之後**:covers-only 更新分支(`updated` 已設、`break`)是在迴圈內就改了 `r["covers"]`,若驗證在其後,記憶體中的 recipes 已被改但尚未寫入——沒問題但要確保驗證在 `atomic_write_verify` 之前且對 `updated` 路徑也跑(計劃要求照驗,實作易漏:`updated` 路徑沒有 `recipe` 的新 old/file 可驗,要用既有那條的 file/old——與 `recipe` 相同因為身分相同);
  - 「擋下:…配方沒有寫入」要避免與 covers-only 路徑印的「只更新了…」同時出現。
- 建議改法:寫明「驗證放在 recipe 組好、判重迴圈之前;covers-only 更新與新增走同一個驗證」,並新增一條測試釘「重複配方且原文已失配時的訊息」。

### ④-6 doctor 軟提醒 `warn_soft`:每段上限、-v、回傳碼
- 計劃原句:「用 doctor 既有的軟提醒輸出(預設每段最多列 3 條,`-v` 全列)」;S2「不影響 doctor 的回傳碼」。
- 程式實際(L:1354-1371):`_SOFT_CAP = 3`(L:1352);`_verbose = verbose or ci`(L:1351)——**`--ci` 也等於 verbose**(計劃只講 -v);超過的印「… 另 N 條(lumos doctor --verbose 看全部)」。`warn_soft` 只動 `_soft` 計數,不動 `issues`;收尾 `return 1 if strict else 0` 只在 `issues>0` 時(L:3187-3190),軟提醒不影響。計劃主張成立。
- 小問題:(a)REVISIT 要 rtb 回報「`lumos doctor` 這一段的輸出」,預設只看到 3 條 + 「另 7 條」,10 條配方要 `--verbose`(或 --ci);REVISIT 句子要寫 `lumos doctor --verbose`;(b)全部對得上用 `ok()`(不計軟段),沒配方也用 `ok()`——跟「⚠ 提醒」標題並存不矛盾,但 `t_doctor_summary_admits_soft_reminders`(T:36969)在本 repo 真跑 doctor,本 repo 的 canary-audit 有一條配方(scripts/lumos 原文命中 1 次,已實測),新段落不應出 ⚠;若日後那條失配,該測試仍成立(軟段數 = 印出的 ⚠ 段數,走 `warn_soft` 即自洽)。**必須用 `warn_soft` 而不是 `warn`**,否則 issues>0 會讓 `--strict` 回 1,違反 S2。

### ④-7 P 段「跳過 superseded/stale」的寫法
- 計劃原句:「status 是 superseded 或 stale 的跳過,理由同 P 段」。
- 程式實際(L:2886-2890):
  ```
  if n.fields.get("type") == "verification" or \
     str(n.fields.get("status", "")).strip() in ("superseded", "stale"): continue
  ```
  另有 `status_of(env, rel)`(L:732)但只回 str,不 strip。
- 差別:P 段還跳過 type=verification;計劃沒寫。且 P 段是讀全文 + 反引號抽路徑,新段是只讀有 `kill_recipes` 欄的節點(`n.fields` 已含,L:5106 列為已知欄位)——可先用 `"kill_recipes" in n.fields` 篩,免得每篇重讀。
- 建議改法:寫明跳過 `type: verification` 與 `status` strip 後為 superseded/stale,逐字照 P 段;迴圈用 `n.fields` 篩選,只有有欄位才呼叫 `_kill_read_recipes(env.vault/rel)`。

### ④-8 `_kill_read_recipes` 的回傳可能含非 dict 元素,共用函式與 doctor 沒處理
- 計劃原句:「`kill_recipes` 解析不了的筆記也列一條(說明照 `_kill_read_recipes` 回的錯)」;共用函式「收(專案根、配方)」。
- 程式實際(L:12850-12869):只驗「是 JSON array」;元素可以是字串、數字、null。`cmd_guard_kill` 在 `invariant_substr` 篩選處就會對非 dict 呼叫 `r.get` 崩(L:13164)、`for r in recipes: r.get(...)`(L:13189);反之 `cmd_guard_kill_add`(L:12958)與 `_backing_note_recipes`(L:38853)都有 `isinstance(r, dict)` 防線。配方缺 `file`/`old` 鍵、值非字串時 `Path(None)`、`str.count(None)` 都拋 TypeError。
- 建議改法:共用函式入口先判 dict 且 file/old 為 str,否則回新狀態 `malformed`(或併入 `missing`/`empty`,說明寫「欄位格式不對」);doctor 迴圈用 try/except 包整段。

### ④-9 ★ 既有 t_guard_kill* 測試會被新規則擋掉的清單(計劃只提「t_guard_kill 等」)
用 `kill-add` 寫配方、且按新規則會被擋(原文 0 次/多次/路徑跑出專案)的呼叫:
- T:20192、20200、20208(`t_guard_kill_rc_precedence`,T:20177):`--old NOT_THERE`,**刻意**用 kill-add 造 drifted,後面斷言 `kill` 的 rc2 與混批次優先序(3 處)。被擋後那三個 `check` 會因為沒有配方而變成「沒有任何突變配方可跑」rc2,有的巧合仍 rc2,有的(混批次 survived 勝 drifted、弱證據不蓋 drifted)會翻紅或失去意義。
- T:20434(`t_guard_kill`):`--old "LIMIT = 42"`(0 次),T:20435 `check("drift kill-add rc0")` 會紅。
- T:20473:`--file ../../etc/hosts`(路徑跑出專案),T:20474 `check("esc kill-add rc0(宣告不擋,跑時擋)")` 會紅,且後續「kill 圍欄擋逃逸」整段測試失去對象。
- T:20483:`--old "n"`(prod.py 命中多次),T:20484 `check("multi kill-add rc0")` 會紅;後續「殺 M1」無配方可驗。
- T:20495:`--file ../wt-evil/f.py`(兄弟前綴逃逸),T:20496 `check("sib kill-add rc0")` 會紅;「殺 M2」失去對象。
- T:59877(`t_guard_kill_log_new_fields`):`--platform zz`(config 沒有的平台)+ `--old "def check"`;現行 kill-add 不看平台、允許寫入,後面 T:59886 斷言 `set(by_plat)=={"a","b","zz"}` 與 `by_plat["zz"]["verdict"]=="error"`。若新驗證在平台不在 config 時擋下或誤判,會翻紅。另 T:59876 平台 b 的 `other/` 是獨立 git repo、根不同,專案根與平台根在這條剛好都有 prod.py 而僥倖通過(見 ④-1)。
不受影響(目標檔存在、原文恰 1 次):T:20187/20199/20207/20229/20241/20259/20381/20388(重複,仍被判重擋,但優先序見 ④-5)/20395(Naked,先因無綁定測試被擋)/20422/20452;T:59796-59802、59814、59842-59844、59875-59876、59903、59923。
合計:3(rc_precedence)+4(t_guard_kill:drift/esc/multi/sib)+1(log_new_fields 的 zz 風險)=8 處呼叫、3 支測試函式。
建議改法:〈實務隱患·既有測試〉改寫成上面清單;這些刻意失配的配方改成測試內直接寫 `kill_recipes` frontmatter(可沿用 T:59747 `_backing_vault_note` 的做法)而不走 kill-add;「宣告不擋,跑時擋」那兩條(esc/sib)的設計裁定要在計劃裡明講被推翻(圍欄測試改由手寫 frontmatter 造)。

### ④-10 doctor 段落代號:哪些沒用過
- 計劃原句:「代號實作時取一個沒用過的」。
- 程式實際(L:`section(` 逐一列舉):已用 1/4、1.5/4、2/4、3/4、4/4、G、L、M、C、T、R、S、S2–S12、S14、S15、I、A1、A2、E1–E5、Z、H、K、D、V、P、Y、N、J、W、Q、F。
- 沒用過的:B、O、U、X、S13(註:S13 在程式註解與測試名稱中是計劃條款編號,不是 doctor 段落,但 doctor 段落序列 S12→S14 跳過了它,取它容易跟「[S13] 條款」混淆)、S16 之後、K2、P2、Y2 等。
- 建議改法:取 `P2`(跟 P 段同形狀、同依據,擺在 P 之後)或 `K2`,不取 S13。
- 注意 doctor 段落順序:段落是依程式位置印出,不是依代號;P 段在 L:2877、Y 在 L:2949,新段放 P 與 Y 之間最貼近計劃寫的「照 P 段形狀」。

### ④-11 PRIOR-ART「共用 guard kill 已有的 drifted 判準」:判準其實在三個地方各自細微不同
- 計劃原句:「`cmd_guard_kill` 已經有『原文恰好一次,否則判 drifted』的判準,本案把這個判準抽成共用函式」。
- 程式實際:kill 的判準對 `old=""` 的行為是 `"abc".count("")` = len+1 → 0/多次判 drifted「命中 N 次」;對空檔案 + 空 old 則 count=1 → **會繼續套壞法**(寫入 `replace("","x",1)`)。共用函式新增的 `empty` 狀態(S 外的做法1)讓 kill 端對 `old=""` 的輸出由「命中 N 次」變成「empty」;S4 說 0 次/多次/檔開不了相同,沒列 `old=""`。
- 建議改法:S4 明寫 `old=""` 屬刻意改變(或 kill 端對 `empty` 仍用原「命中 N 次」字面)。

### ④-12 「kill-add 寫入配方時不開那支檔」「doctor…都不讀配方內容」:大致成立,有一處漏列
- 計劃原句:「doctor、推送前掛鉤、CI、pitfalls、contracts、guard list/audit/trace 都不讀配方內容」。
- 程式實際:`_kill_read_recipes` 呼叫者只有 L:12951(kill-add)、L:13159(kill)、L:38852(`_backing_note_recipes`,寫表態算背書時把 kill-log 對回筆記現有配方,只取 covers/note,不讀檔不數次數)。scripts/、.github 其他檔無引用。故「不數原文次數」成立;但「不讀配方內容」對表態背書這條不成立(它讀 covers 與 note)。影響:不影響本案,但〈依據〉那句想當「結論相同」的證詞,精確說法是「沒有別處數原文次數」。另注意 kill-add 失配擋下會讓「先登記、後改程式」流程無路,而背書那條讀者仍會把筆記裡已存在的失配配方當有效(本案 doctor 只提醒、不阻止背書)——〈誠實界線〉可補一句。
- 建議改法:〈依據〉那句改成「沒有別處數原文出現次數」。

---

## 三條最嚴重(摘要)
1. ④-1:kill-add/doctor 驗的是「專案根」的檔,但配方 `file` 是相對「配方平台的工作樹」(CLI 說明與 kill 實作都是),多平台專案會把合法配方誤擋、或誤放。
2. ④-9:既有測試被擋的清單遠多於計劃寫的「t_guard_kill 等」:3 支測試共 8 處 kill-add 呼叫(含刻意造 drifted 的 rc_precedence、esc/sib 圍欄、multi、drift、`--platform zz`),且「不提供略過旗標」逼這些測試改手寫 frontmatter,esc/sib 還推翻了既有「宣告不擋、跑時擋」的設計裁定。
3. ④-3 + ④-4:共用函式的 UTF-8/`unsafe` 規格會讓 S4「判定與輸出不變」破功——現行 kill 遇非 UTF-8 是崩潰(只接 OSError)、對 repo 內符號連結是放行(realpath 圍欄)、逃逸是 verdict `error` 不是 drifted;`_repo_path_unsafe` 是任一層符號連結就擋、OSError 往上拋。
