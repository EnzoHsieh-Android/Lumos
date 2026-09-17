severity: minor

## F1 圍欄修法的同一支剝行內程式碼函式,會被同一行上一個沒關的反引號吃掉後面的真連結(門判定訊號 2 與推送前重判都用同一份,漏偵測一致但仍是漏偵測)

severity: minor
blocking: no

`_plan_system_links(note, text=..., ...)` 這輪改成先 `_visible_lines` 再 `_strip_inline_markup(ln)[0]` 才抓 `[[連結]]`,目的是把圍欄裡的示範語法排除掉(delta 裡的 F1 修復)。但 `_strip_inline_markup` 的既有規則是「同一行只要出現落單的反引號,那個反引號★之後的內容整段丟掉★」:

引句:「if "`" in s: return s.split("`", 1)[0], True」

在正文散文裡打字如果不小心留了一個沒關的反引號,同一行後面才寫的真連結就會整段消失,不會進 `WIKILINK_RE.findall`。用實際程式碼片段重現(在 worktree 裡跑,不是猜):

```
text = "這裡有個 ` 沒關的反引號 [[Systems/Risky]]\n"
for no, ln in lumos._visible_lines(text.splitlines()):
    vis, cut = lumos._strip_inline_markup(ln)
    # vis == "這裡有個 "、cut == True、WIKILINK_RE.findall(vis) == []
```

這支函式同時餵給 `_door_judge`(門判定訊號 2:計劃連到帶 ★IRREVERSIBLE★/★CHECKPOINT★ 合約或 risk/ 標籤的節點,命中就是硬單向門)與 `_spec_gate_push_check` 的推送前重判(`now = _door_judge(env, n, text)`)。如果一份計劃正文寫到某個真的連到高風險節點的 `[[連結]]`,但同一行前面剛好有個沒關的反引號(常見手誤,例如打程式碼片段忘了補右反引號),這條連結會在寫入時判門(該算單向卻算成雙向)、以及推送前重判(同一支函式、同一個盲點,不會被抓到「留痕時雙向、現在單向」而擋下)都一併漏掉——雙向門不派人審,這個訊號一旦漏就是整條防線繞過去。

不算全新的洞:`_strip_inline_markup` 的「未閉合反引號之後一律不信」是既有、已在別處(PITFALL_CLASSES 關鍵字掃描,即門判定訊號 1)用過的設計取捨,docstring 也寫明是刻意的(寧可少認)。這輪只是把同一個取捨★第一次★套用到連結判定(訊號 2)上,而訊號 2 直接決定要不要繞過設計審——風險面比訊號 1(關鍵字掃描,通常句子本身就會再命中別處)略高一點,值得留意但不是這輪引入的新邏輯錯誤。

## F2 `_spec_gate_push_check` 假設圖譜一定不在 repo 根目錄,vault 直接放在 repo 根時 plans/systems 偵測會靜默永遠是空集合

severity: minor
blocking: no

```
vrel = str(env.vault.resolve().relative_to(rr)).replace(os.sep, "/")
...
plans = {t[len(vrel) + 1:] for t in touched if t.startswith(vrel + "/Projects/") and t.endswith(".md")}
systems = {t[len(vrel) + 1:-3] for t in touched if t.startswith(vrel + "/Systems/") and t.endswith(".md")}
code = [t for t in touched if not t.startswith(vrel + "/")]
```

引句:「plans = {t[len(vrel) + 1:] for t in touched if t.startswith(vrel + "/Projects/") and t.endswith(".md")}」

如果圖譜 vault 剛好就是 repo 根目錄(`vrel == ""`),`vrel + "/Projects/"` 會變成 `"/Projects/"`,而 `git diff --name-only` 印出來的路徑一律是相對路徑、不帶開頭斜線,`t.startswith("/Projects/")` 永遠是 False。結果是這次推送不管動了幾份雙向門計劃或它們的家,`plans`/`systems` 都會是空集合,函式直接 `return 0` 放行——而且★沒有任何一行提示訊息★(跟同一支函式其他 fail-open 分支不一樣,那些都印一句「算不出來,放行」)。用 python 直接驗証過:`"Projects/foo.md".startswith("" + "/Projects/")` 為 `False`。

這輪 diff 沒有改到這段(它是 r1/r2 就有的既有邏輯,只是仍在本次審材範圍 e067c16..HEAD 的整批新增函式裡),而且本專案自己的圖譜固定在 `docs/lumos-toolchain-knowledge/`(CLAUDE.md 明文規定的慣例),`vrel` 實務上不會是空字串,所以現在不會踩到。但這支函式本身沒有防呆,若哪個消費專案把 vault 直接放在 repo 根,雙向門推送閘會整個失效卻不吭聲,跟其它 fail-open 分支「至少印一句」的風格不一致。

## 複核

①圍欄裡示範語法的連結:已用 `python3 scripts/test_lumos.py -k spec_gate_body_link_in_fence` 在乾淨 worktree(`/tmp/seat-r3-reviewer`,detached HEAD 097a647b)重驗,2 個子案例(圍欄/行內程式碼裡的連結不算門訊號、圍欄外的真連結照算)全過。另外直接讀 `_visible_lines` 的實作(scripts/lumos:2944):它是既有、經過 2026-08-03/2026-09-16 兩輪代碼審打磨過的唯一 fence 判定,對「未閉合圍欄」有兩段式讀法(先照 CommonMark 讀,讀不完整份退回寬鬆讀法),不是這輪新寫的邏輯,行為符合文件描述。`_plan_system_links` 改成走 `_visible_lines` + `_strip_inline_markup` 之後,圍欄內的 `[[Systems/Risky]]` 確實不再被 `WIKILINK_RE.findall` 抓到——修復本身有效,唯一的殘留風險是 F1 講的「未閉合反引號截斷同一行後面的真連結」,這是 `_strip_inline_markup` 既有行為的延伸套用,不是這次修復本身失敗。

②推送前反查家改走 `_impact_home_map`+`_nodehome_key`:已用 `python3 scripts/test_lumos.py -k prepush_spec_gate_code_home` 重驗,2 個子案例(①只碰程式檔經家找到計劃、②家已作廢 superseded 不算家)全過,確認 status 過濾確實生效(改用唯一算法前用自己掃 about_code 不會過濾 superseded)。核對過 `_nodehome_key`(`nfc(_posix_norm(strip_quotes(...)))`)與 `_spec_gate_push_check` 的 `code` 清單同樣是 repo 根相對路徑(git diff --name-only 輸出、加了 `core.quotePath=false`),跟 `about_code` 欄位存的慣例(repo 根相對,如「scripts/lumos」)同一種形式,沒有發現路徑形式不對齊的情況。`_HOME_MAP_CACHE` 是模組層級字典、鍵是 `str(env.vault)`,但確認 `run()`(test harness)與 pre-push hook 的真實呼叫都是各自獨立的 subprocess(`subprocess.run([sys.executable, GRAPHCTL, ...])`),同一個 python 行程裡不會有「圖譜在行程內被改過、快取還是舊答案」的情境,cache 對這個用法沒有實際踩雷路徑。
