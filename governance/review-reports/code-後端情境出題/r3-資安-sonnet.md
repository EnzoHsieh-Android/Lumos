severity: major

這輪找到 2 條:一條是修補新引入的正規式 O(n²) 卡死(major),一條是實驗卷證殘留本機路徑(minor)。

快照裡每支新增或改動的檔我都掃過密鑰、權杖、帶密碼的連線字串。`compose.yaml` 的密碼是 `<<lab-admin-password>-password>` 這種遮罩佔位字,`init.sql.txt` 的是 `<readonly-password>`,沒有真值外露。`toolbox-postgres-calls.txt` 裡的 `pg_read_file('/etc/passwd')` 是實驗探測紀錄,結果是權限被擋,不算洩漏。

### Finding 1:新加的題目定義正規式對長行是二次方時間,可卡死規格閘與 lint

- 誰:能把筆記推進 repo 的人,例如 PR 作者或貼了一長串內容的協作者。
- 從哪裡:任何計劃筆記裡的一行,不必在〈待決問題〉節內。
- 送什麼:一行以 `Q1` 開頭、後面接很長的空白或數字,例如 `Q1` 加 4 萬個空格。
- 拿到什麼:修補新增的 `_PQ_DEF_RE` 在 `_pq_unreachable` 裡對全檔每一行(只要不在已解析的節內)都跑一次。這個正規式有 `\d+\s*\]?.*?[\[【]` 的巢狀量詞,對這種行是二次方時間。`lumos lint`、規格閘、`pitfalls --stage` 共用這個解析,所以三處都會卡住;推送前的閘跑的就是它們,CI 同理。
- 這是修補回歸。修補前的 `_PQ_LOOKS_RE` 只在節內比對,而且沒有這個 `.*?`。程式原註解還特別寫「長行不回溯」,新式子違反了這個承諾。

引句:「_PQ_DEF_RE = re.compile(r"^[\s>*+\-\d.、)）|\[\]xX]*[QＱ]\s*\d+\s*\]?.*?[\[【]\s*(?:類|階段|狀態|阻塞|不可逆)")」

file: `scripts/lumos:6920`(以 46bc93c3 為準)

最小重現(在 `/tmp/lumos-seat-work/code-後端情境出題/資安-sonnet/` 下,`t.py` 載入兩版 `scripts/lumos`,對 `parse_pending_questions` 餵「別節」裡一行 `Q1` 加 n 個空格):

```
python3.14 t.py lumos_new.py   # lumos_new.py = git show 46bc93c3:scripts/lumos
lumos_new.py 10000 0.44 1
lumos_new.py 20000 1.74 1
python3.14 t.py lumos_old.py   # lumos_old.py = git show 112ad15f:scripts/lumos
lumos_old.py 10000 0.0 1
lumos_old.py 20000 0.0 1
```

單獨量正規式本身:`"Q"+"1"*40000` 與 `"Q1"+" "*40000` 各要 7 秒以上,時間隨長度平方成長,所以 20 萬字元的一行會到分鐘級。

severity: major
blocking: 是
歸因:有證據的修復回歸。兩版查證如上:修補前 20000 字 0.0 秒,修補後 1.74 秒。

### Finding 2:實驗卷證殘留本機絕對路徑,暴露使用者名稱與 uid

- 誰:看得到 repo 的人。
- 從哪裡:`codex-rater-raw.txt` 在 `rating/` 與 `rating-mini/` 各一份。
- 送什麼:不需要送,檔案已提交。
- 拿到什麼:`rating/` 那份有 14 處、`rating-mini/` 那份有 10 處 `/private/tmp/claude-501/-Users-enzo-orca-workspaces-...` 路徑,洩漏本機使用者名稱 `enzo`、uid 501 和工作區結構。
- 這些路徑是 `985d8818` 「實驗卷證遮掉本機路徑」之後仍然漏掉的。檔內也沒有密鑰,所以只是資訊外露。

引句:「workdir: /private/tmp/claude-501/-Users-enzo-orca-workspaces-lumos-toolchain-Backend-improve/fe5c4f58-e7fb-477f-be55-0823b5438608/scratchpad/qo-rate」

file: `governance/eval/qo-ablation-2026-10/rating/codex-rater-raw.txt:1`(以 46bc93c3 為準)

兩版查證:`git show 112ad15f:…/rating/codex-rater-raw.txt | grep -c 'private/tmp'` 回 14,`git show 46bc93c3:…` 也回 14。`rating-mini/` 那份我只查了 46bc93c3(10 處)。

severity: minor
blocking: 否
歸因:有證據的原有漏查。

### 其他範圍

我也看過下面幾處,沒有找到可利用的洞:

- 新加的 Spring 觸發詞正規式,對連續空白是線性的。
- `_PQ_FLAG_LOOSE_RE` 有 `{0,20}` 上限。
- `cmd_packets` 清舊包只刪 `dest` 底下的 `packet-*.json`,`dest` 由操作者的命令列給,不是攻擊者可控。
- `scenario_probe._run_scenario` 只是把參數帶下去,沒有新的殼層串接。

總結:最嚴重 major;blocking 共 1 條。
