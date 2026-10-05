severity: major

# 資源併發席

## r1：建鎖寫入失敗會留下永久空鎖

severity: major
blocking: 是
引句:「保留 `O_CREAT|O_EXCL` 的正常取鎖。已存在的鎖一律回未取得」
file: `scripts/lumos:33843`
`os.open` 成功後，`os.write` 或 `os.close` 拋 OSError 時函式回 False，卻未關 fd 或移除半成品。審查席注入寫入失敗得到 `False True b''`（依序為取得結果、鎖存在、鎖內容）；停掉自動接手後永久阻斷。需明定只清理由本次成功建立且身份仍相同的半成品，並補失敗紅燈。

驗收其餘、PRIOR-ART、RETIRE-IF、回退、實務隱患已讀，無 finding。

總結：最嚴重 severity: major；blocking 1 條。
