severity: major

## 對照組

- `governance/eval/refresh_labels.py`(`_atomic_write_json` / `_goldset_lock`)——寫同一批 governance/eval JSON 資產的既有慣例。
- `scripts/lumos`(`_write_lf` / `atomic_write_verify`)——全庫寫檔的唯一原語,兩輪代碼審才收斂出目前形狀。
- `governance/eval/build_goldset.py`(`search_pool` / `edit_pool`)——組候選池的既有實作,拿來跟新加的 `rebuild_pool` 比語意。
- `governance/eval/retrieval_eval.py`(`_labels_of` / `collect_unjudged`)——「什麼叫已標註 / final=None 算未標」的權威定義。
- `scripts/test_lumos.py`(`mkvault` / `_mk_eval_fixture` / `_need_src`)——既有測試夾具與守門慣例。

---

## 發現 1:原子寫入重犯了這個專案已經修過兩次的同一個坑(固定暫存檔名、且無鎖)

引句:「tmp = path.with_suffix(path.suffix + ".tmp")」

新加的 `write_json_atomic()`(`governance/eval/retrieval_eval_multiword.py` 內,對應本次 diff 新增段)用**固定**的暫存檔名(`<path>.tmp`),寫完才 `os.replace`,寫入前後都沒有任何鎖。

這正是本專案在**同一批 governance/eval 資產**上已經真的踩過、也已經記錄下來的那個坑,不是理論風險:

- `governance/eval/refresh_labels.py:51-57` 的 `_atomic_write_json` 明文寫著「★單次寫入原子性；跨進程互斥另靠 `_goldset_lock`(code-r1 資源席：**固定 tmp 名+無鎖曾實測出「一方標註靜默消失+另一方假成功」**)★」,暫存檔名帶 `f".tmp.{os.getpid()}"`(`governance/eval/refresh_labels.py:56`),外面還套一層 `flock` 互斥鎖(`governance/eval/refresh_labels.py:61-79` 的 `_goldset_lock`)。
- `scripts/lumos:11054` 的 `_write_lf`(全庫寫檔的唯一原語)同樣寫著「★暫存檔名每次都不一樣★(2026-09-10 代碼審 r3 併發資源席：原本同一篇筆記大家用同一個固定暫存檔名，兩個程序同時寫就互搶，實測六個同時跑六個都噴 `FileNotFoundError`)」,暫存檔名帶 `{pid}-{uuid4()[:8]}`(`scripts/lumos:11060`)。

也就是說,這個專案已經在兩個不同的地方(核心 CLI 一次、governance/eval 標註寫入一次)分別用代碼審抓到「固定暫存檔名」這個形狀,並各自留下事故紀錄;新碼寫的 `write_json_atomic` 沒有沿用任何一份,而是重新長出第三份,而且形狀正好退回到已知會出事的那個版本。

`--rebuild-pool` 的輸出路徑是呼叫端給的一個一般路徑(常態上會是 `governance/eval/multiword/mw-pool.json` 這種會被覆寫、可能被另一個 session/另一次跑重疊到同一個檔名的共用產物),不是每次都保證唯一。兩個程序同時對同一個輸出路徑跑 `--rebuild-pool`(這個 repo 的日常正是常有多個 session 同時在動同一批檔——見 `docs/lumos-toolchain-knowledge` 裡「同工作區 git add 的夾帶風險」「改共用檔要原子寫入」這類已記錄的併發事故),會直接重演 `refresh_labels.py` 註解裡那句「一方靜默消失+另一方假成功」。

severity: major
blocking: 是

判準:這屬於「會弄壞資料」的一類——而且不是新風險,是這個專案已經用代碼審清楚定案過「必須帶唯一暫存檔名(+視情況上鎖)」的既有做法,這次沒有照做,等於重新引入一種本庫已經付過學費的第二種原子寫入寫法。

---

## 逐項比對其餘五項(未發現第二種做法)

**1. 組候選池的語意**——拿 `governance/eval/build_goldset.py` 的 `search_pool`/`edit_pool` 對照 `rebuild_pool`。`build_goldset.py` 的池是「legacy 片語命中 ∪ ranked 排序前 N」,兩個來源都經過 lumos 自己的排序器,服務的是另一份 goldset(單詞/編輯類查詢)。`rebuild_pool` 特意設計成「現行系統 top10(經排序器)∪ 逐詞出現次數 top3(不經排序器)∪ 三詞同篇 top10(不經排序器)」,目的是緩解 pooling bias——這個設計不是這次新發明的,`retrieval_eval_multiword.py` 檔頭的「誠實邊界」段落(diff 裡是既有的、未改動的 context 行)在這次改動之前就已經寫著「池的第三來源是逐詞出現次數 top-3,不經 BM25F,是獨立來源」,而且這個三來源設計能追到 2026-08-03 那次手工建池(commit `d3fdd470`)。也就是說,這次只是把本來就存在、且服務於不同題目(pooling bias 緩解 vs. 單詞/編輯 goldset)的既有設計**formalize 成程式**,不是為同一個問題另開一份語意不同的實作。判 clean。

**2.(見上,判 major)**

**3. 讀標註檔**——`load_labels` 的「已判 = `final` 不是 None,`final is None` 一律當未標而不是 0 分」跟 `retrieval_eval.py:107`(`_labels_of`)、`retrieval_eval.py:246`(`collect_unjudged`)的權威定義完全一致(`n not in lab or lab[n].get("final") is None` ⟺ 未標)。新加的「扁平格式」與「含各評審意見格式」都是真實存在於 `governance/eval/multiword/` 底下的既有檔案形狀(`mw-labels-flat.json`、`mw-labels-final.json`),不是新發明的第三種語意;「題庫外殼」形狀(`{search, edit, labels}`)也對得上 `refresh_labels.py` 的 `apply` 產出形狀。判 clean。

**4. 出聲方式**——退出碼沿用既有 `return 2` = 用法/前置條件錯誤的慣例(跟 `refresh_labels.py`、`retrieval_eval.py` 裡一票 `ERROR:` / rc2 一致)。污染檢查的訊息是「發生什麼→為何在意→處置」三段,形狀對得上 `retrieval_eval.py:224-230`(unjudged 閘的訊息,同樣是「發生什麼→為何在意→下一步」三段);差別只在這裡的下一步是「去改筆記」而非一行可貼的指令,所以沒有獨立成一行指令可比——但這不是新引入的第二種訊息慣例,是同一慣例在沒有現成指令可給時的自然寫法。判 clean。

**5. 常數與旋鈕**——`POOL_SALT` 放在模組層級常數,跟 `build_goldset.py` 的 `SALT = "lumos-retr-v1"` 同一種放法;`term_top(term, n=3)` / `cooccur_top(terms, n=10)` / `[:10]` 這幾個「前 N」都是函式內的行內字面量或預設參數,跟 `build_goldset.py` 的 `[:8]`、`[:12]`、`"--top", "8"` 同一種寫法(該檔也沒有把這些數字抽成模組常數)。判 clean。

**6. 測試**——四支新測試都用 `_need_src("governance/eval/...")` 守門(跟既有「來源 repo 專用產物」慣例一致,消費端會 skip 不會假紅);新夾具 `_mk_mw_fixture` 用 `tempfile.mkdtemp(prefix="gctl-mw-")` 再把 vault 包成 `root/"kg"` 的巢狀私有 root,跟 `mkvault()`(`scripts/test_lumos.py:92`)、`_mk_eval_fixture`(`scripts/test_lumos.py:26741`)同一種「私有 root 包住 vault」寫法,前綴 `gctl-mw-` 也跟 `gctl-evalfx-`、`gctl-deinit-proj-` 等既有前綴同一族;斷言一律走既有的 `check(name, cond, detail)`。沒有另外造一套既有已有的輔助函式,也沒看到既有 fixture 可以直接複用卻沒複用的情形(`_mk_eval_fixture` 是帶 git repo 的另一種用途,跟這裡不需要 git 的多詞 vault 不是同一件事)。判 clean。
