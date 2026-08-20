# r3 s1 通才席 對抗審查報告

審查對象:`/tmp/閘觸發帳統計-r3.md`(178 行,「閘觸發帳統計_計劃」r3 版)
審查方式:逐段讀完全文,對照 `scripts/lumos`(14,969 行)實際程式碼與 `docs/.governance-log.jsonl` / `docs/.canary-log.jsonl` 等帳檔實跑數字驗證。已讀「審計修正紀錄」,以下不重複列已折入項目,只列新洞。

---

## Finding 1(major)—— `anchor-approve` 的「不同節點數」欄位量的是原始碼檔名,不是知識圖譜節點

引句:「`anchor-approve` 實際有 5 列節點為空,這是」

設計把「不同節點數」列為六個「可重算硬事實」欄位之一(第 91 行:「六欄,全部是可重算的硬事實:去重後筆數、原始行數、不同節點數、不同 commit 數、首見日、末見日」),並在第 94 行特別交代 `anchor-approve` 不可整欄 `n/a`——理由是它只有部分列 `nodes` 為空,不是 mapper 硬寫 `nodes: []`。這個判斷本身沒錯(實測 142 列中確實剛好 5 列 `nodes` 為空,其餘 137 列非空),但設計完全沒注意到:**那些非空的 `nodes` 值根本不是知識圖譜節點,而是原始碼檔案路徑。**

追到寫入端:`cmd_anchor_approve`(`scripts/lumos:10046-10061`)把 `ANCHOR_FILES`(`scripts/lumos:9235-9241`,固定 5 個檔案:`scripts/test_lumos.py`、`scripts/test_autonomous_loop.py`、`scripts/hooks/{pre-commit,pre-push,post-commit}`)裡「內容有變」的子集存成 `changed`,寫進 `governance-log` 的 `nodes` 欄(`scripts/lumos:10071-10072`:`"nodes": changed`)。`cmd_gov` 的 governance-log mapper 再對它套用 `stem()`(`scripts/lumos:2918`),得到 `test_lumos`/`test_autonomous_loop`/`pre-commit`/`pre-push`/`post-commit` 這五個「看起來像節點名」的字串。

實測直接證實:

```
$ python3 -c "...anchor-approve 的 nodes 聯集..."
['scripts/hooks/post-commit', 'scripts/hooks/pre-commit', 'scripts/hooks/pre-push',
 'scripts/test_autonomous_loop.py', 'scripts/test_lumos.py']
```

跟 `ANCHOR_FILES` 逐一對應,不多不少。對照 `check-e1` 的 `nodes` 聯集(同樣是 `cmd_gov` governance-log mapper 產出):`['guard-kill', 'slim-get-一行安裝', 'slim-install-安裝器', 'slim-uninstall-一行卸載', '測試假綠形態']`——這些才是真正的 Systems 節點 stem。兩者結構完全相同(同一個 mapper、同一個 `stem()`),但語意天差地遠:一個是「錨點守護的測試/hook 檔名」,一個是「圖譜節點」。目前 repo 內剛好沒有任何 Systems 節點的 stem 撞名這 5 個檔名(已查證),所以純數字不會出錯,但**語意是錯的**——「不同節點數」欄位對 `anchor-approve` 印出的「5」,含義是「5 個錨點檔案」,不是文件通篇宣稱的「涉及節點數」。設計文件從頭到尾(基線表第 27-32 行、S1 欄位定義第 82-95 行、範例)把這一欄當成跨 gate 同質的「圖譜節點計數」呈現,沒有任何一處對 `anchor-approve` 做語意區分或加註警語。這正是文件自己在 78 行警告過的「零觸發有三種、不可暗示等價」的姊妹問題:**同一欄位在不同 gate 底下量的是不同種類的東西,而文件對此毫無防備**。若日後有節點恰好取名 `pre-commit`/`test_lumos` 之類(常見英文詞,並非不可能),`--node` 縮限模式下還會把「錨點檔案的核准紀錄」誤配到那個節點名下,造成假訊號。

---

## Finding 2(major)—— S1 三層數字表的「實測(全史)」數字,親自重算對不上

引句:「8,825(七源合流,`--full` 印出行數)」

第 58-67 行的「★三層數字,不可互相冒充★」表格是全文論證的地基:它被 r1 三席一致列為 blocker #1(第 174 行),整節「刪掉的東西」也用「差 8.6 倍」這個對比(第 69 行)來證明「去重列即人會看到幾筆」是錯的。但這張表自己標出來的「實測(全史)」數字,拿現有 `lumos gov` 實際跑一次對不上:

```
$ python3 scripts/lumos gov --full --since 9999 | tail -3
...
8700 筆(近 9999 天)

$ python3 scripts/lumos gov --since 9999 | ...(canary 分帳前的事件行數)
901 行
```

文件宣稱去重列(七源合流)= **8,825**,呈現行 = **1,026**;實際重算分別是 **8,700** 與 **901**——兩層都少了整整 **125**,且兩次獨立重跑(`--since 9999` 與 `--since 36500`)結果一致,非隨機誤差。

這不是「帳本後來長大了所以數字對不上」的無害漂移:`docs/.governance-log.jsonl` 的原始行數現在仍是 **20,139**(與文件宣稱的原始行數一字不差,git log 顯示該檔最後修改在文件寫成當天),真正變大的只有 `.canary-log.jsonl`(文件宣稱 448 筆,現查 454 筆,+6),而 canary 每列都帶唯一 `token`、不會被摺疊——多出的 6 筆只會讓去重列/呈現行**變多**,不會變少。也就是說,把時間漂移這個因素排除掉之後,文件當初計算 8,825 / 1,026 這兩個數字時,推算方式本身就跟真正跑 `cmd_gov` 的結果對不上,差距比 125 還大。

這節文件反覆強調的賣點是「每一個印出來的數字都可以拿原始帳重算驗證」(第 114、176 行一再重申),而這張最核心的示範表格,親自重算就翻車——這正好打在這句主張的心臟上。建議設計定案前,拿目前這份帳實際跑一次 `lumos gov --full`/`lumos gov` 更新這張表,不要沿用可能是手算/舊版腳本推出的數字。

---

## Finding 3(minor)—— 欄位定義寫錯:`token` 不是只有 canary 來源會填

引句:「`token`:去重鑑別子,只有 canary 來源會填(`scripts/lumos:2933`)」

「讀到的欄位」一節(第 82-88 行)把 `token` 定義成「去重鑑別子,只有 canary 來源會填,其餘為空字串」。這句話直接抄自 `scripts/lumos:2930` 的程式碼註解「只此 mapper 輸出 token 鍵」,但該註解本身已經過期、與現在的程式碼不符:

- `signoff` mapper 在 `scripts/lumos:2922` 就有 `"token": d.get("ts", "")`
- `kill` mapper 在 `scripts/lumos:2927` 有 `"token": d.get("invariant", "") + d.get("ts", "")`
- `ci` mapper 在 `scripts/lumos:2946` 有 `"token": d.get("dedup_key", "")`

四個來源(canary/signoff/kill/ci)都會填非空 `token`,只有 `bypass`(L2)、`rot-queue`(L3)、`governance-log` 三源的 mapper 完全沒有 `token` 鍵(dedup 時靠 `.get("token","")` 補空字串)。文件的「只有 canary 填」是錯的。

這個誤述不影響第 3 節設計的六欄輸出本身(去重鍵早已用 `r.get("token","")` 正確涵蓋所有來源,`scripts/lumos:2953`),所以不會讓實作出錯,故列 minor;但它是一句寫進「先定義好再用」欄位詞彙表的斷言陳述,直接被三處程式碼行反證,且沿用了程式碼裡一句過期註解的錯誤,屬於「引用的證據撐不住結論」。

---

## Finding 4(minor)—— check-j 的行號引用文不對題

引句:「其整段邏輯掛在 `if _regen_rels:` 之下(`scripts/lumos:1289-1291`)」

第 78 行說 `check-j` 的邏輯「整段掛在 `if _regen_rels:` 之下」,並引 `scripts/lumos:1289-1291`。但那三行實際是:

```
1288  # Check J: regen 重生來源守衛...
1289  # 與 cmd_lint 共用 check_regen_provenance...
1290  # errs→warn(hard)計 issues/warns→warn_soft/gov_events→僅 --ci 落帳。
1291  _regen_rels = [(rel_, n_) for rel_, n_ in sorted(notes.items())
```

真正的 `if _regen_rels:` 陳述式在 `scripts/lumos:1293`,不在引用範圍內——1289-1291 是註解與 `_regen_rels` 賦值起始行,不是「掛在其下」的那個 `if`。行號本身存在、內容也大致相關(同一段程式碼區塊),但跟句子描述的具體陳述式(`if` 判斷)對不上,屬於審查規範明講要抓的「壞引用」。全庫 `regen:` 欄位節點數 = 0 這個結論本身經查證是對的(已用 `grep -rn "^regen:"` 覆核)。
