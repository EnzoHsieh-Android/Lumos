severity: minor

# 代碼審第 1 輪 通才-opus(正確性與邊界)

核對範圍:凍結 patch 5f8c84ff..6224d1c2,逐條對照計劃 S1–S4,在 `git clone --shared` 出來的副本裡實跑。基底版本 `git show 5f8c84ff:scripts/lumos` 與新版本放在同一份測試資料上對照跑。

**核對過、沒問題的(附實跑結果):**

- guard kill 每種結果的人讀行都帶對的 id。同一篇筆記放 9 條配方,涵蓋 killed、killed_unattributed、兩種 drifted(原文 0 次、開檔失敗)、檔案路徑逃出沙盒的 error、test 名不合法的 error、平台不在設定檔的 error、缺 old(命中 48 次、判 drifted),另用單獨的資料跑 survived 與 abort(基準測試本來就紅)。每一行 `id=` 後面 12 字元都等於 `_kill_recipe_id(rel, 原配方)[:12]`。
  引句:「print(f"{icon.get(r['verdict'],'?')} {r['verdict']:<9} id={str(r.get('_rid', ''))[:12]} "」
- `--json` 跟基底版本逐字相同:上面每種情況,把暫存路徑正規化之後整串 JSON(含欄位順序、人寫的 `_why` 欄、`recipe_id`)與回傳碼都一樣;結果裡沒有 `_rid`、`_logged`。
  引句:「print(json.dumps({"results": [{k: v for k, v in r.items() if k not in ("_logged", "_rid")}」
- surrogatepass 沒有改到既有配方的身分:拿 9 種元素(一般配方、emoji 與擴充平面字、控制字元、缺欄位、數字、None、巢狀清單、invariant 是數字、JSON 裡寫成成對替身跳脫的 emoji)配兩種節點路徑,`_kill_recipe_id` 與 `_kill_recipe_key` 新舊版本全部相同;蓋 `recipe_id` 時傳 None 或非字串的參數也相同。
- kill-rm 列出遇到 14 種壞欄位都不崩潰、回 0:invariant 是 dict、old 是 list、platform 是 False/0/空白、`{}`、`[]`、null、字串、true、1.5、雙向覆寫與 U+2028 字元、100 字原文、整個元素是落單替身字串、key 名與值帶落單替身。同身分合成一行、截字後加 …、控制字元有跳脫。
- 擋待填字樣:`<照新原文改寫的壞法>`、前後空白、外圍一對單引號或雙引號、換行、全形空白包住的都擋下回 2;含有待填字樣的整行原文 `PH_NEW = "<照新原文改寫的壞法>"` 照常寫入 rc0;舊範本的 `<壞法>` 不擋(本來就不在範圍)。
- `-k kill` 子集 354 條全過;跟改動文件相關的 `t_toplevel_help_has_no_handwritten_command_list`、`t_slim_gate`、`t_tension_doc_sync`、`t_drift_c4_code_review_r1` 也全過。`--id` 只有 main 一個呼叫點,沒有其他程式在解析 guard kill 的人讀輸出。

**範圍外但值得記下的既有問題(不在 diff 裡,不列成 finding):** guard kill 在 Python 專案會因為舊的位元組碼快取(`__pycache__`)把沒有傷害的壞法誤判成 killed。在同一個沙盒裡,前一條壞法跟這一條改動後檔案大小一樣、又落在同一秒內,Python 就會沿用前一條留下的快取。基底版本重現結果:無害壞法單獨跑是 `['survived']` rc1;先放一條會殺死測試的(`LIMIT = 5`→`LIMIT = 99`,多 1 字元),再放同樣多 1 字元的無害壞法(`def check(n):`→`def check(n): `),結果是 `['killed', 'killed']` rc0;換成多 3 字元的無害壞法就變回 `['killed', 'survived']`。這屬於「稻草人證據被判成殺得掉」那一類,建議另開 Issue(例如跑之前設 `PYTHONDONTWRITEBYTECODE=1`,或每條之間清掉 `__pycache__`)。

## F1 擋待填字樣時剝掉外圍引號,誤擋原文本來就是帶引號字串字面值的合法配方

severity: minor
blocking: 否
引句:「if len(t) >= 2 and t[0] == t[-1] and t[0] in "'\"":」
file: `scripts/lumos:13499`
file: `docs/lumos-toolchain-knowledge/Projects/殺傷力配方修補體驗_計劃.md`(S4 條款)

1. S4 寫的是「去掉前後空白後整個等於範本的待填字樣」才擋,「只是含有這串字時應照常寫入」。實作多剝了一對外圍引號(實作紀錄有記),結果程式裡剛好就是 `"<照新原文改寫的壞法>"` 這種字串字面值、而配方的 `--old`(或 `--new`)寫的正好是這個字面值時,也會被擋。照條款字面,這種值只算「含有」。
2. 實跑(同一份資料,基底版本對新版本;`ph.py` 內容為 `PH_NEW = "<照新原文改寫的壞法>"` 與 `MSG = '<照現在的程式填原文>'`):
   - `--file ph.py --old '"<照新原文改寫的壞法>"' --new '"broken"'` → 基底 rc0、新版 rc2
   - `--file ph.py --old "'<照現在的程式填原文>'" --new "''"` → 基底 rc0、新版 rc2
   - `--file prod.py --old 'LIMIT = 5' --new "'<照現在的程式填原文>'"` → 基底 rc0、新版 rc2
   - 擋下訊息都是「範本的待填欄還沒填」,可是使用者根本沒用範本,會被這句話帶錯方向。
3. 實際會碰到的地方:`scripts/lumos` 裡 `"<照新原文改寫的壞法>"` 正好只出現一次(`grep -c` 等於 1),替這支程式的待填字樣常數寫最短配方時,自然就會寫這個值。繞得過去(把原文擴成整行),所以只算 minor。
4. 建議:二選一。一是不剝引號,改成也比對 `'<…>'`、`"<…>"` 這兩種完整寫法,但仍然會擋到第 2 點的例子;二是把剝引號的行為寫進 S4 條款,並把擋下訊息改成同時說明「如果原文本來就是這個字面值,請把原文擴到整行」。不管選哪個,條款要跟程式一致。

## F2 surrogatepass 只修好了「算身分」:同篇另一條配方帶落單替身字元時,kill-rm 移不掉任何一條,guard kill 也還會崩潰,Issue 沒有記

severity: minor
blocking: 否
引句:「# surrogatepass:欄位帶落單替身字元時不崩潰,其他配方的身分不變(Projects/殺傷力配方修補體驗_計劃)」
file: `scripts/lumos:13625`
file: `scripts/lumos:13947`
file: `scripts/lumos:14014`
file: `docs/lumos-toolchain-knowledge/Issues/guard kill遇到格式壞的配方整支崩潰.md`

1. kill-rm:筆記裡有一條正常配方 A,另一條的 `new` 寫成 JSON 跳脫 `"X\ud800"`(B)。新版列出正常、回 0,但 `kill-rm Systems/Limit --id e78d76f5fc38`(要移的是 A)回 rc2,訊息是「擋下:'utf-8' codec can't encode character '\ud800' in position 227: surrogates not allowed」。原因是改寫筆記時,留下來的 B 寫不成 UTF-8。如果同一篇有兩條帶替身字元的配方,哪一條都移不掉。S2 說「身分可直接拿去 `--id` 移除」,測試 ⑧ 只驗了「只有一條、而且移的就是它」這一種。
2. guard kill:替身字元在 invariant、test、note、new 任一欄,新舊版本都在寫 kill-log 或套壞法那一步丟 UnicodeEncodeError,回傳 1。這跟「有配方 survived」是同一個回傳碼。替身字元在 old 時,新版的人讀模式不再崩潰(判 drifted rc2),但 `--json` 模式還是在印 JSON 時崩潰、回 1,同一份輸入兩種模式的回傳碼不一樣(實跑:`old new_lumos () rc 2` 對上 `old new_lumos ('--json',) rc 1 … UnicodeEncodeError`)。
3. 這些都不是這次弄壞的:基底版本在這些情況一樣崩潰,而且更早。但計劃與提交說明的寫法(「原本會崩潰(…kill-rm、guard kill 都當掉)」)容易讓人以為整件事已經修好。這次一起寫的 Issue 列了缺 new、platform 是陣列等崩潰,沒有列替身字元這一類。
4. 建議:在 Issue 補一行替身字元的剩餘崩潰與重現方法。或者在 kill-rm 擋下訊息裡指出是哪一條配方含寫不成 UTF-8 的字元,先用 kill-rm 移掉它(前提是它是唯一一條)。

## F3 同一個提交寫的 Issue 說「invariant 是數字時印結果行才崩潰」,但這次已經修好了

severity: minor
blocking: 否
引句:「f"{str(r.get('invariant', ''))[:30]} [{r.get('test','')}] {r.get('detail','')}")」
file: `scripts/lumos:14036`
file: `docs/lumos-toolchain-knowledge/Issues/guard kill遇到格式壞的配方整支崩潰.md`(摘要 PITFALL 行)

1. Issue 摘要原文:「`invariant` 是數字時留痕寫完、印結果行才崩潰」。這次的結果行改成先轉字串再截,實跑新版 invariant=12345 與 invariant=null,人讀模式都正常印出(`✓ killed id=edacfe76b1c1 12345 …`)並回 0;基底版本在同樣情況是 TypeError、回 1。所以這句 PITFALL 一寫進去就過期了。這屬於筆記與程式的內部不一致,照規則要報。
2. 附帶說明:這個輸入的人讀模式回傳碼從 1(崩潰)變成 0。計劃明寫要修這行,`--json` 模式在基底版本本來就回 0,所以不算判法改變。但 Issue 的 REVISIT 要的是「格式壞的那條判 error」,現在這種配方會安靜地通過;Issue 要寫清楚哪幾種還會崩潰、哪幾種已經能照常判結果。
3. 建議:Issue 摘要刪掉 invariant 是數字那一句,或改成「已於殺傷力配方修補體驗修掉印行崩潰,但仍判成照常結果、沒有判 error」。

最高等級:minor
