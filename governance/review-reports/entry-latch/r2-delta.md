# r2 delta 席(折入自洽+行號抽驗+可實作性殘檢)

**D-1**|major|blocking:是——PRIOR-ART 檢索殘影
引句:「A 用既有 `cmd_search` 多詞回退 + `_rank_score_candidates`」
佐證:scripts/lumos:2104-2106、2173-2175(片語預檢單命中即 break、抑制 OR;cmd_search 無入口可跳過片語階段)。EL-4 已把提案 A 正文改成直接 OR,但 PRIOR-ART 仍宣稱走 cmd_search 多詞回退「正好接住」——兩句不可能同時成立;實測 `search "impact 鏡頭機械化"` 仍只回 1 篇、0.90 近名被藏。redirect stdout 一句預設呼叫會印的 cmd_ 層,同殘影旁證。

**D-2**|major|blocking:是——B 時序兩處殘句
引句:「B 掛在 mkdir 前,炸了會讓「不擋照建」變成建檔失敗」
佐證:/tmp/el-r2.md:19、40、43;scripts/lumos:9602-9609。EL-7 宣稱改「建檔後即告」,但問題節仍留「同名檢查之後、mkdir 之前」、鐵則節直述「B 掛在 mkdir 前」——「紀錄說改了、正文還是舊話」,實作者無法唯一決定插點。

**D-3**|major|blocking:否(單行修正)——建檔後自比坑
引句:「命中 → 建檔完成後印「★近名節點已存在:○○(status/決策 N 條)」
佐證:實測 difflib 自比=1.0;scripts/lumos:9608(寫檔後檔案已在磁碟)。建檔後重掃最自然的實作把新檔自己算進候選,自比 1.0 ≥0.6,每次建檔 100% 誤鳴=546 型麻痺;spec 無「排除自身/用建檔前索引」任何一字。

**D-4**|major|blocking:是——分數門檻無法定義
引句:「掛在「逐詞覆蓋全 0 或 top1 分數低於門檻」」
佐證:scripts/lumos:2129-2131(N/df/avgdl 以候選集為語料)、1953-1956。全 spec 無門檻數值與校準程序;BM25F 分數隨候選集浮動,固定門檻定義不完整;且「逐詞覆蓋全 0」在直接 OR 設計下恆等於「候選 0」,誠實零行全部載重壓在沒給值的門檻上,設錯=系統性假陰性。

**D-5**|major|blocking:是——濾網跑不出自己的驗收例
引句:「濾純數字 token(「2026」實測命中 381/385=全庫召回)與長度 1 的 ASCII token」
佐證:scripts/lumos:1871-1888;實測 `_rank_tokenize("auto-2026-08-23")`=`['auto-2026-08-23','auto','2026','08','23']`,兩道濾網後剩 2 token→不觸發「token ≤1」→拿 auto 查=68 篇垃圾重演;`intake-guard` 濾後三枚非兩枚。缺「丟可拆分母 token」規則。

**D-6**|minor|blocking:否
引句:「今天無 headless 呼叫端,test_lumos.py 只斷 rc」
佐證:scripts/test_lumos.py:541-551(對 cmd_new stdout 有包含式斷言)。「只斷 rc」不實;結論(加行不破)仍成立,措辭失準。

**D-7**|minor|blocking:否
引句:「檔名 difflib ≥0.6 單判準(原「search 前 2 名帶同詞幹」刪除」
佐證:實測 difflib("範本system","範本issue")=0.67;三型 228 檔僅 1 檔有日期前綴。比對語料範圍沒寫死(同資料夾/跨型);剝前綴在納入三型近乎空轉,要嘛說明剝誰要嘛承認防未來。

**D-8**|minor|blocking:否
引句:「既有 21 處消費端全逐鍵取值,加鍵不破壞」
佐證:機械數=test_lumos.py `"loop", "next"` 呼叫 40 處、JSON 消費 4 處;兩個不同口徑撞同一個「21」可疑。安全論證不受影響,帳面精度。

**D-9**|minor|blocking:否
引句:「每筆一行=節點名+status+決策數,title 近名者標 ★近名」
佐證:/tmp/el-r2.md:31、39。A 的「近名」判準沒給——補「沿用 B 判準」即了。

折入自洽:EL-1/2/3/5/6/8/9/10 到位;殘影=EL-4 沒折 PRIOR-ART(D-1)、EL-7 沒折兩處位置敘述(D-2)+時點後挪新生自比坑(D-3)。
行號抽驗 8 處:1871✓ 2174-2176 邊界差一行 5745-5750✓ 5889✓ 5905✓ 5911✓ 5927✓ impact計劃:53✓;附帶:Verification 156 檔全日期前綴✓、事故對 0.903✓、cmd_search 無寫入✓、三型判準可實作✓。

severity: major
