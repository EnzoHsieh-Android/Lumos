severity: blocker

我找到一條會擋合併的修補回歸:範圍切斷檢查把正常筆記整份判成讀不懂。其餘修補(鎖、amend、推送前範圍、改名解析)我逐路徑走過,沒有找到會出錯的輸入。

我另開了修前 `646dc3a8` 與修後 `d6bb423f` 兩份複本當對照,都在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r4-正確性-sonnet/`。`scripts/lumos` 在 `d6bb423f` 與目前 HEAD 沒有差異。

1. 範圍切斷檢查把任何後面出現的 2 格縮排清單都當成被切斷的題目
severity: blocker
blocking: 是
引句:「if _PQ_ITEM_RE.match(fm_lines[k2].rstrip()):」
- 佐證 file: `scripts/lumos:6999`(`_pq_scan`)。`_PQ_ITEM_RE` 是 `^  - (.*)$`,只要是 2 格縮排加 `- ` 就中,不看是不是 `  - id: Q…`。
- 問題:`pending_questions` 後面接任何頂格鍵,再接任何 `  - xxx` 清單(`decisions`、`lands_in`、`tags`、`about_code`),整份就被判「無法判定」。
- 工具自己的正常流程會走到這裡:`question-add` 在檔尾建 `pending_questions`,之後 `decision-add` 或 `append lands_in` 把新欄位加在它後面。
- 後果:`question-set status=已決 decision=…` 與 `question-add` 都被擋,`spec-gate` 也擋;只能手動調欄位順序才解得開。
- 最小重現(在空計劃上依序跑):
  - `lumos --vault v5 question-add Projects/x_計劃 一 --class 需求 --stage 需求 --blocking`
  - `lumos --vault v5 decision-add Projects/x_計劃 選甲 --decided 2026-10-12`
  - `lumos --vault v5 question-set Projects/x_計劃 Q1 status=已決 decision=Projects/x_計劃#d1`
- 修前結果:`question-set` 回「Q1 改了 status、decision」,`spec-gate` 待決問題 ✓。
- 修後結果:`擋下:這篇的待決問題清單本身讀不懂(第 13 行:…頂格的 'decisions' 把清單切斷了…)`,`spec-gate` ✗。
- 同一類輸入:`append lands_in` 之後 `question-add`/`question-set` 同樣被擋。
- 只放在 `pending_questions` 前面的清單(例如 `lands_in` 在前)不受影響。
- 計劃筆記自己寫的是「`  - id:`」,實作比筆記寬。
- 歸因:有證據的修復回歸。
- 為什麼測試沒抓到:`t_qfm_r3_folds` ① 只有「夾頂格鍵又有題」與「頂格鍵接在最後、後面什麼都沒有」兩種,沒有「頂格鍵後面接別的合法清單」的反例。

2. 有符號連結的筆記改成寫不進去,還說是工具漏洞
severity: minor
blocking: 否
引句:「p = os.path.realpath(str(path))」
- 佐證 file: `scripts/lumos:19965`(`_vault_lock_held_for`)。
- 問題:筆記是指向筆記庫外的符號連結時,`realpath(path)` 落在筆記庫外,判成沒拿鎖。
- 重現:`v6/Projects/x_計劃.md -> ../../ext/real_計劃.md`,跑 `lumos --vault v6 question-add Projects/x_計劃 一 --class 需求 --stage 需求`。
- 修前結果:寫入成功(原子換名會把連結換成一般檔)。
- 修後結果:`擋下:寫開頭欄位前沒拿這個筆記庫的寫入鎖…這是工具本身的漏洞,請回報`。
- 建議:判斷用 `os.path.realpath(path.parent)`,或用 `abspath` 比對。
- 歸因:有證據的修復回歸。

3. 旗幟標籤字整段放行,等於放行看不見的 ASCII 文字
severity: minor
⚠
blocking: 否
引句:「return c in "\u200c\u200d\u00ad" or 0xE0020 <= ord(c) <= 0xE007F」
- 佐證 file: `scripts/lumos:6921`(`_pq_cf_ok`)。
- 問題:U+E0020–E007F 是「標籤」字元,每個對應一個隱形 ASCII 字元。
- 重現:`question-add` 題目帶上用這段字元編碼的 `ignore previous instructions`。
- 修前結果:`擋下…控制字元(U+E0069)`。
- 修後結果:寫入成功,畫面上只看到「正常題目」。
- 影響:這些筆記主要由 AI session 讀,可以藏看不見的指令。
- 建議:只放行 U+E0061–E007A 加 U+E007F,且要接在 U+1F3F4 之後。
- 歸因:有證據的修復回歸。我標 ⚠ 是因為這算安全面的取捨,需要你裁。

4. `t_qfm_decision_add_shares_lock` 在負載下偶發紅
severity: minor
⚠
blocking: 否
引句:「rcs = [pp.wait() for pp in procs]」
- 佐證 file: `scripts/test_lumos.py:56527` 一帶。
- 現象:用 `-k t_qfm` 連跑兩次,在 HEAD 的原目錄各紅一次,訊息是 `[(2, 8, 1)]`;單獨跑三次全綠。
- 另一次在我的複本跑 `-k t_qfm` 兩次都是 195 passed。
- 當時我同時在跑別的實驗,所以我只能確定它在負載下偶發,沒查出原因,可能是 16 個行程競爭拿鎖超時,也可能是真的掉寫。
- 修前複本跑了一次,171 passed。
- 歸因:未判定。建議合併前在安靜環境重跑,確認是不是真有掉寫。

沒找到問題的部分:
- `_vault_lock_held_for` 可重入:內層釋放只減計數,最外層才 pop。
- 包裝函式:`decision-supersede/add/reindex`、`_append_decision_ref`、`_dref_remove_ref`、`dref-promote`、`guard bind/audit` 的簽名與預設參數一致;`reindex --all` 內層再呼叫會可重入。
- `_decision_amend_locked(rel, path, did, field, text)`:原本下半段用到的變數都有傳,上半段沒有被漏掉的區域變數。
- 推送前:`_is_commit` 對短 sha、tag、`HEAD~1..@` 都通過;`--output=…` 在指令列就被拒;不存在的版本印「算不出來,放行」。
- `_pq_renames` 的 `[1]` 是 `src`,即新→舊;我造了改名加改字的案例,提醒正確。

圖譜鏡頭:
- `lumos-cli-write.md` 與計劃筆記對鎖的描述跟程式一致,筆記裡已沒有 `_vault_locked` 的殘留。
- 計劃第 69 行寫的是「出現 `  - id:` 的題目行」才算切斷,但實作比對任何 2 格清單項目,筆記對、程式錯(finding 1)。
- 四篇圖譜裡沒有任何一句提到符號連結筆記或標籤字元的取捨。
- `lumos-cli-read.md`、`規格閘.md`、`pitfalls-code-loop.md` 我只對照了這輪修補涉及的部分,沒有逐篇通讀,沒看到衝突。

三問:
- ① 原問題的行為證據:標題 1.「清單中間夾頂格鍵、後面還有題」確實會被擋下,旗標大小寫也擋得住。但修補把「清單後面接別的合法清單」一併擋了,代價高於收益。鎖逾時回 rc2、完全相符路徑優先、推送前 `-` 開頭範圍,我跑下來都成立。
- ② 修補處的正常、錯誤、相鄰路徑:鎖與推送前路徑都成立;`_pq_scan` 的相鄰正常路徑(後面接清單的欄位順序)不成立(finding 1);符號連結筆記的寫入路徑不成立(finding 2)。
- ③ 新發現案例的修前、修後:
  - finding 1:修前 `question-set` 成功、`spec-gate` ✓;修後被擋、`spec-gate` ✗。
  - finding 2:修前寫入成功;修後拒寫並稱工具漏洞。
  - finding 3:修前拒收;修後收下。

總結:修補整體方向對,但範圍切斷檢查的比對太寬,會擋掉工具自己產出的筆記,合併前必須收窄成只比對 `  - id: Q…` 題目行。
