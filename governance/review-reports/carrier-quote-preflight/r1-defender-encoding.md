severity: minor

## R1

severity: minor

blocking: MISS

verdict: evidence

引句:「只在已讀取有效 UTF-8 快照時辨認零引句；不把讀不到快照誤報成零引句。」

觀察 HIT：現象成立。輸入為「合法 UTF-8 載體報告＋處置集合＋存在、非空、含非法 UTF-8 位元組的 snapshot」時，`read_text` 會拋出 `UnicodeDecodeError`；此處只捕捉 `OSError`，而前者繼承 `ValueError`、不是 `OSError`，因此目前會裸例外。後續二進位 hash、留痕落帳均尚未執行。

源碼佐證 file: `scripts/lumos:9565`

源碼佐證 file: `scripts/lumos:9568`

源碼佐證 file: `scripts/lumos:9569`

源碼佐證 file: `scripts/lumos:9585`

源碼佐證 file: `scripts/lumos:9657`

讀側第④步則明確捕捉 `UnicodeDecodeError`，把既有帳中的此類載體判為 quote-check 失敗，而非成功。

源碼佐證 file: `scripts/lumos:22925`

源碼佐證 file: `scripts/lumos:22928`

blocking 判準 MISS：凍結 spec 字面只要求在「已讀取有效 UTF-8 快照」後新增零引句 rc2；S4 明定的是快照「缺失」所走的既有 IO 出口，例外範圍又要求不吞非本案例外。非 UTF-8 snapshot 的裸例外是既有畸形輸入處理缺口，但不是這次新增零引句判準造成的洞。新機制只須保證它不被誤報成零引句、不追加帳列；不必順帶把既有解碼例外改造成 rc2。

最後結論：不必先擴寫 spec 或把非 UTF-8 snapshot 改成 rc2 才能放行實作；可另案改善 CLI 錯誤品質。