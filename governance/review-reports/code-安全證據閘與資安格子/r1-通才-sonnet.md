severity: major

圖譜鏡頭:這次沒附固定席節點(鏡頭計算超時),派工詞說不用自己補算,所以沒有逐條答。

我讀完了整份 r1-tests.patch(3250 行),並用 `scripts/hooks/pre-push` 與 r1-lumos.patch 追了呼叫端。沒有實際跑 `python3.14 scripts/test_lumos.py`,所以下面的「重現」都是靜態推演加指令輸出。

**1. 「跟改動前逐字相同」的對照基準在 CI 與合併後會失效,三支守衛測試變成空轉或誤紅**

severity: major
blocking: 是

引句:「base = _sg_git(repo, "merge-base", "HEAD", "Lumos/main", check=False) or "HEAD~1"」

這行在 `_sg_old_lumos`,S1(`t_secev_s01_no_registration_unchanged`)、S8(`t_secq_s08_s11_existing_unchanged`)、S59(`t_secev_s59_junit_rejections_unchanged`)都用它取「改動前的主線版」。

- `Lumos/main` 是這台機器上遠端的名字。CI 的 checkout 是 `origin`,沒有這個 ref。`merge-base` 失敗後 `_sg_git(check=False)` 回空字串,於是退成 `HEAD~1`。
- 分支上有兩個以上提交時,`HEAD~1` 已經含新碼。新版跟自己比,S1、S8、S59 永遠綠,抓不到「沒登記的專案輸出被改了」或「JUnit 拒收訊息被改了」。這幾支守衛的承諾(「文字輸出與退出碼跟改動前逐字相同」)就沒人在守。
- 合併進主線之後,本機 `Lumos/main` 追上來,`merge-base` 等於 `HEAD`,基準變成它自己,一樣空轉。往後有人刻意改了無登記專案的輸出,這幾支測試不會紅,等於守衛失效。
- 淺層取得(`HEAD~1` 不存在)時,`git show` 的 stdout 是空的,會寫出一支 0 位元組的 lumos 去跑,測試誤紅。
- 重現:在 `/Users/enzo/orca/workspaces/lumos-toolchain/security-gate` 目前這台機器上,`git rev-parse --verify -q Lumos/main` 回 `d42840cf…`、rc=0,所以本機看起來正常。把 ref 名換成不存在的就會退成 `HEAD~1`。這點我是從程式推演,沒有真的在 CI 上跑出紅燈,因此嚴重度保持 major,但請以實跑確認。
- 建議把基準固定成 `git merge-base HEAD <遠端主線>`,並在拿不到時讓測試明確失敗或略過,不要靜默退成 `HEAD~1`。

**2. `t_secev_s18_real_push_stale` 與 `_SgRepo` 預設證據含寫死日期 2026-12-01,過日期後真推送的對照組會變紅**

severity: minor
blocking: 否(未能重現,依派工詞自降一級)

引句:「"judgments": list(_SG_JUDG), "expires_on": "2026-12-01",」

- `_SgRepo.review_item` 的 `expires_on` 與自動補的 `human_review` 核可(`expires_on="2026-12-01"`)都寫死。
- S18 的對照那一次(完整有效的證據,預期 `rc == 0` 且輸出含「必驗集合 1 條都 sound」)是真的推送,跑的是真掛鉤、真今天(UTC)。
- 其他大多數測試用 `today=_dt.date(2026, 10, 20)` 凍結日期,不受影響。S18 是少數吃真日期的測試之一。
- 2026-12-02 起,S18 對照會因 `stale:review_expired` 被擋,測試在日期過後無故變紅。同樣吃真日期的 S24,審查證據不在範圍內,所以它要到 2027-12-01(`approvers_init` 到期)才有問題。
- 建議 S18 的到期日用「今天加 N 天」算出來,而不是寫死。

**其他角度的結論**

- 角度 2(被刪掉的行為):`t_skill_mentions_resolve` 改成逐層往下走子指令,原本守住的「這一層有子指令,後面那個小寫詞就該是子指令名」(外家席:`lumos guard madeup`)在新迴圈裡仍然保留(`wrong = True; break`)。我沒找到被拿掉的不變式。
- 角度 2(中斷測試):`t_prepush_interrupt_stops_every_gate` 補上 tag 推送。實測掛鉤清單列了 `code-loop|安全證據判定(--security-only)`,測試用 `"security-only" in name` 選到它,而且假 lumos 補了旗標字樣。這部分我沒找到問題。
- 角度 3(跨檔追蹤):`validate_suite_counts(root)` 改成 `validate_suite_counts(st.suites)`,r1-lumos.patch 的簽名與呼叫處同步改了(約第 5100~5109 行),`test_test_quality_cli.py` 兩處字串也對上,沒有呼叫端被弄壞。
- 角度 1(逐行):S43 的「子程序數 < 200」只數 `subprocess.run`,但 `_secev_git` 底層走的是 `_lens_git`。我沒有讀 `_lens_git`,所以沒法斷定它是否繞過計數。若它改用別的呼叫方式,這個斷言就量不到。這點給不出具體失敗情境,所以不列為 finding。

最嚴重 severity:major,blocking 共 1 條。
