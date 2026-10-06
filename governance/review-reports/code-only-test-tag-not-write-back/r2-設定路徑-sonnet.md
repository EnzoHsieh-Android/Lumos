severity: minor

# 第 2 輪審查:設定路徑鏡頭(設定讀錯版本、呼叫端漏接)

## 呼叫端清查(題 1)
- `_nodehome_evaluate` 只有一個呼叫端:`cmd_home_check`,該處有設 `cfg["tag_exempt"]`;`_nodehome_mark_note_content` 同處帶 `tag_exempt=cfg["tag_exempt"]`,預設參數是 False。
- 其餘 `_nodehome_config` 的呼叫端(S8–S10 健檢 home_audit 那支、`_cochange_excluded` 取 ignore、1607 行只取 mode)都不經過 `_nodehome_evaluate`,沒設 tag_exempt 時 `cfg.get("tag_exempt")` 為假,走原文 `sig`,行為照舊,也不該設——它們不判「內容有沒有變」。
- `_nodehome_parse_note` 一律同時算 sig 與 sig_t,健檢那條(43071 行)只取其他欄位,不受影響。無漏接。

## 題 4(讀哪一版設定)
- 提交前 `--staged`:`_nodehome_reader(root, "index")` 讀提交索引的設定;推送前讀終點提交那版。豁免與「筆記測試綁定要存在」都吃同一份 `cfg_text`,兩道看同一版。
- 推送範圍中途改設定:只看終點版,逐提交比對全用終點版決定 sig 或 sig_t。終點把 test_refs 調成 warn 時豁免關(保守側);終點才調成 block 時,那道整篇重判碰到的筆記,藏的句子仍會被抓。方向沒有洞。

## Finding 1
severity: minor
blocking: 否——只在使用者明確用 LUMOS_SKIP_NOTE_SHAPE=1 逃生時發生,逃生會留治理帳,CI 不吃這個變數仍會擋;不影響預設路徑。
引句:「    cfg["tag_exempt"] = _nodehome_tag_exempt(cfg_text)」
說明:豁免開關只讀設定、不看環境變數。`cmd_note_shape` 在 LUMOS_SKIP_NOTE_SHAPE=1 時整支提早 rc0(連 test_refs 一起不跑),但 `cmd_home_check` 沒有對應判斷,豁免照開,兩道一起被一個變數關掉。
重現(以 `_tr_repo` 造好 r2 測試 t_nodehome_tag_exempt_hidden_sentence_caught_by_test_refs 的 ① 場景,探針在臨時目錄跑,未改 repo):
```
home: 0
ns normal: 1
ns SKIP env: 0
```
(home=每支檔有家 rc,ns=筆記形狀擋含測試綁定那組;藏進 [test:] 的英文句子在 SKIP 時兩道都 rc0。)
file: `scripts/lumos:27802`、`scripts/lumos:30132`

## Finding 2
severity: minor
blocking: 否——只影響本機推送前那一關,CI 的工作目錄就是終點、不會降級,仍會擋;計劃筆記已寫明降級後交給 CI。
引句:「    return _ns_test_refs_mode(gate, cfg_text, False)[0] == "block"」
說明:豁免只問「設定上會不會擋」,沒問「這次實際擋不擋」。`_ns_test_refs_collected` 在推送時工作目錄對不上(HEAD 不是推送終點、config.json 有沒提交的改動、已追蹤測試檔有未提交修改)會把 block 降成 warn 且只提醒,例外時 fail-open 成 off;這些情況豁免仍開著,藏在 [test:] 的一句英文說明兩道都放過。
重現(同一個探針,切到別的分支後推送 base..tip 版本,終點不是 HEAD):
```
ns tip!=HEAD: 0  ...指不到真測試(dangling) a now retries three times then logs ...(只提醒)
home tip!=HEAD: 0
```
同族但未重現:test_profile 壞掉讓 `_ns_test_refs_collected` 走例外分支回 "off"、或判不了(平台索引建不起來)時同樣會兩道都放行;不另列等級,與本條同根因。
file: `scripts/lumos:30006`、`scripts/lumos:29954`

## 提交前補充(不另列)
`_nodehome_tag_exempt` 內固定傳 staged=False,所以提交前(筆記測試綁定只提醒)豁免也開;提交前藏句子兩道都過,由推送前那道補。這是設計取捨,與 Finding 2 同一個缺口的提交端版本。

總結:全份最高等級 minor
