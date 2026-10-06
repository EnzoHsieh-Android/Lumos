severity: clean

## R1

severity: clean

blocking: 否

verdict: evidence

引句:「只在已讀取有效 UTF-8 快照時辨認零引句；不把讀不到快照誤報成零引句。」

源碼佐證 file: `scripts/lumos:9565`  
源碼佐證 file: `scripts/lumos:9585`  
源碼佐證 file: `scripts/lumos:22925`

觀察 HIT：現象成立。輸入為「既存、非空、含非法 UTF-8 位元組的 snapshot＋帶 `findings_set` 的載體報告」時，`Path(snapshot).read_text(encoding="utf-8")` 拋 `UnicodeDecodeError`；該例外不是 `OSError`，現碼不捕捉，因此在引句判定前中斷，不進後續 `_sha256_file` 留痕路徑，也不追加 canary 帳。讀側第④步則明確捕捉 `UnicodeDecodeError`，將其列為 quote-check 失敗。

blocking判準 MISS：凍結 spec 字面把新判準限定於「已讀取有效 UTF-8 快照」。S4 只要求「快照缺失」沿用既有 IO 錯誤出口；例外範圍又明載不吞非本案例外。因此非 UTF-8 是既有輸入錯誤：目前雖以未捕捉例外結束，但不會被新增的「零引句」判準誤報。新機制必須保證的是：有效 UTF-8 載體零引句才 rc2、缺失快照仍走既有 rc2、帳不變；並未承諾把所有解碼失敗正規化為 rc2。

最後結論：不必先把非 UTF-8 snapshot 改成 rc2 才能放行實作；若要改善其錯誤體驗，應另案擴張輸入契約與測試，不是本 spec 的 blocking 缺口。