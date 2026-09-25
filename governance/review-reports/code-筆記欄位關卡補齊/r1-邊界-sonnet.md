severity: blocker

## F1 type 欄位寫成 YAML 清單會讓 `lumos doctor` 整個當掉(TypeError,不是這篇筆記的問題而已)

severity: blocker
blocking: yes

這批把 `_lint_collect` 從 `cmd_lint` 抽出來,新增的健檢 L 段擴充現在對**整個圖譜每一篇**都呼叫它(原本只有人手動 `lumos lint <單篇>` 才會走到這段判斷):

引句:「_e, _w = _lint_collect(env, rel)」

`_lint_collect` 裡沿用的舊判斷式是 `if t in _STATUS_ENUM and _st and _st not in _STATUS_ENUM[t]:`(這行不在 patch 改動範圍內,但現在被新的呼叫點以全圖規模觸發到)。只要圖譜裡任何一篇筆記的 `type:` 寫成 YAML 清單(而不是字串——這是這次補的欄位規則明講要防的「反過來」形狀之一,只是防在別的欄位上,`type` 本身沒防),`t` 就是一個 `list`,拿去當 dict key 直接炸:`TypeError: cannot use 'list' as a dict key (unhashable type: 'list')`。

翻紅重現(在 /tmp 複本跑,唯讀不動正式 repo):
```
cd /tmp/lumos-boundary-test   # git clone + git apply r1-snapshot.patch 於 f3a06bab 之上
cat > "docs/lumos-toolchain-knowledge/Systems/邊界測試筆記.md" <<'EOF'
---
type:
  - system
  - project
created: 2026-09-25
summary: 邊界測試
---
body
EOF
python3 scripts/lumos doctor
```
結果:doctor 印到 `[L]` 段(★這段就是本批新加的整圖掃描★)時整支程式丟出未接住的 `TypeError`,exit code 1,後面 M 段以後的所有健檢(狀態漂移、快照…)完全不跑。

★這不是只有 warn 模式才會、也不是只有本 repo 這種「gate: on」的專案才會踩到★:我把 `.lumos/config.json` 的 `note_lint` 整段拿掉(退回沒設定、預設 `warn`)重跑同一份壞筆記,一樣crash、一樣 exit 1、一樣的 traceback。因為 `_nl_mode == "off"` 才跳過這段整圖掃描,`on`/`warn` 兩種都會執行到 `_lint_collect`。也就是說任何消費專案只要升級到這批、圖譜裡剛好有一篇 `type` 被人手寫成清單(或機械匯入工具生的清單),`lumos doctor`(pre-push / CI 的閘)就會對著全 repo 硬當,而不是只擋那一篇、只警告那一篇——波及面遠大於作者的說法「④四類筆記 status 必填…about_code 每項…」預期的「擋這一篇、印一條訊息」。

## F2 `.lumos/config.json` 整份不是物件(null/陣列/純量)時,壞掉的設定被當成「沒設」悄悄吃掉,不出聲

severity: major
blocking: no

`_note_lint_config` 的設計說法(docstring)講得很清楚:「讀不了、JSON 壞掉、是捷徑檔、note_lint 不是物件 → 用預設並警告」。但只驗了「`note_lint` 這個鍵不是物件」,沒驗「整份設定檔本身不是物件」:

引句:「nl = data.get("note_lint") if isinstance(data, dict) else None」

當 `data` 因為 `isinstance(data, dict)` 是 False(例如整份檔案內容就是合法 JSON 的 `null`、`[]`、`"hello"`、`42`)時,直接走 `else None` 分支,而 `nl is None` 那條路徑回傳的是空的 `warns` 清單,完全不印任何警告——跟檔案內容是空字串(`json.loads` 直接丟 `JSONDecodeError`,那條路有警告)待遇不一樣。

翻紅重現:
```python
# 於 /tmp/lumos-boundary-test(已套用 r1-snapshot.patch)
import importlib.machinery, importlib.util, sys
loader = importlib.machinery.SourceFileLoader('lumosmod', 'scripts/lumos')
spec = importlib.util.spec_from_loader('lumosmod', loader)
m = importlib.util.module_from_spec(spec); sys.modules['lumosmod']=m; loader.exec_module(m)
import tempfile, os
for content in ("null", "[]", '"hello"', "42"):
    d = tempfile.mkdtemp(); os.makedirs(d+"/.lumos")
    open(d+"/.lumos/config.json","w").write(content)
    print(content, "->", m._note_lint_config(d))
```
四種都印 `('warn', [])`——模式退到預設 `warn` 沒錯,但 warns 是空的,使用者完全看不到「你的設定檔壞了」這件事,跟同一支函式對「JSON 讀不了」「note_lint 不是物件」兩種壞掉都會印警告的行為不一致,違反自己寫的 docstring 承諾。不擋提交、不影響現有規則,所以標 major 不是 blocker。

## 已驗過、沒問題的路徑

以下輸入形狀有照鏡頭清單逐一試過,行為正確:

- `about_code` 帶 `../` 逃出 repo、絕對路徑、跑到圖譜資料夾裡:`_about_code_path`(沿用既有函式,這次只多接了「在圖譜資料夾裡」這條)三種都正確擋下並給出對應訊息,不會誤放行也不會 crash。引句:「target.relative_to(env.vault.resolve())」
- 完全沒有開頭欄位(整篇沒有 frontmatter)的筆記:`n.fields` 是空 dict、`n.fm_lines` 是空清單,`_lint_new_rules` 每個迴圈都乾淨跳過,不 crash,原有的「沒寫 type」錯誤照常擋。
- `lands_in` 寫成單一字串而不是清單:`as_list()` 會把字串包成單元素清單,只要那個字串本身符合 `Systems/<名>` 形狀就正常通過,沒有被誤判成「格式不對」。
- decisions 的 `decided` 帶時間(`2026-09-20T10:00`)、`valid` 寫成清單:兩者都正確被新規則抓出來當 warning(warn 模式)或 error(on 模式),不會 crash、訊息雖然把清單印成 Python repr(`"['true', 'false']"`)但不影響判定正確性。引句:「第 {i} 條 decisions 的 valid 只能是 true 或 false,你寫的是 {str(v)!r}」

## F3(⚠ 判不準,僅記錄不升級)`type` 本身寫成清單時,status-必填規則會被整條繞過

severity: minor
blocking: no

跟 F1 同一個輸入(`type` 是清單)有第二個效果:就算沒有 F1 那個 crash(假設之後修掉了),`_lint_new_rules` 裡 `if t in _NOTE_STATUS_REQUIRED_TYPES:` 這行只認字串完全比對,`t` 是清單時恆為 False,於是「四類筆記 status 必填」這條新規則被整條繞過而不出聲——跟作者說的「四類筆記 status 必填」預期不符,但因為欄位形狀本身已經是明顯寫錯(type 不該是清單),影響範圍限縮在「錯上加錯」的邊角情境,且被 F1 的 crash 蓋過,獨立影響有限,標 minor。

引句:「if t in _NOTE_STATUS_REQUIRED_TYPES:」
