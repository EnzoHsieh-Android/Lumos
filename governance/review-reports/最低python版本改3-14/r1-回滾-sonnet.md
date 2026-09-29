severity: major

# r1 回滾鏡頭(Sonnet)

## F1 「還原提交即可」漏了消費專案副本:掛鉤是複製進去的,還原工具鏈不會動它們
severity: major
blocking: 是 — 不改,回退時只還原工具鏈就以為收乾淨,已更新的消費專案仍卡在新掛鉤,而且沒裝 3.14 的人手上的 vendored lumos 自己也跑不了更新
引句:「還原本計劃的提交即可,沒有資料格式改變」
1. 消費專案的 `core.hooksPath` 指向專案內的 `scripts/hooks`,新版 pre-commit/pre-push 與 `scripts/lumos`(含第 2 點的重跑檢查)是 `lumos update` 時複製進去的工作目錄副本。還原工具鏈 repo 的提交,只改來源;已更新的消費專案照舊用新掛鉤(擋下)。回退節只有〈消費專案〉一條談「沒裝 3.14 的暫時解法」,沒有「回退後每個消費專案要跑 `lumos update` 把舊掛鉤複製回去」這一步。
2. 誰最需要回退:沒 3.14 的機器。但這台機器上專案自帶的 `python3 scripts/lumos update` 已是新版 lumos,在 3.9 下會回 2。只有全域 `lumos`(指向來源、來源已還原)跑得動。spec 沒寫「回退時要用全域/來源那份 lumos 跑更新」。⚠ 全域 lumos 是否一定指向來源,未逐機核對。
3. 更新前被擋期間的暫時出口只有 `LUMOS_PYTHON` 或 `--no-verify`(後者不留帳)。
file: `scripts/lumos:18254`(`_set_hooks_path` 只設 `scripts/hooks`,掛鉤是專案工作目錄副本)
file: `scripts/lumos:17424`(`_vendor_toolchain` 只在 `lumos update`/init 時複製)

## F2 還原後再更新,消費專案裡會留下沒人管的共用檔,被當成專案自己的程式掃
severity: minor
blocking: 否 — 只是殘檔與風險分級偏高,不影響掛鉤運作
引句:「新共用檔要登記進工具自裝檔的精確名單」
1. 新共用檔進了 `_VENDORED_TREE_FILES`;回退後名單少一項,`_vendor_toolchain` 只「複製清單上的檔」,不刪舊檔,消費專案的 `scripts/hooks/` 底下那支共用檔變殘檔。
2. `_vendored_state` 只認名單內的檔名為「原封不動的工具檔」,殘檔不在名單 → 推送閘風險掃描當成專案自己的程式(該函式註解自述為了避免的正是這種歸類)。回退節沒寫要刪殘檔。
file: `scripts/lumos:17450`
file: `scripts/lumos:17225`

## F3 「只回退擋下」沒講完:測試條款、消費專案重發、以及 3.9 機器上其實比計劃前更弱
severity: major
blocking: 是 — 照字面做這條回退,[S3] 的測試會紅、消費專案不會生效,而且沒 3.14 的機器上 lumos 本體仍回 2
引句:「放行是整道檢查不跑,★不是改用 3.9 跑★;其餘保留」
1. 這個回退是改共用檔與兩支掛鉤的行為,但 spec 沒寫要同步翻 [S3] 與 `t_hooks_block_without_python314`(否則守衛測試對回退狀態必紅),也沒寫這個改動同樣得經 `lumos update` 才到消費專案(同 F1)。
2. 「其餘保留」包含第 2 點:機器上只有 3.9 時,`python3 scripts/lumos …` 與安裝入口交接後仍會回 2。半套狀態 = 掛鉤靜默放行、但一切 lumos 指令仍被拒。計劃前的基線是「3.9 找得到就拿 3.9 跑檢查」,半回退比基線弱(檢查完全不跑,治理帳沒寫)。spec 只承認「檢查整個沒跑」,沒寫治理帳也不會有、CI 是否兜底(pre-push 現況文字是「CI 會再跑一遍兜底」,但 CI 已改 3.14)。
3. 放行時要印的提醒內容沒定(現況 pre-push 的提醒寫「找不到 python3 或 lumos」,在「找得到 3.9 卻放行」的情形下字面不成立)。
file: `scripts/hooks/pre-push:70`
file: `scripts/hooks/pre-push:119`

## F4 uv 以外的直譯器搬家與「設定壞了沒人告訴你」
severity: minor
blocking: 否 — 有補救(重跑安裝),缺的是偵測與回頭條件,不會做出錯的行為
引句:「寫進 Claude/Codex 設定的是絕對路徑,搬家後掛鉤會失效,要重跑安裝」
1. `sys.executable` 進設定檔的情形不只 uv:從啟用中的 venv 跑 `lumos install`、pyenv 版本目錄、`LUMOS_PYTHON` 指的直譯器,都會被寫成絕對路徑,消失就同樣失效。spec 只列 uv。(已驗:本機 Homebrew 給的是穩定的 `/opt/homebrew/opt/python@3.14/bin/python3.14`,不受升級影響。)
2. `_prune_dangling` 只剪「腳本檔不存在」的註冊,不看直譯器是否還在;沒有任何檢查(doctor/install)會發現「註冊裡的直譯器已不存在」,「要重跑安裝」全靠人先察覺掛鉤壞了。〈實務隱患〉與〈誠實界線〉承認此風險,卻沒有 REVISIT 或偵測入口(專案鐵則 4:承認風險要附回頭條件)。
3. 重跑安裝確實會遷移:`_equivalent` 只比腳本檔名,內容不同就取代,所以補救路徑成立(已讀碼確認)。
4. 反向:回退節說直譯器路徑「不會自己變回來」,但回退後那條 3.14 絕對路徑仍可執行舊版掛鉤腳本,不重跑也不壞;說法過強,文件精度問題。
引句補:「Claude/Codex 設定檔裡寫進去的直譯器絕對路徑,在使用者機器上要重跑安裝才會換回來」
file: `scripts/merge-claude-settings.py:306`(`_equivalent`)
file: `scripts/merge-claude-settings.py:51`

## F5 「還原提交即可」在有後續提交之後不成立:S7 守衛一起消失,存量漂移防線乙會重新踩 3.9
severity: major
blocking: 是 — 上線後才回退才有意義,此時主線多半已有後續提交,照字面「還原一個提交」會留下不能在 3.9 跑的程式又沒有守衛
引句:「存量漂移防線乙回來收尾時,拿掉它為 3.9 加的事先篩選」
1. 第 9 點規定漂移防線乙合進主線時拿掉 `_drift_py_too_deep`。若之後回退本計劃,那個提交已依賴「最低 3.14」;回退節沒寫這條要一起補回篩選,否則 3.9 的 ast.parse 崩潰(本計劃的起因)原樣重現。
2. 還原本計劃的提交也會還原 [S7] 測試與其它 3.14 專屬條款;回退窗口內其他人寫進 `scripts/lumos`、`scripts/hooks/**` 的 3.10+ 語法,還原不會退掉,回退後 3.9 的可解析性也沒有機械守衛。spec 對「回退後 3.9 又能用」的保證,只寫了「照舊存在」問題,沒寫還原前要先確認窗口內無 3.10+ 語法。
3. 同一提交還含圖譜收尾(Issue 結案、F65、REVISIT 改寫),還原會一併把它們退回;spec 沒說這是預期還是要單獨處理。
引句補:「回退後 3.9 的崩潰與測試總檔的 3.12 寫法問題照舊存在」
file: `docs/lumos-toolchain-knowledge/Projects/最低Python版本改3.14_計劃.md:49`

## 各節已讀
- 範圍、依據、PRIOR-ART/RETIRE-IF、條款 S1–S7 內部交叉引用:已讀,無 finding(本鏡頭只看回退)。
- 實務隱患的「守衛面」「不可逆」:已讀,不可逆一條見 F4。
- 已排除的類別:金流,不適用;併發:回退動作為序列操作,無新增競態;不可逆:git 掛鉤與 lumos 本體皆檔案覆寫可退,設定檔路徑見 F4。

總結:最嚴重等級為 major,blocking 共 3 條(F1、F3、F5)。
