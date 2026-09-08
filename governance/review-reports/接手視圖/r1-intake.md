# r1 intake — 接手視圖(代碼審,外家 Codex,2026-09-07)

preflight-4: n/a(代碼審,非設計審)

材料:`r1-snapshot.diff`(工作樹相對 HEAD 的 diff,sha256 前 16 碼 0ccce79b6fe11bf9)、派工詞 `r1-codex-prompt.txt`、報告本體 `r1-外家codex.md`(從逐字稿最後一個 `severity:` 切出;完整逐字稿 `r1-外家codex-transcript.md`)。
席位宣告 severity: major,5 條。收貨方式:每條先自己重現「觀察」,再獨立判「判準」。

## 逐條

- **#1 輪次邊界被系統行截斷 — HIT,折**。重現:`t_tail_meta` 那組 fixture(人話→Edit→tool_result→isMeta 提醒)原本 `turn_files=[]`,席位觀察對;判準也對——接手者要的是「人話之後做了什麼」,不是「最後一個 type=user 行之後」。折法:`_handoff_claude_turn` 自算邊界(最後一句人話),只借 hook 的人話判定與 `EDIT_TOOLS`;Codex 逐字稿仍走 hook。測試加兩條(尾端 meta 提醒 / 一輪中間夾任務通知)。順帶觀察(不折、不動 hook):收工 hook 自己的邊界對 stop 閘可能也有同樣的漏——任務通知之後才做的 Edit 會被算成新一輪,通知之前的會漏;另案。
- **#2 多份候選逐字稿挑錯人 — HIT(設計缺口),折**。原碼只排掉自己、拿最新;同 checkout 多開時會把別人的尾巴當接手線索。折法:最新 10 份裡「提到這份計劃名」的最新一份優先,都沒提到才拿最新;候選清單印出、要指定用 `--transcript`。測試三段(提到者優先 / 都沒提到拿最新 / 只剩自己)。席位建議的「比對 cwd / branch」沒採:目錄 slug 已隱含 cwd;逐字稿每行有 `gitBranch` 可再加,等真挑錯一次再說。
- **#3 fail-open 有缺口 — 半 HIT,折**。席位舉的 `content: null` **不會炸**(hook 的人話判定對 None 回 False,實測);`session_meta.payload` 是 list **真的 traceback**(實測 `AttributeError: 'list' object has no attribute 'get'`)。折法:外層 `try/except` 兜住整段解析。測試兩條。
- **#4 路徑正則只吃 ASCII 無空白 — 觀察對,判準不採(accepted)**。理由:沿用派工鏡頭的正則是計劃明寫的設計;本 repo 程式檔路徑全 ASCII 無空白;要支援空白 / CJK 路徑得自寫路徑解析器=引入第二種做法。寫進計劃的天花板。回頭條件(綁事件):某份計劃點名含空白或非 ASCII 的路徑而漏列時,回這裡。
- **#5 唯讀命令執行 hook 檔頂層碼 — 觀察對,判準不採(accepted)**。理由:hook 與 `scripts/lumos` 同一信任域(同 repo、同 anchor 守衛,能改 hook 的人同樣能改 lumos 本身);實測 hook 頂層只有 def / 常數 / `__main__` 守衛(grep 頂層陳述只有那一行 `if __name__`)。回頭條件:hook 頂層新增副作用時(驗證筆記 revalidate_when 已寫)。

## 席位「未測」清單順帶折入
- rename:`git mv` 後計劃點名的舊路徑列成「已改名 → 新路徑」(status 改成整個 repo 問一次,舊路徑才會跟新路徑一起出現)。
- root 是子目錄(vault 不在 git toplevel):porcelain 路徑相對 repo 根,對齊後測到「已改」。

## 折入後
- `t_handoff_view` 41 條全綠;翻紅釘第二輪見計劃筆記實作紀錄。
- **帳:`canary record` 待合回主線後補**——審查帳本在主樹上另一個 session 也在寫,工作樹上記一筆合併時必衝突;reviewed 指紋以合併當下的計劃檔為準。
