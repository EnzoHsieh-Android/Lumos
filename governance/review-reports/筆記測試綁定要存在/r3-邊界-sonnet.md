severity: major

# 設計審 r3 邊界-sonnet 席報告

實驗環境:`git clone --shared` 出來的 `negguard` 到我的臨時目錄,另建 5 個小 repo(子模組、方括號根、playwright、非 UTF-8 筆記、一般 vault)。實跑的是現有的 `slot_parse`、`_dispositions_check_test`、`_drift_tree_env`、`_ns_text_key`、`_ns_superseded`、`_platform_test_index`。全部在我自己的目錄,沒動 repo 根。

## F1 在原行上標作廢、測試照掛,1c 抓不到(最主要的撤除寫法整個漏掉)
severity: major
blocking: 是
引句:「新寫的作廢條目掛著活測試,而且這一條用 `_ns_text_key` 正規化後在起點那一版整個知識庫找不到一樣的」
file: `scripts/lumos:28170`(`_ns_text_key` 吃的是 `slot_parse` 的 core,欄位全被剝掉)
file: `scripts/lumos:28194`(`_ns_is_old` 現成就會回「對上的舊行有沒有標作廢」,計劃沒用它)
1. 輸入:起點版有 `RULE: 點數過期後一律作廢 [依據:法規] [since:…] [retire:人裁] [until:…] [test:t_live]`;這次提交只在同一行尾加 `[status:superseded] [被取代:[[Systems/新規則]]]`,`[test:t_live]` 留著。這就是 rtb 那 12 條的真實形狀(撤除發生在舊行上)。
2. 實跑:舊行與新行的 `_ns_text_key(slot_parse(…)["core"])` 都是 `'點數過期後一律作廢'`,`same key: True`;`_ns_superseded` 舊行 False、新行 True。
3. 照字面實作:新行是「新寫的行」,但它的鍵在起點版找得到一樣的 → 被當成「只重排折行」放過,1c 不報。1c 只會對「整條新寫就帶 status:superseded」的行回 1,而撤除幾乎都是改舊行。S11、S12、S24 的測試用新寫整條的例子會綠,真實撤除路徑照樣漏。
4. 判準應該是「起點那一版同鍵的條目有沒有已標作廢」(`_ns_is_old` 第二個回傳值),不是「找不找得到同鍵」。

## F2 平台根是子模組或路徑含 glob 字元時,推送時第②道對每個真測試名都回「grep 不到」
severity: major
blocking: 是
引句:「平台根在 repo 外時只做第①道(它既有的規矩)」
file: `scripts/lumos:41262`(`rel = root.relative_to(rr)` 對子模組路徑成功,所以不走「跨 repo 只做①」的出口)
file: `scripts/lumos:41271`(`:(glob){_base}**/*{e}` 路徑沒轉義)
1. 子模組:`config.json` 設 `platforms.py.root = vendor/sub`,`vendor/sub` 是 git 子模組,裡面 `tests/test_s.py` 有 `def test_in_sub`。實跑 `_dispositions_check_test(root, HEAD, "test:test_in_sub", pidx)`:
   - 有 at_sha:`(False, "測試 'test_in_sub' 在推送版本 5d662342 的樹裡整字 grep 不到(未追蹤/未提交的測試不算證據)")`
   - 無 at_sha:`(True, '')`
   原因:`git grep <sha> -- :(glob)vendor/sub/**/*.py` 不進 gitlink,rc=1。
2. 路徑含 `[ ]`:root = `apps/[web] x`,真測試 `test_br` → 同樣 `(False, … 整字 grep 不到 …)`、無 at_sha 時 `True`(`[web]` 被當字元類)。
3. 計劃把「平台根在 repo 外」寫成已處理(PRIOR-ART 與〈名詞〉),但子模組根在 repo 內路徑上、第①道過了第②道必敗。推送與 CI 對這種專案的每個新測試名都擋;步驟 4 的「工作樹與被檢查版本有差異就只提醒」也接不住(兩邊測試檔一樣)。S14 的跳過只涵蓋根不存在或掃不到方法。
4. 退路只有 `warn`/`off`/單次跳過;子模組放測試的專案等於整組規則報廢。

## F3 沒反引號的散文提到 `[test:]` 會被 S20 當違規擋(本 repo 實測 76 筆)
severity: major
blocking: 是
引句:「新加的是佔位字、或 `[test:]` 方括號裡沒有名稱 → 一律違規,先於判存在」
file: `scripts/lumos:3764`(`slot_parse` 對 `[test:]` 回 `('test','',None)`;對沒收尾的 `[test:… 回帶錯誤的整段尾巴)
1. 用 `slot_parse` + `_visible_lines` 掃本 repo 全部 `docs/**.md` 非 other 區的 `test` 欄:1247 個,其中 76 個空值或帶錯誤(約 6%),全是把 `[test:]` 當名詞在講的句子,例如 `- ❌ **[test:] 綠燈錨不進 v1 gate**…`、`同 [test:]/[audit:]/[rollback:] 的誠實`、`ref 在 [test:] 綁定 + doctor Check T`。這個 repo 的筆記天天在講這個標記。
2. 照字面實作:有人新寫一句這類話(沒包反引號)→ S20 擋,而且 `decisions` 區的 14 行也有同類字樣(計劃沒說 decisions 區要不要掃,也沒說空值要不要先排除「值是空的但後面接 `/[manual:`」這類名詞用法)。
3. 同一支抽取對沒收尾的 `[test:`(散文提到、方括號不成對)給的是帶 error 的整段行尾當名稱,例如 `slim-install-安裝器.md` 現有那行會抽出 `/FLOW:/KEY:/valid_under/佚失: 等仍有效內容;★Task 10 新增★…` 當「新加的測試名」。計劃只說「值再切逗號」,沒說 error 欄位怎麼處理(`_slot_vals` 的慣例是排除)。
4. 擋下訊息「照那一條的前綴給改法」沒有一條是「這是在講標記本身,用反引號包起來」,作者只能亂改。

## F4 計劃沒定「單支判存在丟例外或逾時」的 fail-open,現有函式的慣例是反過來擋
severity: major
blocking: 是
引句:「索引建不起來、或某平台的根不存在、掃不到任何測試方法 → 那個平台這次不查、印一行原因。」
file: `scripts/lumos:41209`(`_disp_git_timeout` 預設 8 秒,docstring:超時往上拋 `subprocess.TimeoutExpired`,由呼叫端接成「無法驗證(擋,不放行)」)
file: `scripts/lumos:28560`(`cmd_note_shape` 全程 fail-open:git 算不出來、淺層 clone 都 rc0)
1. 步驟 4 與 S14 只列索引層的三種失敗。`_dispositions_check_test` 本身在 `git grep` 逾時、`OSError` 時是拋例外,不是回 `(False, 原因)`;表態閘的呼叫端把它接成擋下。
2. 計劃沒寫新組怎麼接。兩種字面實作都錯:不接 → 推送時 note-shape 噴 traceback、掛鉤 rc≠0 擋推送;照表態閘接 → 大 repo 一次逾時就把一個真測試名判成「指不到」擋下,跟 `cmd_note_shape` 「算不出來就說一句 rc0」的契約相反。
3. 未實測逾時(環境下限 0.1 秒、我的小 repo 單次 0.04 秒觸發不了),依據是讀碼與 docstring。

## F5 起點版的非 UTF-8 筆記沒有名稱,把筆記轉成 UTF-8 的提交會把舊名字全當新加
severity: major
blocking: 是
引句:「起點那一版整個知識庫的名稱集合用 `_drift_tree_env` 一次批次讀」
file: `scripts/lumos:30601`(解不開的筆記進 `unreadable`,建成空筆記)
file: `scripts/lumos:707`(`env_text` 對這種 Env 回 None)
1. 實跑:vault 裡 `Systems/B.md` 是 latin-1(含 `\xe9`)。`_drift_tree_env(root, HEAD, vault)` 之後 `env_text(e,"Systems/A.md")` 有字、`env_text(e,"Systems/B.md")` 是 `None`,且 `_note_unreadable` 為 True。
2. 現有流程(筆記內容閘訊息)叫人「轉成 UTF-8 再提交」。轉碼提交只動含非 ASCII 位元組的那幾行,這些行成為新寫的行;如果那行有 `[test:舊且已懸空的名]`,起點集合裡沒有它(整篇當讀不出來),被算成「新加」→ 擋。
3. 這跟〈名詞〉自己寫的「改舊行其他字…不算新加(起點那一版有)」衝突;起點判不了的篇應該讓這組對該篇的名稱改成只提醒(或把該篇的名稱視為已有),計劃沒處理 unreadable。

## F6 一行很多真名稱時推送時間無上限,起點整庫讀不看有沒有候選
severity: minor
blocking: 否
引句:「每個要查的名稱一次 `git grep`(本 repo 量過一次約 0.2 秒),新加的名稱通常個位數。」
file: `scripts/lumos:41281`
1. 我的量測:100 個真名稱逐個 `_dispositions_check_test(…, at_sha)` 共 3.9 秒(此 repo 每個約 0.04 秒,計劃說 rtb 約 0.2 秒)。新開一篇列出 200 個測試名的驗證筆記,在 rtb 規模約 40 秒;一行放上千個不同的真名稱沒有上限,也沒說同一名稱去重。
2. 步驟 3 沒寫「第 1 步沒抽到候選名稱就不讀起點整庫」;空推送與純程式推送也要付 0.3 秒(630 篇)到 60 秒上限。步驟 4 只對索引寫了「有要查才建」。

## F7 `slot_parse` 的反引號規矩讓單個落單反引號吃掉整行後面的名稱
severity: minor
blocking: 否
引句:「反引號與大小寫、全形冒號照 `slot_parse` 的規矩(跟筆記格子認得的寫法一致)。」
file: `scripts/lumos:3764`
1. 實跑 `slot_parse("x ` [test:abc] y")` → `fields=[]`;`slot_parse("x [test:`abc`] y")` → 名稱 `'`abc`'`(反引號被保留在值裡)。
2. 前者:行裡奇數個反引號(例如 `` `a` 和 `b [test:ghost] ``)之後的真綁定整段不被檢查(漏網,不是誤擋)。後者:`_dispositions_check_test` 對 `` `t_x` `` 回 `(False, …工作樹掃不到…)`,計劃沒說抽取時要不要剝名稱兩端反引號,而 `slot_parse` 自己的錯誤訊息還叫人「把值用反引號包起來」。實作不剝就會對照著提示去包而被擋。

## F8 其他字面實作細節(minor,合併列)
severity: minor
blocking: 否
引句:「「類別.方法」寫法照 `_classify_test_refs` 的規矩補進第①道(只認方法名那段),第②道用方法名找。」
file: `scripts/lumos:40262`(`method.rsplit(".", 1)[-1] in mset`,前面的類別名任何字都放行)
file: `scripts/lumos:40917`(legacy 設定遇冒號:`不支援平台前綴`;multi 設定:`不在 platforms 裡`,兩句原因不同)
1. `Wrong.t_real` 會判第①道過、第②道用 `t_real` 找也過;類別名寫錯不報。
2. S25 的「另提示 `[manual:]`」要從 `_dispositions_check_test` 回的原因字串判「前綴沒定義」,legacy 與多平台是兩句不同的話,只比對其中一句會漏另一種。
3. `[test:` 的 `_notelines_new` 第二次呼叫(步驟 2 說不靠 `--slots` 自己要)會重算一次整個範圍逐提交 diff,並把同一批非 UTF-8 `errs` 再生一份,計劃沒說這組要丟掉 errs。

## 已讀無 finding 的項目
- `slot_parse` 對大寫鍵(`[TEST:abc]`)、全形冒號(`[test：abc]`)、鍵前後空白、`[test:a][test:b]` 連寫、名稱含 `-rf`、`t_.*` 之類:實跑都正確抽出,名稱含 `-` 開頭或正則字元時 `_dispositions_check_test` 用 `-F -e`,不被當旗標或正則(`-rf`、`t_.*`、`(` 都回「掃不到」)。
- 效能:一行 5000 個沒收尾的 `[test:` 0.0014 秒;2 萬個 `[test:a]` 0.015 秒;3000 層 `[test:[[[` 0.0014 秒;`slot_parse` 本身無二次方。
- 空樹:`_drift_tree_env(root, None, vault)` 與空樹編號都回空 Env、不拋例外,「全是新加」的語意成立。
- 空推送、刪分支(終點全 0)、淺層 clone、提交時的合併中:`cmd_note_shape` 在跑到這組之前就 rc0 返回,這組不會被走到。
- 起點整庫批次讀:本 repo 630 篇、420 萬字,0.28 秒、最大常駐約 74 MB,在時間上限內。
- 平台根在 repo 外(跨 repo):`relative_to` 失敗,確實只做第①道(F2 說的是 repo 內的子模組,不是這條)。
- `test-gone` 作為新鍵:`_SLOT_KEY_RE` 的 1 到 12 字元上限放得下 9 個字元的鍵名,`TEST_REF_RE`(`\[test:`)不會誤吃 `[test-gone:`。

最高等級:major,blocking 共 5 條
