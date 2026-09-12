severity: major

# code-推筆記認家 r2 合約與圖譜一致性複審

方法說明:所有 blocker/major 均在乾淨環境重現——用 `git archive HEAD` 與 `git worktree add` 對 `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh` 建立隔離副本(避開共用 clone 裡另一個未知程序留下的髒改動,見文末附註),在其上跑測試、寫最小重現腳本、實跑評測腳本。

## 1. 「事故·家」的合併顯示只在一條路徑上做,計劃模式派工鏡頭那條路徑反而把「家」資訊整個丟掉

r2 新寫進 `Systems/retrieval-ranking.md` 的說法,把「一篇同時是事故又是家」的顯示行為講成統一規則。但實測 `cmd_impact --file --json`(非 ranked,`cmd_dispatch_lens_spec` 計劃模式用的正是這條路)在節點同時是確認過的家、又是事故觸發節點時,`homes` 鍵完全不輸出這個節點(被 `if _hn in _inc: continue` 排掉),只留在 `incidents` 裡——不是「印成事故·家」,是家的身份整個消失,下游 `pinned.setdefault(node, {"kind": _LENS_KIND.get(kind)})` 也就只會標成「事故」。已用同一支 `scripts/lumos` 實際跑一個「about_code 命中且帶 `pitfall_when: glob:` 」的節點重現:輸出只有 `"incidents": [...]`,沒有 `homes` 鍵。

引句:「事故是最高優先的安全訊號,不能被蓋掉」
file: `scripts/lumos:22140`(`continue # 事故優先,不重複列`,把 home 排除在 `all_homes` 之外)
file: `scripts/lumos:23548`(`picks = [(v, "home") for v in data.get("homes", [])...]`,吃的正是上面被排空的鍵)
severity: major
blocking: 是

## 2. `doctor` S4 段的程式碼註解仍原樣寫著這輪已部分翻案的舊前提,r2 只改了圖譜筆記那一份複本

同一句話(「about_code 只做固定席排序不做連結是 2026-08-23 甲案收窄,設計正確」)在 r1 被抓到出現在 `Projects/消費專案接入靜默失效_計劃.md`,r2 已經在那篇補上「已部分翻案」的括號說明。但一字不差的同一句話,在 `scripts/lumos` 的 `doctor` S4 段落裡,以程式碼註解形式獨立存在一份,r2 完全沒碰它,現在讀那段程式碼的人看到的仍是未加註的舊斷言。用 `git show 09567f39^:scripts/lumos` 對照確認這行在功能落地前就存在、r1/r2 兩輪的 diff hunk 範圍都沒覆蓋到它。

引句:「現在會直接進必推名單,不再只是排序」
file: `scripts/lumos:1462`(`# 理由:about_code 只做固定席排序不做連結(2026-08-23 甲案收窄,設計正確);`,未加任何翻案註記)
severity: major
blocking: 是

## 3. G14 新寫的「整詞比對」規則排除了英數邊界字元,卻沒把 `/` 算進邊界,完整路徑仍會被子路徑誤判成「有提到」

`_home_mentions` 修的是「新掛 a.py、正文只寫 xa.py」這種裸檔名子字串誤判(已用測試釘住),但邊界字元集 `_HOME_MENTION_BOUNDARY = re.compile(r"[A-Za-z0-9_.@+\-]")` 不含 `/`,所以完整路徑比對時,`/` 前導字元會被當成「非檔名字元」放行邊界檢查。實測 `_home_mentions("實作在 lib/src/pay.py 裡", "src/pay.py")` 回 `True`——node 正文其實提到的是另一支檔 `lib/src/pay.py`,卻被判定「有提到 src/pay.py」。影響面是 [S15] 的「正文沒提到」提醒(只提醒不擋),不影響 `_home_confirmed` 的保送判定(那條走的是另一套精確比對)。

引句:「命中位置的前後要是非檔名字元(或字串邊界)才算」
file: `scripts/lumos:17802`(`_HOME_MENTION_BOUNDARY` 字元類不含 `/`)
severity: minor
blocking: 否

## 4. A4 的驗證數字實跑可重現

在 `/tmp/lumos-wt`(HEAD=7df7abd0 的乾淨 worktree)分別用 `LUMOS_IMPACT_HOME=0` 與 `=1` 跑 `governance/eval/retrieval_eval.py --ablation`,兩次的固定席噪音都是練習題 11 條、保留題 39 條、全體 50 條,逐位數字相同,跟留痕引的數字一致。

引句:「旋鈕關/開各跑一次,必推噪音練習題 11→11、保留題 39→39,完全一樣。」
severity: clean
blocking: 否

## 5. G6 的變異驗證屬實

把 `_impact_mark_home` 裡 `lane_raw.remove(lane)` 那行換成 `pass` 後,重跑 `t_impact_home_moves_out_of_lane`,斷言③(「不會同時留在參考道」)確實翻紅,驗證後已還原程式碼、diff 為零。

引句:「變異驗證:拿掉搬移那行現在會翻紅」(引自 r1-intake.md 第 44 行)
severity: clean
blocking: 否

## 6. 24 條 → 17 組的折入紀錄逐條核對,沒有找到「只寫留痕、程式碼未動」的情況

逐一對照 r1-intake.md 列出的 G1–G19、A1–A4 與 r2-snapshot.patch 的 diff hunk,19 組 G 全部對應到可辨識的程式碼或圖譜筆記改動,A1–A3 的折法(A1 寫成程式碼旁註解、A2 收窄 `--lumos` 路徑、A3 換用既有 git 包裝)也都對得上實際 diff;新增測試(`t_impact_about_max_has_floor`、`t_impact_repo_files_reads_bytes`、`t_home_audit_lumos_path_must_be_inside` 等)在乾淨環境全數通過(`-k home` 318 passed,另外三支個別執行亦全綠)。

引句:「以下全部折進真碼,並各自補了會翻紅的測試。」(引自 r1-intake.md 第 35 行)
severity: clean
blocking: 否

---

附註(非本報告的 finding,不計入編號):審查途中發現共用 clone `/Users/enzo/.claude/jobs/9e5c5b9b/tmp/clone-nh` 的工作目錄裡,`scripts/lumos` 有未提交的髒改動,把 r2 已修好的兩處「★家★」空白拼接(`cmd_impact`、`cmd_impact_diff` 的印表行)又改回黏字串的寫法。比對 `git show HEAD:scripts/lumos` 確認 HEAD 本身是乾淨、正確的——這份髒改動不在 r2-snapshot.patch 裡,懷疑是另一個並行程序在同一個共用目錄留下的痕跡(跟現有圖譜的「同工作區 git add 的夾帶風險」是同一類環境風險),已用乾淨副本繞過,不影響上面各條 finding 的結論,但提醒編排者:提交/推送前務必用 `git status`/`git diff` 再核一次這份共用 clone 目前是不是乾淨的。
