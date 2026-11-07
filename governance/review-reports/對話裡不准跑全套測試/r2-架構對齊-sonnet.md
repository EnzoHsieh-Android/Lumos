severity: major

以下四問都以我讀到的程式為準。

## 1. 分層與依賴方向

結構對得上。`scripts/test_lumos.py` 本來就用 `_load_lumos_inproc`(`scripts/test_lumos.py:240`)載入 `scripts/lumos`,依賴方向是測試執行器讀 lumos 的工具函式。判斷點接在位置參數併進 `-k` 之後、`_fanout_wanted` 之前(`scripts/test_lumos.py:49674-49677`),跟既有擋下的位置一致。`CLAUDECODE` 在判斷後才拿掉,放在 `main()` 開頭清 `GIT_*` 的那段之外(`scripts/test_lumos.py:49617-49620`)。這個順序有明講理由,沒有分層問題。本問沒有發現。

## 2. 命名與錯誤處理

## F1 理由門檻是第三種寫法,而且少了字元類檢查
severity: minor
blocking: 否
引句:「理由去空白後至少 10 個字才算數(不夠照擋並講要寫理由)」
佐證: `scripts/lumos:41861`(`lint-waive` 的 `len(re.sub(r"\s","",note)) < 10 or not re.search(r"[^\W_]", note)`)、`scripts/lumos:47129`(同樣只數去空白後的字數)、`scripts/lumos:73519`(`_dispositions_reason_ok`:CJK 至少 10 個或總字元至少 25 個)
專案裡已經有兩套理由門檻。計劃用的是 47129 那套。它少了 41861 那道「至少要有一個字母或文字字元」的檢查,所以 10 個標點也能放行。另外,計劃有寫擋下訊息「不含逃生門變數名」,這點對得上鄰居;但「帶理由才放行」是環境變數形式,鄰居的理由是 `--note` 參數。逃生門用環境變數放行是對的(`LUMOS_SKIP_*` 全是環境變數)。差別只在理由判斷沒有說明沿用哪一套。

## F2 三成門檻會新寫一個字面 0.3
severity: minor
blocking: 否
引句:「三成沿用 `_keys_suite_select` 既有的「太泛」門檻」
佐證: `scripts/test_lumos.py:58`(`def _keys_suite_select(tests, keys, cap=0.3)`,0.3 是預設參數,沒有具名常數)
計劃說「沿用」,但沒說怎麼沿用。0.3 只是預設參數,不是常數。選完後的判斷要在 main 裡再寫一次 0.3,就有兩處字面值。口徑也不同:`_keys_suite_select` 是每個關鍵字各自選中占全部的比例,計劃是選中支數的聯集占全部的比例。`--suite keys` 已經先丟掉太泛的單一關鍵字,所以再套一次會有部分重複。⚠ 計劃沒寫是否抽成具名常數,所以判不準。

## 3. 第二種做法

## F3 計數檔是第二套快取寫入,位置也不照既有慣例
severity: major
blocking: 是
引句:「追加一行 JSON 到 `~/.cache/lumos/full-suite-guard.jsonl`(時間、種類、argv、理由)」
佐證: `scripts/lumos:62015-62045`(`_drift_m1_ledger_miss`:追加 jsonl 的既有先例,有 `_mkdir_trusted_under_home`、`_trusted_private_dir`、`O_NOFOLLOW`、`O_NONBLOCK`、確認是自己的一般檔、短寫判失敗)、`scripts/lumos:69244`(`_home_cache_write`:`~/.cache/lumos/<subdir>/` 底下一律先驗目錄)
- 專案寫 `~/.cache/lumos/` 的慣例是放子目錄,再逐層建目錄並驗目錄可信。計劃把檔放在 `~/.cache/lumos/` 頂層,沒有子目錄。
- 計劃只說「寫不進去就略過」,沒說走既有的目錄驗證與寫入函式。
- 執行器入口早於 `_isolate_environment`,真 HOME 還在,所以在這裡寫的就是那個真目錄。計劃自己寫一套,就會漏掉目錄被換成捷徑時的防護,而專案已經因此改過一次(`scripts/lumos:69247-69250` 的註解)。
- 追加 jsonl 這件事已有 `_drift_m1_ledger_miss` 一支,卻是專用的、不是通用的。計劃要求:抽出共用的追加寫入、或在子目錄下呼叫同樣的檢查,不要手抄第三份。
- 不寫治理帳的理由有講,是刻意跟鄰居的 `skipped-env` 不同,這條沒問題。

## F4 `--lf` 的「上次紅」讀法寫在 main 裡面,沒有函式可重用
severity: minor
blocking: 否
引句:「只跑執行器既有「上次紅過」紀錄裡的測試;沒有紀錄時印一行並回 2,不退成全套」
佐證: `scripts/test_lumos.py:49752-49759`(讀 `.lumos/test-cache*.json` 的 `failed` 欄位,只在 `_is_src` 時讀;`--ff` 就地用)、`scripts/test_lumos.py:49765-49766`(`--ff` 沒紀錄時印一行並照原順序跑)
紀錄來源計劃指對了,是既有的那份,沒有另造。但既有的讀法是 `--ff` 區塊裡的內聯程式碼。`--lf` 若在別處再寫一遍,就會有兩份「讀上次紅」。要抽成一支函式,或把 `--lf` 接在同一個讀取點之後。另外 `--lf` 的沒紀錄行為(回 2)跟 `--ff` 的(照跑)是刻意不同,計劃有講理由。消費專案(非來源 repo)的 `_is_src` 為假,所以 `--lf` 一律回 2;計劃的實務隱患寫了消費專案,但沒寫這一點。⚠ 計劃沒寫具體寫法,所以判不準。

## 4. 落點

對得上,沒有發現。`Systems/測試執行器` 在計劃提交 `b0eb608233` 裡存在(`about_code: scripts/test_lumos.py`),責任寫「參數解析、子集挑選」,正好涵蓋本案。`scripts/hooks/pre-push:1032` 與 `:1035` 兩行 `--ff -x` 提示改成 `--lf -x`,它的家是別的節點(例如 `bound-tests-gate`),不是 `測試執行器`。計劃的 `lands_in` 只列 `測試執行器`,但這兩行是提示文字、不是行為說明,所以只需要照鐵則 5 檢查提交時那幾個家有沒有被動到,不需要補寫。

不對齊共 4 條
