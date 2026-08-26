# dref-v4 r3 delta 席(r2 折入回歸 + 新洞)
sha256 已核對 = 6918e768758d1314763ea8c08f00784966efac284d14a467113b389a046796a9。

### d-f1
severity: clean
引句:「單次單趟沒有機械擋,純靠 Claude 編排協議紀律不重查」
佐證:file: `governance/review-reports/dref-v4/r3-snapshot.md:114-121`
說明:r2 d-f1 要的誠實話補了,還把設計改了:相一 add-ai 掃描明講「重跑 backlog 對正確性安全(冪等)」,把「防重查」換成「重查也不會壞」,危險操作挪相二收尾。真架構調整非換句話說。

### d-f2
severity: clean
引句:「定位比對用正規化 tuple(r2 d-f2:人照 candidates/promote 印的正規形輸入」
佐證:file: `governance/review-reports/dref-v4/r3-snapshot.md:129`
說明:V5 prune 明講定位改用共用正規化 tuple helper,兩種結果拆不同訊息(真移除印「已移除」、本來不在印「這條本來就不在,是不是打錯正規形」)。靜默假剪路徑不再靜默。

### d-f3
severity: clean
引句:「★連補都補不了:先 reindex 給它 id、或明知會被無條件壓掉仍蓋章★」
佐證:file: `governance/review-reports/dref-v4/r3-snapshot.md:130`;file: `scripts/lumos:1236`
說明:掃描來源明講搬 E2 判準(verified_by/plan_refs 排除 related,對齊 1236 typed_in),無 id 翻案決策獨立列更重警訊,原因講對(E2 對這批正欄一有東西無條件壓、candidates/add-ai 永遠碰不到)。兩毛病都補。

### d-f4
severity: major
引句:「收尾單次,全掃描完成後才做」
佐證:file: `governance/review-reports/dref-v4/r3-snapshot.md:116-121`;file: `governance/review-reports/dref-v4/r1-s2.md:8-12`
說明:相一到相二分界靠「所有 add-ai 完成後才做」撐,但沒講「完成」怎麼判。backlog 沒第三欄記「判過不像不加」,這類候選永留候選集,backlog 結構上很可能永遠不回傳空(回頭條件段也拿覆蓋數而非 backlog 清空當驗收,side-step 了)。「全掃描完成」無系統可觀測觸發點,唯一訊號是人記得「整份名單看過一輪」=d-f1 同型(協議非機械),卻沒附同等誠實標籤。更嚴重:相序是 v4 取代 v3 否決記憶的核心安全論證(121 行),若一 session 誤判相一完成提早 prune、另一還在相一之後又 add-ai,剛被剪的 ref 加回=相序要擋的振盪換位置重演,沒人被提醒風險。

### d-f5
severity: major
引句:「promote locate·remove·dedup·count·覆蓋掃描)一律走同一支」
佐證:file: `governance/review-reports/dref-v4/r3-snapshot.md:129-130,138`;file: `scripts/lumos:1272-1278`
說明:_dref_same 定義是「兩節點都解析相同且 did 相同」,前提是比「兩個 ref」。但覆蓋掃描要列的無 id 翻案決策沒有 ref 可比(沒東西指向它們=問題本身),靠掃 id 是否空字串抓,不是靠 ref 比對。釘死合約把覆蓋掃描算進「用 _dref_same 做 ref 比對」清單,沒把「無 id 決策識別」與「ref 對 ref 比對」分開。字面最自然實作=覆蓋掃描列這批時也套 _dref_same 去重,而 did 都空字串 `""==""` 恆真,把同節點兩筆不同無 id 翻案決策誤判同一筆 dedup 掉,警訊比實際少。正是 E2 抑制(1272-1278)已學到用 `did and ...` 防的坑,_dref_same 字面沒比照,無 id 分支比現碼更危險,撞 d-f3/s3-f1 防的最壞子集。

## 掃過但乾淨的面
- 六原語數/巢狀 add_subparsers/共用候選函式/V1-V3 冪等口徑,r2 折入未回歸;promote count-check「此 ref 不在 _ai」非「整欄空」對齊 ext-f3,V6 冪等三分支自洽;V1-V5 正規化 tuple 口徑一致對得上 env.resolve/E2/E3;砍第三欄「人剪錯可能重加」誠實標本身沒問題,d-f4 挑的是相序缺可觀測完成訊號非砍欄本身錯;_append_decision_ref 落盤 exact-string 與外層 _dref_same 兩層不衝突。
