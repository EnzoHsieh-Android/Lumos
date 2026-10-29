severity: major

整體判斷:新子指令的形狀、設定鍵、逃生變數、回傳碼、掛鉤接法都照著筆記形狀擋和存量漂移的做法走,結構是對的。沒有看到計劃明寫要另起一套的地方。但計劃在三個地方沒指名要重用的 helper(剝註解、讀 git、讀設定),另外漏了登記閘名。這些寫實作時很容易長出第二種做法,所以在計劃裡就該點名。

## 1. 分層與依賴方向:對齊,有一處 ⚠

- 新子指令放在 `scripts/lumos` 單檔內,由 `scripts/hooks/pre-push` 以 `"$PY" "$GRAPHCTL" <子指令> --diff … --repo …` 呼叫。這跟 note-shape、home check 同形。
  - file: `scripts/hooks/pre-push:500`
  - file: `scripts/hooks/pre-push:512`
- 掛鉤接法跟鄰居一致:`pp_stop_if_signaled`、rc1 才 `pp_record_block`、其他非零講一句放行。
  - file: `scripts/hooks/pre-push:684`
  - file: `scripts/hooks/pre-push:693`
- 「中斷就停」清單加一行,假 lumos 認得新子指令。
  - file: `scripts/hooks/pre-push:77`
- 計劃寫「接在筆記形狀擋區塊之後、區塊外面、用 `_brange`」,對照代碼審判定的接法。`_brange` 本來就是給會擋的步驟用的。
  - file: `scripts/hooks/pre-push:474`
- CI 第一版不接,跟 Android 端到端驗收同樣只在本機推送時判。
  - file: `scripts/lumos:41949`
- ⚠ **起點的算法有兩種來源。** 計劃說「起點照筆記形狀擋用的 `_lens_push_base` 算;掛鉤傳的是 `_brange`」。但掛鉤註解寫明:note-shape 與 home 用 `_hrange`,存量漂移與回頭重讀不走 `_lens_push_base`,改走 `_push_range_start`,因為它在合過主線時會算錯。
  - file: `scripts/hooks/pre-push:469`
  - file: `scripts/lumos:60954`
  - 計劃要把 `_brange` 當輸入、又在子指令裡再經 `_lens_push_base` 處理一次。這在新分支首推時正好是 `_brange` 已經幫你算過真起點,等於重算一次。結構上沒有第二種做法,但該寫清楚「子指令收到的是 sha 起點,`_lens_push_base` 只做 sha 驗證」,不然會被點跟另一邊不同。
  - 計劃也沒提筆記形狀擋用的 `_nodehome_clamp_base(…, _NOTE_SHAPE_GOLIVE_MARK)` 這種上線點截斷。
  - file: `scripts/lumos:46893`(`cmd_note_shape` 內)
severity: minor
⚠
- blocking: 否

## 2. 命名與錯誤處理:大致對齊,三處缺漏

**對齊的部分**
- 設定鍵 `room_guard.gate` 加 `room_guard.dao` 兩層,跟 `note_shape.gate` 加 `note_shape.test_refs` 同一個模式。
  - file: `scripts/lumos:44224`
  - file: `scripts/lumos:46815`
- 逃生變數 `LUMOS_SKIP_ROOM_GUARD`「只認 1」,跟 `LUMOS_SKIP_NOTE_SHAPE` 同。
  - file: `scripts/lumos:46915`
- 擋下與提醒才記帳、放行不記,淺層 clone 記 skipped-env,也是照筆記形狀擋。
  - file: `scripts/lumos:46930`
  - file: `scripts/lumos:47199`

**缺漏**

**(a) 閘名沒登記進 `_KNOWN_GATES`。** 計劃通篇沒提 `room-guard` 要進 `_KNOWN_GATES`。
- 不在名單上時 `_gate_event` 會印「⚠ …不在 _KNOWN_GATES 名單上」,然後不寫帳。
  - file: `scripts/lumos:1825`
  - file: `scripts/lumos:16015`
- 結果是 S13 的 skipped-env 和 S14 的 warned 都寫不進治理帳,REVISIT 數筆數也會數不到。
- 鄰居每道閘上線都有一行對應(`scripts/lumos:16040` 的 note-shape)。
- 引句:「REVISIT:2027-04-28 數治理帳裡 room-guard 的 blocked/skipped-env/warned 筆數與誤擋比例」
severity: major
- blocking: 是

**(b) 其他註冊點沒列。** 計劃只列了「中斷就停」清單和假 lumos,沒列:
- 掛鉤擋下時的「逃生:…」`echo` 段。note-shape、home、drift 都有。
  - file: `scripts/hooks/pre-push:500`
  - file: `scripts/hooks/pre-push:515`
- 子指令說明字典。
  - file: `scripts/lumos:68085`
- argparse 的 `add_parser`。
  - file: `scripts/lumos:69240`
- skills 裡指令速查的更新。
  - file: `skills/lumos-project-notes/commands/INDEX.md`
- 計劃把逃生語寫在「實務隱患」(要講「這個版本還沒發布可以單次跳過」),沒落到掛鉤的逃生段。
severity: minor
- blocking: 否

**(c) 兩種放行情況的行為沒定。**
- `--diff` 格式錯的 rc2 與訊息(鄰居印「擋下:--diff 要給 <起點>..<終點>…」回 2)。
  - file: `scripts/lumos:46930`
- `_lens_push_base` 回 None 時鄰居記一筆 `skipped`。計劃只說「git 算不出來 → 放行」,沒說記不記帳,也沒說前綴字樣(鄰居是「筆記形狀擋:」,計劃只定了「提醒:」)。
  - file: `scripts/lumos:46958`
- 引句:「不是 git、淺層 clone、git 算不出來 → 講一句、放行」
severity: minor
- blocking: 否

## 3. 第二種做法:計劃沒明寫自刻,但三處沒指名重用,風險高

**(a) 剝註解。**
- 計劃只寫「判斷前先剝掉註解」,沒說用哪支。
- 全庫已有 `_strip_c_comments(txt, blank_strings=False)`,docstring 明寫「全庫只有這一支」,Kotlin 建置檔剝註解也呼叫它。要重用這支,不要另寫正規式。
  - file: `scripts/lumos:6750`
  - file: `scripts/lumos:37056`(`_kt_strip_comments` 也轉呼叫它)
- 引句:「判斷前先剝掉註解(註解裡的 `Migration(1, 2)` 不算)」
severity: minor
- blocking: 否(寫實作前先在計劃補一句重用 `_strip_c_comments`;若實作另寫就升 major)

**(b) 從提交讀檔。**
- 計劃寫「內容全從提交讀」和「一次 `git grep`」,但沒指名 helper。應重用:
  - `_lens_git`(`scripts/lumos:61454`),git grep 鄰居也是經它呼叫(`scripts/lumos:47928`)。
  - `_nodehome_list`(`scripts/lumos:42918`),列終點檔案清單。
  - `_nodehome_reader(root, tip)(path)`(`scripts/lumos:42967`),讀提交裡的檔,含 `.lumos/config.json`。
  - `_lens_full_sha`、`_lens_range_ok`、`_is_git_worktree`,驗範圍與 git 狀態。
- 引句:「內容全從提交讀,工作目錄沒提交的不算。」
severity: minor
- blocking: 否

**(c) 設定讀法。**
- 計劃要一個新的 room_guard 設定解析(`gate`、`dao`、`allow_destructive` 清單)。照 `_note_shape_config(text)`(`scripts/lumos:44224`)的寫法:吃終點提交讀出的文字、壞值回預設並附警告字串,不要另寫直讀工作目錄的版本。
- 不要自己再抄一份「檔案是捷徑就不讀」的檢查。那段已抽成 `_doctor_cfg_bytes`(`scripts/lumos:4397`),`_nodehome_reader` 也已經處理。
severity: minor
- blocking: 否

**(d) 方法對應到改動行。**
- ⚠ 計劃寫「方法範圍跟這次改動的行有交集就算」,需要「每個檔哪幾行改了」。
- 現成的 `_lens_changed_lines`(`scripts/lumos:61682`)回傳的是整體增行清單,不分檔,而且排除測試檔;所以直接用會不夠。
- 要自己跑 `git diff -U0` 的話,至少重用 `_diff_text_lines` 與 `_lens_diff_header` 這兩個解析 helper。
- 我沒讀到任何現成的「檔 → 行區間」函式。若確定沒有才算新增,但不要連 diff 標頭解析都重刻。
severity: minor
⚠
- blocking: 否

## 4. 落點:合理,維持計劃寫法

- **Systems/room-guard 新開:對齊。**
  - 鄰居每道推送前閘各有自己的節點:每支檔有家、存量漂移守衛、筆記內容閘、安全證據閘,都把 `scripts/hooks/pre-push` 和 `scripts/lumos` 列進 `about_code`。
  - 筆記形狀擋本身沒有獨立的 Systems 節點,但 Android 端到端驗收有(`Systems/android-e2e-acceptance.md`)。
  - 所以新閘開一篇、掛 `scripts/lumos` 和 `scripts/hooks/pre-push`,是現有做法。
  - 新節點用 `lumos new system room-guard --code scripts/lumos --code scripts/hooks/pre-push --responsibility "…"` 開。
  - 不要把掛鉤改動寫進別人的家,要用那個家的 `[[連結]]`。
- **Systems/test-quality-cli:對齊。**
  - 它的 `responsibility` 已寫明「另含 lumos-project-notes 的測試品質接入標準文件(各棧撰寫補充)」。
    - file: `docs/lumos-toolchain-knowledge/Systems/test-quality-cli.md:6`
  - 網頁前端那一節就是記在這篇(同檔第 72 行),連綁的測試 `t_test_quality_standard_frontend_section` 的寫法都有先例。
  - Room 一節照抄這個做法,不需另開。
- 計劃的 `lands_in` 兩篇,一篇新開、一篇既有,各歸其位。

不對齊共 8 條,其中 major 0 條。

- blocking 是的有 1 條:閘名沒登記進 `_KNOWN_GATES`,也就是 2(a)。
- 其中 ⚠ 判不準的有 2 條:起點算法(1)、改動行對應(3d)。


## 席位重判(2026-10-28,編排者點出 2(a) 兩欄矛盾後由本席回覆,原文照錄)

2(a) 改判 major、blocking 是:`_gate_event` 對不在 `_KNOWN_GATES` 名單上的閘名會印警告然後不寫帳,計劃漏登記 `room-guard`,skipped-env、warned 和 REVISIT 要數的筆數都寫不進治理帳。統計改為「不對齊共 8 條,其中 major 1 條」,檔級改 major。
