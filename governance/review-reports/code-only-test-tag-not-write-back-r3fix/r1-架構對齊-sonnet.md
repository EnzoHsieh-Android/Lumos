severity: minor

## 問 1 分層與依賴方向
結論:clean。新碼都在 `_nodehome_*` 區段內,向下呼叫既有的 `_NsTrJudge` 系(`_ns_tr_judge`、`_ns_tr_guard`、`_platform_test_index`)與 `_NS_TR_SPLIT_RE`、`_test_names_of`,沒有反向依賴或跨層直呼。對照:file: `scripts/lumos:29732`(`_test_names_of`)、file: `scripts/lumos:30015`(`_ns_tr_judge`)。
引句:「return _ns_tr_judge(repo_root, tip, pidx)[0]」

## 問 2 命名與錯誤處理
結論:clean。印提醒的寫法 `print(..., file=sys.stderr)` 加 `e.__class__.__name__`,跟鄰居一致;`except Exception` 後回 None 也跟「筆記測試綁定要存在」那道同形。常數用 `_NODEHOME_` 前綴,跟同區段命名一致。對照:file: `scripts/lumos:26565` 之類的 `_NODEHOME_*` 常數;提醒寫法對照 file: `scripts/lumos:18005`(同樣 file=sys.stderr)。
引句:「print(f"提醒:每支檔有家這次沒核對測試名({e.__class__.__name__}),只換測試綁定的筆記照舊算寫了說明", file=sys.stderr)」

`def bare(x)` 巢狀函式:專案已有同形的巢狀 `_bare`(file: `scripts/lumos:16191`,同樣是去平台前綴),不算新做法。命名上差一個底線前綴,但屬純風格,不列。
引句:「def bare(x):」

## 問 3 第二種做法
逐項對照:

1. `_NODEHOME_COMMIT_RE`:專案內判提交編號 `[0-9a-f]{7,40}` 已有多處,但都是行內 `re.fullmatch(r"[0-9a-f]{7,40}", bac)`(file: `scripts/lumos:39158`)或各自語境的常數(`_CTX_SRC_RE` file: `scripts/lumos:3707`、`_FULL_SHA_RE` 只收 40/64 碼 file: `scripts/lumos:45050`),沒有可共用的「短提交編號」常數。新常數語意(7 到 40 碼)與 39158 一致,等於再抄一份字面,但沒有既有常數可重用,不算第二種做法。clean。
引句:「_NODEHOME_COMMIT_RE = re.compile(r"[0-9a-f]{7,40}")」

2. `_NODEHOME_TAG_NAME_RE`:專案內判「測試名形狀」的是 `_KILL_METHOD_OK_RE`(file: `scripts/lumos:14567`),但它收空白與點號、用途是殺傷力配方方法名,這裡刻意只收單一識別字(含平台前綴),寬窄相反且註解寫明原因。不算第二份。clean。
引句:「_NODEHOME_TAG_NAME_RE = re.compile(r"(?:[A-Za-z0-9_-]+:)?[A-Za-z_][A-Za-z0-9_]*")」

3. `_NODEHOME_TAG_PREFIX_RE`:專案已有判平台前綴的 `_NS_TR_PREFIX_RE`(file: `scripts/lumos:29690`),`_test_names_of` 內就用它切前綴(file: `scripts/lumos:29746`)。新常數是同一件事(去掉 `平台:` 前綴)的第二份寫法,字元集、全形冒號、空白的容忍度都不同,而且 `bare()` 拿的名稱本來就是 `_test_names_of` 用 `_NS_TR_PREFIX_RE` 切過再接回 `pre + nm` 的產物。新版多了 `(?!:)` 排除 `::`,有理由,但沒在註解寫明為何不直接重用或參數化既有那支。⚠ 判不準是否算 major:結構上是第二份、行為上有刻意差異,先列 minor。
severity: minor
blocking: 否 + 判準:只是同概念多一份正則、兩份語意刻意不同,沒有造成判定結果互相打架的路徑;建議在註解寫明與 `_NS_TR_PREFIX_RE` 的差別(`::` 不當前綴),或日後改成共用一支。
引句:「_NODEHOME_TAG_PREFIX_RE = re.compile(r"^[A-Za-z0-9_-]+:(?!:)")」

總結:不對齊共 1 條,其中 major 0 條
