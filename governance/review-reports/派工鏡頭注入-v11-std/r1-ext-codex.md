### f1

同一條 ★INVARIANT★ 可綁多支測試；若其中一支存在、另一支懸空，第 157、158 行會同時符合，未規定應取最壞狀態。現有閘會逐支產生項目，任一懸空即擋，因此若照第 157 行判成「有」，鏡頭會掩蓋實際阻擋狀態。

引句:「行含 `[test:…]` 且解得出、方法在測試索引裡」

file: `governance/review-reports/派工鏡頭注入-v11-std/r1-snapshot.md:157`

file: `scripts/lumos:16854`

severity: major  
blocking: 是

### f2

現有 `_lens_contract_lines` 先把合約行截成 200 字；若 `[test:]` 位於截斷點後，照「已在印的合約行直接餵」實作會標成無綁定，但硬閘的 `extract_contracts` 讀完整 summary，仍會找到並執行該測試。規格須明定用未截斷原文分類、截斷只用於顯示。

引句:「合約行=base 版節點文字(已在印;`resolve_test_refs` 吃字串,可直接餵)」

file: `scripts/lumos:16580`

severity: major  
blocking: 是

### f3

「分支上新增同名假測試所以假的擋得住」與現碼不符：只要空殼方法被測試索引認成 real，閘就會執行它，而 rc=0 即放行，並不驗證測試是否有有效斷言。這會讓審查員把 `[綁定測試:有]` 誤讀成假測試可由閘攔下。

引句:「閘會真跑那支測試所以假的擋得住」

file: `scripts/lumos:16863`

file: `scripts/lumos:16906`

severity: major  
blocking: 是

總結:最高 severity major，blocking 3 條。
