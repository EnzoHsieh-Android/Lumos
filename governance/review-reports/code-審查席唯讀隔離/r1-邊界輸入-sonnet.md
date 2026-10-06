severity: major

### F1 Read 的路徑含 `..`、`//`、`/./` 或寫成相對路徑時,席報告暫存處照讀
severity: major
blocking: 是 — 守衛要擋的核心目標(別席報告)靠普通路徑寫法就繞過去,而且跟 Grep/Glob 的處理不一致
引句:「if (parts.some(s => s === '' || s === '.' || s === '..')) return null」
引句:「return real !== null && inStaging(real)」

`realOf` 遇到空段、`.`、`..` 回 `null`。Read 分支只在 `real !== null && inStaging(real)` 時擋,`null` 會落到放行。Grep/Glob 分支把 `null` 當擋下,Read 卻是放行,兩邊方向相反。

最小重現:node 跑 register.ts 的 `checkTool`,io 用 `fs.realpathSync.native`,staging 目錄實際存在。

| 輸入 | 結果 |
|---|---|
| `Read /tmp/lumos-seat-staging/r.md` | 擋下 |
| `Read /tmp/x/../lumos-seat-staging/r.md` | ALLOW |
| `Read /tmp//lumos-seat-staging/r.md` | ALLOW |
| `Read /tmp/./lumos-seat-staging/r.md` | ALLOW |
| `Read lumos-seat-staging/r.md`(cwd 為 /tmp 時) | ALLOW |

作業系統與 Read 工具都會把這些寫法化簡成同一個檔。建議 Read 在 `real === null` 時也擋(跟 Grep/Glob 一致),或先正規化再判斷。

### F2 Bash 字樣粗擋用「路徑段」比對,在本 repo 常見的唯讀指令上誤擋
severity: major
blocking: 是 — 審查席最常做的 `cat`、`git diff`、`git log` 在這個 repo 被擋,只能繞去用 Read 工具
引句:「const words = new Set(cmd.split(/[^A-Za-z0-9_.-]+/).filter(Boolean))」
引句:「if (words.has('git')) for (const w of GIT_PUSH_WORDS) if (words.has(w)) return」

分詞把 `/`、空白、引號、`=` 都當分隔,所以任何位置的 `claude`、`gh`、`push` 都算命中,不管它是不是命令。實測結果如下。

| 指令 | 結果 |
|---|---|
| `cat mods/claude/lumos-guard/hooks/register.ts` | 擋(「claude」) |
| `git -C /r diff -- mods/claude` | 擋(「claude」) |
| `grep -rn "git push" docs` | 擋 |
| `git log --grep=push` | 擋 |
| `git log -- scripts/push` | 擋 |
| `curl https://github.com/gh/foo` | 擋(「gh」) |

`mods/claude/` 是本 repo 真實目錄。審查本 repo 的 pre-push 相關改動時,`git ... grep push` 也很常見。

反方向漏擋有兩種,前一種有人為意圖,第二種是無意:
- `ls /tmp/lumos-seat-st*` 通過(萬用字元)。
- `grep -r x /tmp` 通過。
- 上面兩條同一目的的 Grep 工具呼叫會被擋,所以這是 Bash 與 Grep 的規則不一致。

### F3 標記不在「第一個非空行行首」時靜默放行,沒有提示
severity: minor
blocking: 否 — 屬於 fail-open 且符合設計文字,但沒有任何提示,範本一寫歪守衛就整個失效
引句:「if (!SEAT_LOOSE_RE.test(line)) return { kind: 'none' }」

`parseMarker` 實測結果如下。

| 派工詞第一個非空行 | 結果 |
|---|---|
| `` `LUMOS-SEAT: a/b/c` `` | none |
| `# LUMOS-SEAT: a/b/c` | none |
| `**LUMOS-SEAT:** a/b/c` | none |
| 第一行是「你是外部 reviewer」,第二行才是標記 | none |

這幾種都回 `none`,子代理不受任何限制,也沒有 toast。相對地,全形冒號 `LUMOS-SEAT：` 會被當 bad 而擋下,所以加了 markdown 修飾的寫法反而比全形冒號更危險。

反向誤擋也在同一行:`^lumos-seat` 不分大小寫又不要求冒號,第一行是 `Lumos-seating plan` 的一般派工會被 deny。

### F4 `realOf` 對超長路徑是平方級,工具呼叫會卡很久
severity: minor
blocking: 否 — 要送出極長路徑才會觸發,不是常態輸入
引句:「for (let n = parts.length; n >= 0; n--) {」

Read、Write、Grep 的路徑沒有長度上限(Bash 才有 `BASH_MAX`)。路徑不存在時,這個迴圈每往上一層就 `slice` 加 `join` 並呼叫一次 `io.real`。實測用假 io(沒有真實 stat 成本):
- 5,000 段:0.1 秒。
- 20,000 段:1.8 秒。
- 40,000 段:9.0 秒。

真實 `$.fs.stat` 還會再加上每次呼叫的成本。建議先限制長度,或改成二分搜尋已存在的上層。

### F5 市集檔 `plugins` 為 null 或數字時,`_lumos_plugin_listed` 丟出沒被接住的 TypeError
severity: minor
blocking: 否 — 市集檔是自己 repo 的檔,實際上 `marketplace add` 通常會先擋掉
引句:「except (OSError, ValueError, AttributeError):」

用 python 重現:`{"plugins":null}` 與 `{"plugins":5}` 都丟 `TypeError`,會把整個 install 帶倒。`except` 沒收 TypeError。

其他怪值實測行為如下,沒問題:
- `plugins` 是 dict 或頂層是 list:回空集合。
- 重複的 name:去重。
- name 缺:變成 `None@lumos-toolchain`,不影響結果。

另外,檔首有 BOM 時 `json.loads` 丟 ValueError,結果是回空集合,兩支外掛都被當成「市集沒有它」而靜默略過(`no-source`)。

### 固定席逐條
- 派工詞解析:CRLF、BOM(U+FEFF)、全形空白(U+3000)開頭、純空白行都能正確跳過,值含中文與 emoji 可用。四段值、空段、全形冒號會被擋。標記值內含 U+200B 零寬字元時會被當合法名稱,對安全無影響。
- 路徑:`/tmp` 與 `/private/tmp`、`/var/folders/.../T` 與 `/private/var/folders/.../t` 的大小寫與連結都正確處理。尾斜線、根目錄 `/`、剛好等於工作資料夾本身都符合預期。Write 對 `..` 與 `//` 一律擋(保守但安全)。
- Grep/Glob:`path` 為空字串、省略、`./`、絕對根都符合預期。`pattern` 的第一個萬用字元在第一段時,基底退到 `/`,會正確擋。`/tmp/lumos-seat-work/*/../../lumos-seat-staging/*` 這種「萬用字元之後才出現 `..`」的寫法目前放行。是否能真的走出去取決於引擎 glob 是否解讀 `..`,未能重現,所以不列 finding。
- Agent:`isolation: ''` 會被當成有設值而擋下。`subagent_type` 大小寫需完全一致,這點跟引擎是否大小寫敏感有關,未驗證。
- 型別檔 `FsStat.realPath`:不存在時 stat 會 reject,懸空連結的語意依型別檔是「realPath 缺席」。`realOf` 把兩者分開處理(reject 往上找、缺席擋下),但實際引擎對懸空連結是 reject 還是缺席,這裡沒驗證。若是 reject,在工作資料夾內預先放一個指向 repo 的懸空連結,Write 就會寫出去。這屬於有心繞過,設計文字已聲明不防,所以未列。
- 圖譜牽連與合約檔:沒有跟輸入處理直接相關的條目。

總結:最嚴重 major,blocking 2 條
