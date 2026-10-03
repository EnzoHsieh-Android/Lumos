severity: major

# 代碼審 r3(末輪)通才席 — opus

審材:`r3-delta.patch`(第二輪修正差異,173 行,逐 hunk 讀完);對照 `scripts/lumos`、`scripts/test_lumos.py` 真代碼與 `.github/workflows/ci.yml`。
實驗一律在 `git clone --shared` 的臨時目錄 `scratchpad/r3opus` 裡做,做完已 `git checkout` 還原;repo 本身沒動。

## F1 長檔名測試在 Linux CI 上會因檔名超過 255 位元組而例外失敗

severity: major
blocking: 是
引句:「long = "Verification/" + "長" * 140」
file: `scripts/test_lumos.py:66242`(新測試 `t_doctor_check3_long_name_hint_intact`)
file: `.github/workflows/ci.yml:11`(`runs-on: ubuntu-latest`,全套在這裡跑)
file: `scripts/test_lumos.py:60305`(既有前例 `"docs/" + "a" * 145 + "/" + "b" * 145`:刻意拆兩層、每層 ASCII 145 位元組,避開單層上限)

1. 這支測試建的檔名單一層是 `長`×140 + `.md`,UTF-8 是 **423 位元組**(`python3.14 -c "print(len(('長'*140+'.md').encode()))"` → 423)。
2. Linux ext4(GitHub ubuntu-latest 的 `/tmp`)的單層檔名上限是 255 **位元組**;macOS APFS 算的是字元數(本機 `getconf NAME_MAX` 是 255,但實測 `長`×140 寫得進去、`長`×256 才報 `[Errno 63] File name too long`)。所以本機與推送前的閘都綠,推到 CI 那一刻 `write()` 的 `p.write_bytes(...)` 會丟 `OSError: [Errno 36] File name too long`,整支測試記成 EXCEPTION → 那一片紅 → CI 紅。
3. 最小重現(模擬 ext4 的位元組上限,手上沒有 Linux 機器,真 Linux 未跑):
   ```
   # scratchpad/ext4sim.py:把 pathlib.Path.write_bytes 包一層,任一路徑段 > 255 位元組就丟 ENAMETOOLONG,再 runpy 跑 test_lumos.py
   cd <clone> && python3.14 <scratchpad>/ext4sim.py -k long_name_hint_intact
   ```
   結果:`✗ t_doctor_check3_long_name_hint_intact EXCEPTION: [Errno 63] File name too long: '.../kg/Verification/長長…長.md'`,`0 passed, 1 failed`。不包這層照常 `1 passed`。
4. 建議改法(已在臨時目錄驗過兩向):照 60305 行的前例拆成兩層,例如 `long = "Verification/" + "長" * 80 + "/" + "長" * 60`(每層 ≤ 243 位元組)。驗證:
   - ext4 模擬下:`✓ ①長檔名:改法完整、照貼後參數等於登記原字面`,`1 passed`;
   - 把 `sr_extra` 那段改回第二輪「整行一起 `_esc_clean(…, _DOCTOR_LINE_MAX)`」的寫法:`✗ ①長檔名…`,`0 passed, 1 failed`——拆層後仍然對這次修的症狀翻紅,不會空轉。

## 看過沒問題的

### 照貼指令只清控制字元、不截斷(修正①)
引句:「+ "改法:" + _esc_clean(f"lumos remove {_drift_sh(sys_rel[:-3])} verified_by {_drift_sh(a)}", 100000)」
- `_esc_clean` 只把 `< " "` 與 `\x7f–\x9f` 換成空白,`_drift_sh` 產生的引號(`shlex.quote` 只用 `'` 與 `"`)不在這個範圍,不會被改動;反斜線也不碰。新測試照貼後 4 個參數等於登記原字面,證實引號完整。
- 登記值含控制字元時:實測 `verified_by: - "[[Verification/V]]\t"`(引號內尾巴一個 tab),doctor 印 `lumos remove Systems/B verified_by '[[Verification/V]] '`(tab 變空白),照貼跑真 `lumos remove` → `✓ … 拿掉了`、rc=0,檔案正確清掉。比對不中時 `cmd_remove` 本來就「不命中一律 rc=2」,不會誤刪別項;控制字元在單引號內也不會被 shell 執行。沒找到會出錯的具體輸入。
- 說明那半照舊截在 `_DOCTOR_LINE_MAX`,截斷落在「改法:」之前,不會截進引號。上限 100000 對檔名(單層 ≤ 255)實際等於不截;只有 `verified_by` 寫了超長別名才可能碰到,屬刻意構造,不列。

### warn 的封頂在 --verbose/--ci 全列(修正②)
引句:「shown = list(lines) if (cap is None or _verbose) else list(lines)[:cap]」
- 閉包取值時機:`warn` 定義在 `_verbose = verbose or ci` 之前,但 Python 閉包是呼叫時才讀外層變數;`warn` 的第一次呼叫在 1/4 段,遠在指派之後,`run_doctor` 內也沒有再改 `_verbose`(grep 只有定義一處、讀兩處)。不會 NameError。
- 沒帶 `cap` 的呼叫端:`cap is None` 短路成全列,跟改前一樣;全 repo 帶 `cap=` 的 `warn` 只有 sr_bad 這一處,其他段行為完全不變。
- 結尾措辭改成「另 N 項(lumos doctor --verbose 看全部)」,既有斷言 `"另 5 項" in sec`(66059 行)仍是子字串,照綠。
- 翻紅驗證:把 `or _verbose` 拿掉,新測試 `①--verbose 全列 25 項` 紅。

### _system_ref_blank 與混合清單(修正③)
引句:「items = raw_items if any(not _system_ref_blank(x) for x in raw_items) else []」
- 實測 `parse_frontmatter` 對各寫法讀出的值與判定:`""`→空、`null`/`"null"`→空、`~`→空、`- #comment`→`'#comment'` 空、`"#Systems/B"`→空、`"　"`(全形空白)→`strip()` 後空、`[[Systems/C]] # note`→不算空(交給 `_typed_link_target` 判成「不是單一連結」)。
- `#Systems/A` 這種被當空項:結果是照樣列為寫壞、算 issue,不是默默放行;只是原因寫「空的項」而不是「不是單一連結」,但改法字串「拿掉,或寫成 [[Systems/X]]」對它仍然正確。給不出會讓人修錯的具體場景,不列 finding。
- 常見的整行註解 `  # - "[[Systems/B]]"` 根本不會被 `LIST_ITEM_RE` 當成一項,不受這次改動影響;只有 `- # …` 這種 YAML 本來就算 null 項的寫法會被報,跟 `""` 一致。
- 混合清單每項只報一次:空項在 `_system_ref_item` 開頭就回「空的項」,`bad.append` 一次;`items` 非空所以不會再加「讀不出任何一項」。全是空的 → `items=[]` → 只報一條「讀不出任何一項」,與計劃〈做法〉2「清單本身一項都沒有」那句一致。
- 其他消費端(1/4 孤兒推薦、`sync-verified-by` 的 `n_bad`、3/4 多掛的 `not dec[1]`)讀的是同一個 `bad`,混合空項現在會讓多掛提醒對那份紀錄閉嘴、sync 多一句「有 N 項寫壞」,都是既有「有壞項時」的路,沒有新分支。
- 翻紅驗證:把 `_system_ref_item` 開頭的空項判斷拿掉、`items` 改回第二輪的過濾寫法,`③空項混在好項裡也報空的項` 紅。

### 測試會不會空轉
引句:「check("③空項混在好項裡也報空的項", "空的項" in sec, sec[-500:])」
- 三處修正逐一改回第二輪寫法(已清 `__pycache__`)後跑 `-k doctor_check3`:`①--verbose 全列 25 項`、`③空項混在好項裡…`、`①長檔名…` 三條紅,`26 passed, 3 failed`;還原後 `29 passed, 0 failed`。新測試不空轉(F1 是平台問題,不是空轉)。

### 圖譜鏡頭
引句:「# 說明照行長上限清;照貼的指令只清控制字元、不截斷(代碼審 r2 通才席:長檔名會被截在引號中間,照貼卡在續行)」
- 派工單尾端只有 `LUMOS-IMPACT:` 一行、沒附固定席筆記,依規不逐條答。自跑 `lumos impact --diff e594a964..HEAD`:直接命中 `Projects/驗收紀錄寫明驗了哪些功能_計劃`(1.00),其〈實作紀錄〉已補 r2 一行,寫明三件修正,與代碼一致;〈做法〉2「清單本身一項都沒有 → 讀不出任何一項」與修正③的「全是空的才算」對得上。`lumos search "檔名 長度 位元組 Linux"` 沒有關於 ext4 檔名位元組上限的 PITFALL,F1 修完值得補一條(測試檔名每層要 ≤ 255 位元組,macOS 本機驗不出)。

最高等級:major,blocking 共 1 條
