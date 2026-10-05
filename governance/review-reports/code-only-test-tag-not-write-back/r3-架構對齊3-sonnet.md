severity: minor

# 架構對齊審查 第 3 輪(code-only-test-tag-not-write-back)

## 問 1 分層與依賴方向
大致對齊。「每支檔有家」那層(_nodehome_*)向筆記內容閘那層(_ns_tr_*)借判定零件,接法跟既有呼叫端同一套:先 `_platform_test_index`,推送時先過 `_ns_tr_guard`,再 `_ns_tr_judge`。對照:doctor S20 與提交閘兩處都這樣組。掃描器共用(`_slot_scan` 供 `slot_parse` 與 `_slot_strip_keys`)也是抽共用零件,不是第二套。
引句:「return _ns_tr_judge(repo_root, tip, pidx)[0]」
file: `scripts/lumos:30066`、`scripts/lumos:30138`(既有兩處同樣的 pidx→guard→judge 組法)
一個小處:這是 `_nodehome_*` 區第一次直接呼叫 `_ns_*` 函式(同一檔、執行期解析,不壞),但把測試名判定零件的組裝步驟第三次複製了一份,而不是抽成共用小函式。結構上不算第二種做法,不列為不對齊。

## 問 2 命名與錯誤處理
命名對齊(`_nodehome_tag_judge`、`_nodehome_tag_only_change` 沿用 `_nodehome_` 前綴;`tag_names` 欄位跟 `sig_t` 並列,沒問題;`_slot_strip_keys` 回 (行, 清單) 是新函式,沒有舊呼叫端要改)。

不對齊兩條:

1. 例外處理靜默。鄰居 `_ns_tr_check`(30055 起)對同一組零件的 `except Exception as e` 是「印一句提醒、不影響其他檢查」;新函式 `except Exception: return None` 完全不出聲,使用者看不到為何沒豁免(只會看到被擋)。專案內 `except Exception: pass/回預設` 的先例也有(`_nodehome_parse_note` 的決策解析),但那是解析退路,不是外部判定零件失敗;跟同零件的鄰居比,少一句 stderr。
引句:「        return _ns_tr_judge(repo_root, tip, pidx)[0]
    except Exception:
        return None」
file: `scripts/lumos:30076`(`say(f"提醒:筆記測試綁定這次沒查({e.__class__.__name__}),不影響其他檢查")`)
severity: minor
blocking: 否 + 判準:錯誤處理風格不一致,結構正確,fail-open 方向與鄰居相同。

2. 模組常數位置。`_SLOT_*` 常數族全部擺在使用它們的函式之前(4125–4142 一整排),新增的 `_SLOT_STRIP_WS` 擺在 `_slot_strip_keys` 之後、`_slot_value_end` 之前,是這一族裡唯一在使用處之後定義的。執行期不出錯(呼叫時才解析),但跟同族慣例的位置不一樣。
引句:「_SLOT_STRIP_WS = " \t　"」
file: `scripts/lumos:4125`(常數族集中在函式前)
severity: minor
blocking: 否 + 判準:純放置位置不一致,不改行為,不是第二種做法。

## 問 3 第二種做法
未發現第二種做法。惰性物件:`cmd_home_check` 的 `_tj = []` 加內層函式,跟既有 closure 內快取同形(`_cat_cache = {}` 加 `_cats`、`_name_cache` 加 `by_name`、`pidx = None` 加 `nonlocal`),且以「用到才建」為註解的宗旨跟 `_NotelinesNet` 一致;`_NotelinesNet` 是類別,因為要帶旗標與多個參數,這裡單一值用 closure 符合鄰居。用 list 而非 nonlocal 是同檔兩種都有(`nonlocal pidx` 在 44600 附近),屬同族寫法,不列。
引句:「        if not _tj:
            _tj.append(_nodehome_tag_judge(root, None if staged else tip_where))」
file: `scripts/lumos:11395`、`scripts/lumos:29480`(既有惰性 closure 快取)

總結:不對齊共 2 條,其中 major 0 條
