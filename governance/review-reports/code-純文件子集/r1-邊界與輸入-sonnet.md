severity: blocker

## F1 副檔名不在硬編清單裡的程式檔,放進 governance/ 或 docs/ 就被當成純文件,pre-push 與 CI 一起漏測

severity: blocker
blocking: yes

`_docs_only_file` 判一支檔算不算「純文件」時,對「有副檔名但副檔名不在 `_NODEHOME_CODE_EXTS`」的檔案,直接放行當文件,完全不檢查內容:

引句:「if kind != "shebang?":」
引句:「if not any(path == w or (w.endswith("/") and path.startswith(w)) for w in _DOCS_ONLY_PATHS):」

`kind = _nodehome_code_kind(path)` 只回三種值:`"ext"`(副檔名在清單裡)、`"shebang?"`(沒副檔名)、`None`(有副檔名但不在清單裡)。`_docs_only_file` 的邏輯是「`kind=="ext"` → 不是文件;其餘(`kind != "shebang?"`,也就是包含 `None` 這種情況)→ 是文件」。問題出在 `None` 這一支根本沒做首行 shebang 檢查就直接判定為文件——這條路只對「有辨識到的副檔名」有效果,對「副檔名沒被收錄」完全失效。

而 `_NODEHOME_CODE_EXTS`(`file: \`scripts/lumos:20457\``)只收錄了 `.cs .vue .js .ts .tsx .jsx .mjs .sql .py .kt .kts .java .swift .go .rs .c .cc .cpp .h .hpp .sh .ps1` 這 22 種,連這個 repo 自己有 skill 支援的 Dart(`dart-idioms`)都不在裡面,更別說 Ruby/PHP/Perl/Lua/R/Elixir/Haskell 等。

重現(在 /tmp 開的乾淨 repo,不是本 repo):
```
mkdir -p governance/tools
cat > governance/tools/scan.rb <<'EOF'
#!/usr/bin/env ruby
def risky_delete!
  system("rm -rf /some/real/path")
end
EOF
git add -A && git commit -m "add ruby script under governance/"
```
直接呼叫這批新加的函式:
```
>>> m._nodehome_code_kind('governance/tools/scan.rb')
None
>>> m._docs_only_file('<repo>', 'governance/tools/scan.rb', 'HEAD~1')
True
>>> m._test_suite_for_range('<repo>', 'HEAD~1..HEAD')
('docs', '改到的只有 README、docs、assets 這類文件(沒碰程式與 skills)')
```
一支帶真實邏輯(`system("rm -rf ...")`)的 Ruby 程式檔,被判定「沒碰程式」。

為什麼是 bug 而不是風格:`_test_suite_for_range` 的結果直接決定 pre-push 與 CI 要不要跑全套(`suite == "docs"` 時兩邊都只跑文件子集)。CI 那端的判斷用的是同一支 `_pitfall_diff_collect`→`_test_suite_for_range`(patch 裡 `scripts/lumos` 的改動),不是獨立算法,所以**沒有第二層防護**——不像 F2 那樣有「CI 對非純文件一律跑全套」當後盾。任何語言副檔名沒被收進 `_NODEHOME_CODE_EXTS` 的程式檔,只要放進 `docs/`、`assets/`、`diagrams/`、`governance/` 底下,整條「純文件推送」機制在推送前跟 CI 都會把它當空氣,測試全套被跳過。這正是這批 patch 自己聲稱要守住的底線(「★白名單不是『非程式檔』★」「保守方向是多跑,不是少跑」),但 `None` 這一支剛好反過來。

## F2 affected_keys 用逗號序列化,但值本身可能含逗號,round-trip 後被拆成錯的關鍵字

severity: major
blocking: yes

`scripts/lumos` 新增的 `_affected_test_keys` 用檔名(去副檔名)當關鍵字之一:

引句:「b = f.rsplit("/", 1)[-1]」

這個 basename 沒有做逗號跳脫。pre-push 把這份清單序列化成逗號分隔字串:

引句:「",".join(json.load(sys.stdin).get("affected_keys", []))」

再傳給 `test_lumos.py` 的 `--keys`,那邊又用逗號切回來:

引句:「_keys = [k.strip() for k in _args.keys.split(",") if k.strip()]」

重現(在乾淨的 /tmp repo,新增一個檔名含逗號的檔案並跑真正的 `_affected_test_keys`):
```
mkdir -p x && printf 'y=1\n' > "x/foo,bar.py"
git add -A && git commit -m "add comma file"
>>> m._affected_test_keys('<repo>', 'HEAD~1..HEAD')
['foo,bar']
>>> ",".join(['foo,bar'])
'foo,bar'
>>> [k.strip() for k in 'foo,bar'.split(",") if k.strip()]
['foo', 'bar']
```
原本一個關鍵字 `foo,bar`(檔名 `foo,bar.py` 去掉副檔名)被拆成兩個獨立關鍵字 `foo` 與 `bar`,`test_lumos.py --suite keys` 挑測試時就會照這兩個破碎的字面值去比對,跟原始檔名完全對不上。

為什麼是 bug 而不是風格:這是關鍵字清單在三個檔案之間傳遞時的協定沒處理分隔字元衝突,屬於「做出錯的行為」——選出來的測試子集不再對應真正改到的檔名。不是 blocker 是因為這條路只在推送前掛鉤的「light」快路徑生效(pre-push 專用,`_SUITE_KEYS`),而 CI 端對任何非純文件改動一律照 F1 修好後的邏輯跑全套當後盾(前提是 F1 本身沒把它誤判成 docs);在目前 F1 尚未修的狀況下,含逗號檔名若剛好也落在 F1 的漏洞路徑,兩個問題會疊加,但各自獨立成立、值得分開列。

## F3 訊息本身自相矛盾:「跑文件子集(不跑全套)」後面直接接「全套約 8 分鐘」

severity: minor
blocking: no

`scripts/hooks/pre-push` 印使用者看的等待訊息時,`_suite_word` 已經把「不跑全套」的說明包進去,外層又固定接了「全套約 X 分鐘」字樣:

引句:「_suite_word="文件子集(這次沒改到程式、或改動判成 light,不跑全套)"」
引句:「echo "推送前先跑$_suite_word(全套約 8 分鐘;嫌久可 --no-verify,CI 會兜底)…" >&2」

實測兩者串接後的輸出:
```
推送前先跑文件子集(這次沒改到程式、或改動判成 light,不跑全套)(全套約 8 分鐘;嫌久可 --no-verify,CI 會兜底)…
```
同一句話裡「不跑全套」跟「全套約 8 分鐘」相鄰出現,多分片那一支(`切成 $_shards 片同時跑,全套約 4-5 分鐘`)是同一個模式,一樣的問題。

為什麼不是純風格:這不是措辭好不好看的問題,是「全套約 X 分鐘」這個耗時估計對正在跑的文件子集/keys 子集根本不成立(子集通常幾秒到幾十秒跑完),使用者會被誤導覺得這次推送還要等 8 分鐘,可能因此多按一次 `--no-verify` 跳過原本很快就能過的檢查,或反過來以為子集也要等很久。屬於資訊本身錯誤,不是文字風格偏好,但不影響測試實際跑對跑錯,所以列 minor。
