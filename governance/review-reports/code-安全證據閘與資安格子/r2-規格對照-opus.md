severity: major

**1. S9 改寫後要求「校準輸出檔(calibration_path)要在 bindings 裡」,綁定的測試完全沒驗這一半,把這條檢查拿掉測試照綠**
severity: major
blocking: 是

引句:「review(與 deployment)的審查紀錄綁定也要涵蓋家節點 about_code 的程式檔:綁定是空的 → invalid:binding_incomplete;」

- 規格:這一輪依 d18 把 S9 改成「綁定集合少了 … 校準輸出檔(calibration_path,d18) … 應判 invalid:binding_incomplete」。d18 選這個方案的理由是「校準輸出檔已經機械綁定(換了就 stale)」。
- 程式:file: `scripts/lumos:10063` `_secev_bindings_problems` 有做 `need.add(it["calibration_path"])`,行為符合條款。
- 測試抓不到:
  - 綁定的 `t_secev_s09_bindings` 只對四支檔做漏綁比對:src/app.py、tests/test_app.py、tests/fixtures/f.json、Dockerfile。
  - 測試小工具 `_SgRepo.fence_items` 的 `@auto`(file: `scripts/test_lumos.py:104980`)一定會把 calibration_path 補進綁定,所以全測試檔沒有任何一支造出「漏綁校準檔」的輸入。
  - 全檔只有兩處手改 bindings(105348、108168),都沒有拿掉 calibration。
- 本輪新增的 `t_secev_r1_review_bindings_cover_home` 只補了 S9 另一半(review 綁家節點),而且沒綁進 S9 的 `[test:]`。
- 失敗場景:改壞時把上面兩行拿掉,掃描類證據不綁校準檔照樣 qualified;校準檔之後被換,也不會 stale。d18 宣稱的機械守衛等於沒有測試在守。
- 最小重現(在 7655a12d 的 detached worktree 刪掉那兩行):
  ```
  python3.14 scripts/test_lumos.py -k t_secev_s09  → 12 passed, 0 failed
  python3.14 scripts/test_lumos.py -k t_secev_s11  → 4 passed, 0 failed
  ```
- 歸因:有證據的原有漏查。b99f52c8 做同一個改壞,`-k t_secev_s09` 也是 12 passed,兩版 S9 測試的漏綁清單相同。本輪改寫條款時沒有跟著補測試。

**2. 這一輪新加的「讀證據兜底」把程式自己的 KeyError、IndexError、ValueError、AttributeError 也歸成單項 report_malformed,S42 的綁定測試改丟 RuntimeError 繞過**
severity: minor
blocking: 否

引句:「raise RuntimeError("注入的判定錯誤")     # 不是外來資料的型別錯(那種只讓那一項 report_malformed,見 t_secev_r1_type_gate_*)」

- 規格:S42 改寫後只把「讀外來證據時的欄位型別錯」排除在 evaluation_error 之外,這種錯要只讓那一項判 report_malformed,而且要「講出哪一列哪一欄」;其他未預期例外都要擋成 evaluation_error。
- 程式:file: `scripts/lumos:10171` 在 `_secev_item_report` 外面整個接住 `(TypeError, AttributeError, KeyError, IndexError, ValueError)`,一律改判 report_malformed。附的說明只有例外類別名(「讀這份證據時欄位型別不對(KeyError)」),沒講是哪一列哪一欄。
- 失敗場景:判定程式本身的 bug(例如 KeyError)變成單項 invalid。這種結果可以被使用者簽的例外蓋掉而放行;evaluation_error 則是蓋不掉的整道擋。
- 重現:把 S42 測試的注入改成 `raise KeyError("注入的程式內部錯誤")`。
  - 7655a12d:`✗ S42 判定時拋出未預期例外 → evaluation_error 擋`,gate_code=None
  - b99f52c8 做同樣替換:3 passed(判成 evaluation_error)
- 歸因:有證據的修復回歸。這是行為改變,S42 的測試是配合程式改的。

**3. d17 要求 stdin「與」stdout 都是互動終端,測試分不出「與」和「或」**
severity: minor
blocking: 否

引句:「check("人機區分 非互動 → 擋下、說要本人在終端機跑、給可複製指令、不寫入", p.returncode != 0 and "本人在自己的終端機" in p.stderr」

- 非互動那一案用 `stdin=DEVNULL` 加 `capture_output`,兩端都不是終端;偽終端那一案兩端都是終端。
- 把 file: `scripts/lumos:11406` 的 `and` 改成 `or`(只要一端是終端就放過),在 7655a12d 跑 `-k t_secev_r1_approval_add_needs_human_terminal` 結果是 4 passed。
- 「其中一端是終端」這個情況沒有任何一案在測。
- 歸因:未判定。這一型是本輪新增的,修前沒有這段程式。

**4. S52 新加的但書「被推的提交自己設的不採用」,綁定的 `t_secev_s52_mainline` 驗不到**
severity: minor
blocking: 否

引句:「_sg_git(r.root, "checkout", "-q", "main")       # 主線設定只從主線 tip 版讀(被推的提交自己的不採用)」

- 改過的 S52 測試先在 main 上設好,再 merge 進 feat,所以推送版和主線 tip 版的設定一模一樣。改壞成「讀推送版的設定」也分不出來。
- 反向案例只在 `t_secev_r1_mainline_not_from_pushed_config` 裡,而這支沒寫進 S52 的 `[test:]`。
- 歸因:未判定(條款是本輪改寫的)。

**5. S55 條款沒跟著〈三〉改寫:〈三〉已改成「任何工具名被刪或改名都算變弱」,S55 還只寫「刪掉某工具類別的最後一個工具」**
severity: minor
blocking: 否

引句:「變弱比對:主線有、推送版沒有的工具名一律當變弱要核可(改名=刪舊加新)」

- 規格內部不一致:
  - 〈三〉的〈工具清單變弱要核可〉這一輪改成「主線有、推送版沒有的工具名(刪掉或改名)都算變弱」,另外加了「同類別新加的工具也不算登記(`tool_unregistered`)」。
  - S55 條款的文字沒動。
- 程式照〈三〉做:file: `scripts/lumos:10587` `_secev_tool_freeze`。
- 新行為的測試 `t_secev_r1_tool_rename_is_weakening` 沒有綁到任何條款。
- 歸因:未判定(屬於文件不一致)。

**6. 計劃〈五〉回退節還寫「`junit()` 改 iterparse」,跟同一篇〈二〉改寫後的寫法矛盾**
severity: minor
blocking: 否

引句:「拒 DTD 只有 NoDtdTreeBuilder 一處(_JUnitStream 委派給它)」

- 安全主張驗收閘計劃(7655a12d 版)〈二〉的〈深度〉與〈四〉的 test_quality 那一行,這一輪都改成「XMLParser 自訂 target,不用 iterparse」。
- 〈五〉回退 ① 那一句還是「`junit()` 改 iterparse 與帶型別拒收」,沒改到。
- 歸因:有證據的原有漏查(本輪的文件差異只改了前兩處)。

---

**逐條對照:本輪改寫或新增的條款與決策,程式有沒有做到(開碼讀過語意)**
- d17 互動終端加確認碼:file: `scripts/lumos:11400` `_secapr_confirm_human`。先驗整條鏈,再用 `secrets.token_hex(3)` 產確認碼;所有型別都要過這一關;不是 sk- 金鑰只提醒、不擋。成立,缺口見第 3 條。
- d18、S9:程式成立,測試缺口見第 1 條。
- 主線只讀主線 tip 版的設定、只收 `refs/remotes/`、候選裡挑歷史最長的分岔點:`_secev_mainline_pick`、`_secev_mainline_override`、`_secev_config(for_mainline=True)` 都照計劃做。
- 核可鏈曾經有效就永遠只能追加(`_SECAPR_EVER_VALID` 含 approval_expired):成立。
- approval_backdated:只拿有效筆當日期基準,基準單調遞增,等同「不早於前面任何一筆有效筆」。成立。
- revision 的 target 帶 `|decision_ref`:`_secev_revision_ok` 與 `_secapr_c_revision` 兩邊一致。
- consideration 的 outcome 與 30/180 天:鏈上那一層不強制 outcome 欄,但列那一層(file: `scripts/lumos:10994` 附近)照列的 outcome 卡住 30 天與 180 天。成立。
- `target=` 用 urlsplit 取主機、工具清單格式與類別 id 表、`--plan` 讀全文:都跟程式一致。

**抽查 3 條本輪沒改的條款,仍然成立**
- S44:用 committer date(`%cI`)比。
- S58:level 是 note 或 none、kind 是 pass 不算命中。
- S45:warn 要鏈上有內容雜湊相符、狀態 ok 的 gate_setting,過期的不是 ok,照 block 判。

**程式做了、計劃沒寫的**
- pre-push 遇到多個 tag 指同一個提交只判一次;舊版 lumos 略過時印提醒(`t_secev_r1_hook_tags_same_commit_once`)。計劃沒有對應文字。

**三問**
- ① 修復效果的行為證據:有。
  - S42 的單項型別錯、核可鏈只能追加、主線不讀推送版設定、改名算變弱,各有本輪新增、帶前置對照的測試,我讀過斷言,斷言的確實是條款要的結果。
  - 第 1 條的校準綁定沒有行為證據。
  - 新測試裡我只實跑了 d17 的 r1 那一支,其他的沒跑,也沒做翻紅。
- ② 正常、錯誤與相鄰路徑:
  - 第 2 條的兜底改變了相鄰的「內部錯誤」路徑。
  - 其餘修補處的正常路徑,讀碼看起來成立;只實跑了 S9、S11 與 d17 那一支。
- ③ 同一案例修前、修後:
  - 第 1 條兩版同樣測不到。
  - 第 2 條修前判 evaluation_error、修後判 report_malformed。
  - 第 3 到 6 條未判定或屬文件。

**沒驗的範圍**
- `-k t_secev_` 整組沒跑,太慢,一支約 45 秒。
- 寫進 pre-push、CI 的那部分沒驗。
- 席位臨時目錄與 worktree 我已清掉,只剩空的 `/tmp/lumos-seat-work/code-安全證據閘與資安格子/規格對照-opus/` 留給編排者刪。

最嚴重 severity:major;blocking 共 1 條。
