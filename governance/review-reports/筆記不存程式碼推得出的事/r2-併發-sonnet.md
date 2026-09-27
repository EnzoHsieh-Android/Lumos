severity: blocker

〈開頭白話 / 依據 / PRIOR-ART / RETIRE-IF / REVISIT〉已讀,無 finding

〈判定者能不能用:小實驗(2026-09-27)〉已讀,無 finding

## F1 CI 對新分支首推的起點沒有指定用分岔點,鄰接的既有寫法會用空樹起算

severity: blocker
blocking: 是 —— 不改,CI 會對每一個新分支的第一次推送都用空樹當起點,把整庫既有筆記行當成新增,重現 r1 已修掉的 57,474 行誤判,但只在 CI 端;第一次接線就會全面卡住新分支推送

引句:「那樣第一次推新分支會把整庫舊筆記當成新增(r1 外家席實跑:整庫 57,474 行),違反 d2」

1. 輸入:任何一個新分支第一次 `git push`(GitHub Actions 的 push 事件對新分支一定給 `github.event.before` 全零)。
2. 走到哪:spec〈共用〉節把「CI=這次推送的前後兩個版本」與「新分支或本機沒有遠端那個版本時,起點改用分岔點」寫成同一條規則,但只用本機語彙(「本機沒有遠端那個版本」)描述判斷條件,沒有寫 CI 端要怎麼從 `github.event.before` 判斷同一種情況、也沒有寫 CI 端要 fetch 哪個 ref 才能算出「跟預設分支的分岔點」。
3. 壞在哪:本 repo 現有 `.github/workflows/ci.yml:109-111`(code-loop gate 那一步,正是本計劃 PRIOR-ART 明講要照抄機制形狀的鄰居)已經有一段處理 `BEFORE` 全零的既有寫法——`EMPTY=4b825dc642cb6eb9a060e54bf8d69288fbee4904`、`case "$BEFORE" in 0000000000000000000000000000000000000000|"") BEFORE="$EMPTY";; esac`——這正是 spec 自己點名要避開的「空樹起算」。因為 spec 沒有另外交代 CI 這兩個新步驟該怎麼判斷「這是新分支的第一次推送」並改用分岔點,實作者順手照抄旁邊這段既有 CI 樣板(本來就是同一個 job、同一個 `BEFORE`/`SHA` 環境變數命名慣例)幾乎是最省力的寫法,而那樣寫出來的 `note-shape --diff`/`note-audit check --diff` 在新分支首推時會算出 `空樹..HEAD` 的整庫差異,得到一份跟本機（用分岔點算出的小範圍)完全不同的新增行集合與集合指紋,`check` 在治理帳找不到吻合的通過紀錄,CI 會擋下——即使本機已經正常 prepare/record 過。
4. 佐證:file: `.github/workflows/ci.yml:109-111` `EMPTY=4b825dc642cb6eb9a060e54bf8d69288fbee4904` 與 `case "$BEFORE" in 0000000000000000000000000000000000000000|"") BEFORE="$EMPTY";; esac` 就是 spec 明文否定的空樹起算寫法,而它是本計劃 PRIOR-ART 段指名要抄的鄰居(code-loop gate)的既有實作。

## 做法 > 共用:哪些行算「這次新增的筆記行」——已涵蓋於 F1,其餘無 finding

## 做法 > 第一層:提交時擋形狀固定的東西——已讀,無 finding(唯讀判斷,不寫檔,無併發疑慮)

## F2 prepare 清單檔沒有指定原子寫入,兩個會談同時 prepare 時有機會被讀到寫一半的內容

severity: major
blocking: 是 —— 不改,審查員在極端時序下可能讀到截斷或空白的派工檔,判出來的結果不可靠,而 record 端沒有任何機制能偵測「報告是根據壞掉的清單寫的」

引句:「所以兩個會談同時跑不會互蓋、同一批內容重跑得到同一檔」

1. 輸入:兩個會談(內容相同、算出同一個集合指紋)同時各自跑 `note-audit prepare --diff <範圍>`,對同一個路徑 `.lumos/note-audit/<集合指紋>.md` 幾乎同時開檔寫入;第三方(其中一個會談馬上派出的審查員 agent)在這個時間窗口內開檔讀取。
2. 走到哪:spec 只講「集合指紋命名不互蓋、同一批內容重跑得到同一檔」,這是在講「最終內容語意相同」,完全沒提寫入方式;文中也沒有指名重用本 repo 已有的原子寫入原語。
3. 壞在哪:本 repo 已經為「兩個程序同時碰同一個檔案」這個問題寫過專用的安全寫法——`scripts/lumos:14140` 的 `_write_lf`(暫存檔+`O_EXCL`建立+`os.replace` 原子換名,doc 裡明講「任一步敗:tmp 丟棄,原檔不動」),`atomic_write_verify` 也是靠它才不留半截檔。如果 prepare 這裡沒有指名沿用這支,實作者最自然的寫法是 `open(path,'w').write(text)`,那是先截斷檔案、再逐段寫入,不是單一系統呼叫保證的操作;如果另一個進程或審查員 agent 在那個時間點打開同一路徑讀取,可能讀到空檔或只有前半份派工詞、缺派工詞的分類定義或缺清單本身,而審查員不會知道自己讀到的是不完整版——判出來的報告 record 端也驗不出「這份報告是不是根據截斷的清單寫的」(record 只驗每行都有判定、判定合規則,不驗清單檔本身的完整性)。
4. 佐證:file: `scripts/lumos:14140` `def _write_lf` 建臨時檔案再 `os.replace` 換名;`scripts/lumos:14158` `def atomic_write_verify` 註解「寫 tmp → re-parse 自驗 + lint 無新指紋 → atomic rename。任一步敗:tmp 丟棄,原檔不動」——這正是 spec 沒有指名重用的既有安全寫法。

## F3 note-audit 新增的寫入指令沒有交代 `_vault_write_lock` 逾時(60 秒)時該回什麼

severity: major
blocking: 是 —— 不改,實作者照 S1–S15 逐條做完仍可能漏接這個例外;鎖逾時時使用者看到的是裸 Python traceback,不是本專案自己要求的白話「擋下」訊息,而且沒有任何條款規定這時該回什麼 rc

引句:「兩個會談同時寫會壞行,讀端會靜默跳過」

1. 輸入:`note-audit record`/`skip`/`decision-amend` 這三支新指令都要走既有寫入鎖;鎖檔已有明文的 60 秒等待上限(`scripts/lumos:14260-14263`),等滿了會 `raise RuntimeError("等了 60 秒還輪不到寫入……")`。在我這個鏡頭安排的最壞時序下——例如同一個工作目錄有另一個會談長時間卡在同一個 vault 的寫入鎖裡(鎖檔要 30 秒 stale 才會被判定死亡並接手,期間又有第三個程序排隊)——這支新指令有實際機會撞到這個 60 秒上限。
2. 走到哪:spec〈第二層〉只寫「寫入走既有的 `_jsonl_append_verified` 並拿既有寫入鎖」,條款 S10 只驗「兩個行程同時 record 時,兩筆通過紀錄都應完整落在治理帳且讀得回」(驗的是鎖在時限內正常輪替的快樂路徑),S1–S15 沒有任何一條提到鎖逾時、也沒有指定這時候的回傳碼。
3. 壞在哪:本 repo 對「哪些既有指令要接這把鎖」有一致的既有慣例——每個會呼叫到會拋 `RuntimeError` 的路徑,都在 `main()` 自己那個分支包一層 `except (ValueError, RuntimeError, OSError) as e: print(f"擋下:{e}"); return 2`(例如 `scripts/lumos:32318`、`scripts/lumos:32324`,註解直接寫「守全專案 rc 協議」)。spec 的〈第二層〉第 4 點只講了「都過才寫...沒過就 rc1」和「不是 git 或找不到 lumos 就照既有 hook 慣例放行」兩種分支,完全沒提鎖逾時這第三種分支要落在哪個 rc;因為條款清單就是驗收標準,一份逐條符合 S1–S15 的實作可以完全不處理這個例外仍然通過所有列出的測試,鎖逾時時就會讓使用者看到裸 traceback,而不是 spec 自己在〈第一層〉明講的「回傳碼照鄰居」的白話擋下協議。
4. 佐證:file: `scripts/lumos:14260-14263` 逾時 `raise RuntimeError("等了 60 秒還輪不到寫入(同一個筆記庫有別的程序正在寫,或上一個寫入的程序卡住了),檔案沒動")`;file: `scripts/lumos:32318` `except (ValueError, RuntimeError, OSError) as e: print(f"擋下:{e}", file=sys.stderr); return 2` 是既有指令逐一手動接的既有慣例,spec 沒有交代 note-audit 的三支新指令要不要、在哪裡接這一層。

## 做法 > 第二層:推送前的筆記內容審——已涵蓋於 F2、F3,其餘無 finding

## 做法 > 上線前校準〉已讀,無 finding

## 做法 > 規範文字跟著改〉已讀,無 finding

## 條款(S1–S15)已讀:S9/S10 只驗鎖在時限內正常運作與 rebase/壓提交後指紋不變的快樂路徑,沒有一條對應 F1(CI 新分支起點)或 F3(鎖逾時回什麼),已在對應 finding 標明;其餘條款無 finding

## 回退〉已讀,無 finding(回退步驟本身沒有新的併發疑慮)

## 實務隱患〉F2、F3 直接對應這節「資源併發」那一條的兩個子句(「清單檔以集合指紋命名不互蓋」「同時 record → 走讀回自驗的寫入加寫入鎖」);F1 屬於同一大類(集合算出來要一致)但發生在這節沒提到的 CI/本機分歧場景,不是這節現有子句宣稱要處理的範圍。其餘(對外送出、可用性、已排除)無 finding

## 誠實界線〉已讀,無 finding

## 審計修正紀錄〉已讀,無 finding

總結:最嚴重 severity 為 blocker(F1);blocking 共 3 條(F1 blocker、F2 major、F3 major)。
