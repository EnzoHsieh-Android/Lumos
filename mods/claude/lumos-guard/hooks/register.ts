import type { Register } from 'claude-code'
import type { GuardSeat } from '../types'

// lumos-guard:審查席的工具規則(Projects/審查席唯讀隔離_計劃)。
// 派工詞第一個非空行是 LUMOS-SEAT: <迴圈>/<輪次>/<席名> 的子代理(與它再派的子代理)套白名單;其他人照常。
// 防的是被文件裡的指令誘導,不防有心繞:Bash 仍是完整的 shell。外掛不改輸入與結果、不跑任何外部指令。
// 核心邏輯在 createGuard,查路徑、時間、提示由外面注入,測試可以換成假的(guard.test.ts)。

export type Seat = GuardSeat
export type Marker = { kind: 'none' } | { kind: 'seat'; loop: string; round: string; name: string } | { kind: 'bad'; why: string }
export type Io = {
  // 真實路徑(跟過所有連結、折疊 . 與 ..);不存在丟錯;存在但拿不到(懸空連結)回 undefined
  real: (path: string) => Promise<string | undefined>
  now: () => number
  sleep: (ms: number) => Promise<void>
  toast: (text: string) => void
  // 對照表存在 $.state:外掛熱重載後模組變數歸零,讀回來繼續擋
  loadSeats: () => Promise<Record<string, Seat>>
  // 存回時帶讀到的版本:別人(熱重載前後的另一份實例)先寫了就回 false,重讀重合併再試(代碼審 r3)
  loadVersioned: () => Promise<{ seats: Record<string, Seat>; version: number | undefined }>
  saveSeats: (seats: Record<string, Seat>, ifVersion?: number) => Promise<boolean>
}

export const WAIT_MS = 5000 // 子代理登記完成前就呼叫工具時,最多等這麼久
export const SAVE_MS = 2000 // 派工最多等存回這麼久,存回卡住不拖住派工(代碼審 r3)
export const SAVE_TRIES = 3 // 存回撞版最多重試幾次
export const BASH_MAX = 1_000_000 // 指令超過這麼長一律擋
export const PATH_MAX = 4096 // 路徑超過這麼長或這麼多段,當看不懂(擋)
export const SEGS_MAX = 256

const TOOLS_OK = new Set(['Read', 'Grep', 'Glob', 'Bash', 'WebFetch', 'WebSearch', 'ToolSearch', 'TodoWrite', 'TaskOutput',
                          'TaskStop', 'Agent', 'Task', 'Write', 'Edit', 'NotebookEdit'])
const AGENT_TYPES_OK = new Set(['general-purpose', 'Explore', 'Plan'])
const WRITE_TOOLS = new Set(['Write', 'Edit', 'NotebookEdit'])
const BASH_WORDS = new Set(['gh', 'hub', 'glab', 'claude'])
const GIT_PUSH_WORDS = new Set(['push', 'send-pack', 'send-email'])
const BASH_STRINGS = ['api.github.com', 'uploads.github.com', 'lumos-seat-staging']
// 暫存根(真實路徑,一律小寫比):macOS 的 /tmp、/var/tmp 是連結,真實路徑在 /private 底下
const ROOTS = ['/private/tmp', '/private/var/tmp', '/tmp', '/var/tmp']
const FOLDERS_ROOT = /^\/private\/var\/folders\/[^/]+\/[^/]+\/t(?=\/|$)/

const SEAT_RE = /^LUMOS-SEAT:\s*(\S+)$/
// 寫壞的判準:去掉開頭所有非字母數字的字元(markdown 修飾、清單符號、引號、零寬空白)與「1.」這類編號後,
// 以 lumos-seat(或 lumos-seats)開頭、後面不接字母數字或連字號 → 想寫標記;不合格就擋下派工(代碼審 r1、r2)。
// 只是提到 lumos-seat-work、Lumos-seating 這類字的一般派工不算
// 連字號寫成全形、底線、空白或其他橫線也算想寫標記(代碼審 r3);比對前先 NFKC、剝零寬字元
// 連字號(含別的橫線)寫法不管有沒有冒號都算;底線、空白或沒有分隔的寫法要接冒號才算——
// 「Lumos seat 的修正」這種一般句子不算(代碼審 r4:放寬後誤擋一般派工)
const SEAT_LOOSE_RE = /^lumos[-\u2010-\u2015]seats?(?![a-z0-9_-])|^lumos[_\s]*seats?\s*[:\uff1a]/i
const FORMAT_CHARS = /\p{Cf}/gu // 所有格式字元(零寬、方向標記、軟連字號……),不另列清單(代碼審 r4)
const clean = (line: string) => line.normalize('NFKC').replace(FORMAT_CHARS, '').trim()
function looseHead(line: string): string {
  return line.replace(/^[^\p{L}\p{N}]+/u, '').replace(/^\d+[.)]\s*/, '').replace(/^[^\p{L}\p{N}]+/u, '')
}

// 第一個非空行:跳過去空白後為空的行;JS 的 \s 本來就含 \r、BOM(U+FEFF)與全形空白(U+3000)
function firstLine(prompt: string): string {
  for (const raw of prompt.split(/\n|\u2028|\u2029/)) {
    if (clean(raw)) return raw.trim() // 回原文:合格標記要逐字比,標準化只用來認「想寫標記」
  }
  return ''
}

// 標記的一段(迴圈、輪次、席名):不能空、不能是 . 或 ..、不含斜線、反斜線、空白與控制字元;
// 從 $.state 讀回的席位也用這一條驗(代碼審 r3:讀回路徑原本只驗型別)
function segOk(p: unknown): boolean {
  return typeof p === 'string' && p !== '' && p !== '.' && p !== '..' && !/[\/\\\s\u0000-\u001f\u007f\p{Cf}]/u.test(p)
}

export function parseMarker(prompt: unknown): Marker {
  const line = firstLine(typeof prompt === 'string' ? prompt : '')
  if (!SEAT_LOOSE_RE.test(looseHead(clean(line)))) return { kind: 'none' }
  const m = SEAT_RE.exec(line)
  if (!m) return { kind: 'bad', why: '要寫成 LUMOS-SEAT: <迴圈>/<輪次>/<席名>(半形冒號、大寫)' }
  const parts = m[1].split('/')
  if (parts.length !== 3) return { kind: 'bad', why: `值要剛好三段,現在是 ${parts.length} 段` }
  for (const p of parts) {
    if (!segOk(p)) return { kind: 'bad', why: `「${p}」不能當一段(空的、.、..、含反斜線或控制字元)` }
  }
  return { kind: 'seat', loop: parts[0], round: parts[1], name: parts[2] }
}

const fold = (p: string) => p.normalize('NFC').toLowerCase()

function rootOf(p: string): string | null {
  const f = FOLDERS_ROOT.exec(p)
  if (f) return f[0]
  return ROOTS.find(r => p === r || p.startsWith(r + '/')) ?? null
}

const inside = (p: string, dir: string) => p === dir || p.startsWith(dir + '/')

// 在不在席報告暫存處裡(任一暫存根底下的 lumos-seat-staging)
function inStaging(p: string): boolean {
  const r = rootOf(p)
  return r !== null && inside(p, `${r}/lumos-seat-staging`)
}

// 範圍是不是暫存處的祖先(含 /、/private、暫存根本身、/private/var/folders 底下到 T 為止)
function aboveStaging(p: string): boolean {
  if (p === '/') return true
  if (ROOTS.some(r => r === p || r.startsWith(p + '/'))) return true
  return /^\/private\/var\/folders(\/[^/]+){0,2}(\/t)?$/.test(p) || p === '/private/var'
}

// 絕對路徑的真實路徑(小寫、NFC):取最深一層已存在的上層,再接上剩下的段;任何一段是空的、.、.. 回 null
export async function realOf(io: Io, path: unknown): Promise<string | null> {
  if (typeof path !== 'string' || !path.startsWith('/') || path.length > PATH_MAX) return null
  // macOS 的檔案編號寫法(/.vol/<卷>/<編號>):真實路徑保留原樣、比不出在哪,當看不懂(型別檔 FsStat.realPath;代碼審 r3)
  if (/^\/\.vol(\/|$)/i.test(path)) return null
  const parts = path.split('/').slice(1)
  if (parts.length && parts[parts.length - 1] === '') parts.pop() // 結尾的斜線(先拿掉再數段數;代碼審 r3)
  if (parts.length > SEGS_MAX) return null
  if (parts.some(s => s === '' || s === '.' || s === '..')) return null
  for (let n = parts.length; n >= 0; n--) {
    let got: string | undefined
    try {
      got = await io.real('/' + parts.slice(0, n).join('/'))
    } catch {
      continue // 這一層不存在,往上找
    }
    if (got === undefined) return null // 懸空連結或拿不到:擋
    const rest = parts.slice(n)
    return dataVol(fold([got.replace(/\/$/, ''), ...rest].join('/') || '/'))
  }
  return null
}

// macOS 的資料卷在 /System/Volumes/Data 底下也看得到同一批檔,真實路徑不折疊它;剝掉這個前綴再比(代碼審 r3)
const DATA_VOL = '/system/volumes/data'
function dataVol(p: string): string {
  return p === DATA_VOL ? '/' : p.startsWith(DATA_VOL + '/') ? p.slice(DATA_VOL.length) : p
}

function workDir(seat: Seat, root: string): string {
  return fold(`${root}/lumos-seat-work/${seat.loop}/${seat.name}`)
}

export const BASH_ERROR = '擋下(lumos-guard Bash):判斷出錯。\n為什麼在意:判斷不了的指令寧可擋。\n換個寫法再試。'

const why = (head: string, what: string, how: string) =>
  `擋下(lumos-guard ${head}):${what}\n為什麼在意:被審材料裡的指令不能讓審查員改到 repo、你的設定,或看到別席的報告。\n${how}`

const WORK_HINT = (seat: Seat) => `要做實驗請寫到:\n  /tmp/lumos-seat-work/${seat.loop}/${seat.name}/`

// 粗擋:一律轉小寫;以空白、引號與 shell 符號切詞(不切斜線,路徑裡只是出現 claude 不算)。
// gh、hub、glab、claude 看整詞,或明確的執行路徑(/、./、../、~/ 開頭)最後一段;push 這類只看整詞
export function bashBlock(cmd: unknown): string | null {
  if (typeof cmd !== 'string') return '指令不是字串'
  if (cmd.length > BASH_MAX) return '指令超過 1MB'
  const low = cmd.toLowerCase()
  const toks = low.split(/[\s'"`;|&(){}<>$\\]+/).filter(Boolean)
  // 每個詞都取最後一段斜線之後的部分比:帶路徑的寫法(絕對、相對、$HOME/…)一律算數(代碼審 r2)
  const words = new Set(toks.map(t => t.slice(t.lastIndexOf('/') + 1)).filter(Boolean))
  for (const w of BASH_WORDS) if (words.has(w)) return `指令裡有「${w}」`
  if (words.has('git')) for (const w of GIT_PUSH_WORDS) if (words.has(w)) return `指令裡同時有「git」與「${w}」`
  for (const s of BASH_STRINGS) if (low.includes(s)) return `指令裡有「${s}」`
  return null
}

// 搜尋範圍:Grep 只看 path;Glob 再接上 pattern 第一個萬用字元之前的固定段
function searchBase(e: any, seat: Seat): string | null {
  const p = e?.path
  let base: string
  if (p === undefined || p === null || p === '') base = seat.cwd
  else if (typeof p !== 'string') return null
  else if (p.startsWith('/')) base = p
  else {
    if (p.split('/').some((s: string) => s === '..')) return null
    base = `${seat.cwd}/${p}`
  }
  if (e?.tool === 'Glob' && typeof e?.pattern === 'string') {
    const pat: string = e.pattern
    // 大括號選項裡放絕對路徑或 ..:搜尋範圍算不準,當看不懂(代碼審 r3);一般的 *.{ts,js} 照常
    // 任何一段是 ..(萬用字元前後都算)、大括號巢狀,搜尋範圍都算不準,當看不懂(代碼審 r4)
    if (pat.split(/[/,{}]/).includes('..') || /\{[^{}]*\{/.test(pat)) return null
    for (const g of pat.matchAll(/\{([^{}]*)\}/g)) if (g[1].split(',').some(a => a.startsWith('/'))) return null
    const segs: string[] = []
    for (const s of (pat.startsWith('/') ? pat.slice(1) : pat).split('/')) {
      if (/[*?[{]/.test(s)) break
      segs.push(s)
    }
    if (segs.some(s => s === '..')) return null
    const fixed = segs.filter(s => s && s !== '.').join('/')
    if (pat.startsWith('/')) base = '/' + fixed
    else if (fixed) base = `${base}/${fixed}`
  }
  return base.replace(/\/{2,}/g, '/').replace(/(.)\/$/, '$1').split('/').filter(s => s !== '.').join('/') || '/'
}

// 一次工具呼叫該不該擋;回擋下理由或 null
export async function checkTool(io: Io, seat: Seat, e: any): Promise<string | null> {
  const tool = String(e?.tool ?? '')
  if (!TOOLS_OK.has(tool)) {
    return why('工具', `審查席不能用「${tool}」。`, '只准讀取、搜尋、Bash、網路查詢、派一般子代理,以及寫自己的工作資料夾。')
  }
  if (tool === 'Agent' || tool === 'Task') {
    if (e?.isolation !== undefined && e?.isolation !== null) {
      return why('工具', `審查席派子代理不能帶 isolation(${String(e.isolation)})。`, '拿掉 isolation 再派:remote 在雲端跑、這裡管不到,worktree 會在真 repo 開分支。')
    }
    const t = e?.subagent_type
    if (t !== undefined && t !== null && !AGENT_TYPES_OK.has(String(t))) {
      return why('工具', `審查席不能派「${String(t)}」型的子代理。`, '只准不指定,或 general-purpose、Explore、Plan。')
    }
    return null
  }
  if (tool === 'Write' || tool === 'Edit' || tool === 'NotebookEdit') {
    const raw = tool === 'NotebookEdit' ? e?.notebook_path : e?.file_path
    const real = await realOf(io, raw)
    const ok = real !== null && rootOf(real) !== null && inside(real, workDir(seat, rootOf(real)!))
    return ok ? null : why('寫檔', `審查席只能寫自己的工作資料夾(${String(raw)} 不在裡面)。`, WORK_HINT(seat))
  }
  if (tool === 'Read') {
    const real = await realOf(io, e?.file_path)
    if (real === null) return why('暫存處', `讀檔路徑看不懂(${String(e?.file_path).slice(0, 200)}:相對路徑、含 . 或 .. 段、空段或過長)。`, '改用乾淨的絕對路徑。')
    return inStaging(real)
      ? why('暫存處', '審查席不能讀席報告暫存處裡的檔。', '別席的報告要等全部交回才看得到;你的發現直接寫在回答裡。')
      : null
  }
  if (tool === 'Grep' || tool === 'Glob') {
    const base = searchBase(e, seat)
    const real = base === null ? null : await realOf(io, base)
    if (real === null) return why('暫存處', '搜尋範圍看不懂(含 .. 或不是字串)。', '改用絕對路徑指定 path。')
    return inStaging(real) || aboveStaging(real)
      ? why('暫存處', `搜尋範圍(${real})包含席報告暫存處。`, '把 path 指到要搜的 repo 或資料夾,不要指到暫存根或它的上層。')
      : null
  }
  if (tool === 'Bash') {
    const hit = bashBlock(e?.command)
    return hit === null ? null
      : why('Bash', `${hit}:審查席的 Bash 不能做對外動作(開 PR、推分支、另開 claude)或碰席報告暫存處。這幾個詞是整詞比對,只是路徑最後一段或要搜的字也算。`,
            '檔案內容用 Read 工具讀;搜字可用 Grep 工具(有的話);目錄名剛好是這個詞就在結尾加斜線;git 與 push 要分成兩次 Bash 呼叫(同一行用分號分開也不行);報告內容直接寫在回答裡。')
  }
  return null
}

type Pend = { n: number; waiters: (() => void)[] }

export function createGuard(io: Io) {
  const seats = new Map<string, Seat>() // 子代理編號 → 席位
  const bySession = new Map<string, Set<string>>()
  const pending = new Map<string, Pend>() // 會談 → 啟動中的審查席派工

  function wake(p: Pend) {
    const ws = p.waiters
    p.waiters = []
    for (const w of ws) w()
  }

  // 用派工開始時拿到的那一份計數扣:會談結束後同編號的新派工有自己的一份,舊派工回來不扣到它(代碼審 r4)
  function release(session: string, p: Pend) {
    p.n -= 1
    if (p.n <= 0 && pending.get(session) === p) pending.delete(session)
    wake(p) // 每登記一席就叫醒等待者各自重查,不必等整批
  }

  // 會談結束過幾次:派工開始時記下,回來時變了就是「結束前開始、結束後才登記完」,不登記;
  // 結束後同一個編號再派的席照常登記(代碼審 r3:原本只增不減的集合讓之後的席全部不登記)
  const endGen = new Map<string, number>()
  const sessionOf = new Map<string, string>() // 子代理編號 → 所屬會談

  // 存回 $.state:先讀既有的再合併(熱重載後記憶體只有部分席,整份覆寫會抹掉別席;代碼審 r2),
  // 拿掉 drop 指定的會談;一次只跑一個,避免兩次存回交錯、後寫蓋掉先寫
  let saving: Promise<void> = Promise.resolve()
  // 每一格最多等 SAVE_MS:一次存回卡住不拖住後面每一次(代碼審 r4:原本只有派工那頭設上限,會談結束與之後的存回整條卡死)
  function save(drop?: string): Promise<void> {
    let abandoned = false // 這一格逾時被放掉後,還在背景跑的那次不再寫(代碼審 r5)
    const job = async () => {
      try {
        for (let i = 0; i < SAVE_TRIES && !abandoned; i++) {
          const { seats: saved, version } = await io.loadVersioned()
          const merged: Record<string, Seat & { session?: string }> = {}
          for (const [id, s] of Object.entries(saved ?? {})) if (validSeat(s)) merged[id] = s as any
          for (const [id, s] of seats) merged[id] = { ...s, session: sessionOf.get(id) ?? (s as any).session }
          if (drop !== undefined) for (const id of Object.keys(merged)) if ((merged[id] as any).session === drop) delete merged[id]
          if (abandoned) return
          if (await io.saveSeats(merged, version ?? 0)) return
        }
        if (abandoned) return
        io.toast(`lumos-guard 存回撞版 ${SAVE_TRIES} 次放棄:這場的席只在記憶體裡,外掛重載後不受保護`)
      } catch { /* 存不進去:這場仍在記憶體裡擋 */ }
    }
    saving = saving.then(() => Promise.race([job(), io.sleep(SAVE_MS).then(() => { abandoned = true })]))
    return saving
  }

  // 記憶體查不到時讀 $.state(熱重載後模組變數歸零);讀壞了回 'error'
  async function lookup(id: string): Promise<Seat | undefined | 'error'> {
    const s = seats.get(id)
    if (s) return s
    let saved: unknown
    try {
      saved = (await io.loadSeats())?.[id]
    } catch {
      return 'error'
    }
    if (!validSeat(saved)) return undefined
    seats.set(id, saved)
    if (typeof (saved as any).session === 'string') sessionOf.set(id, (saved as any).session)
    return saved
  }

  return {
    // agent.spawn:回 { deny } 或 next 的結果
    async spawn(session: string, sessionCwd: string, e: any, next: (e: any) => Promise<any>): Promise<any> {
      const found = typeof e?.parentAgentId === 'string' ? await lookup(e.parentAgentId) : undefined
      // 讀不到對照表、又是子代理派的:判不出發起方是不是審查席,寧可擋(跟工具呼叫那頭同方向;代碼審 r3)
      if (found === 'error') return { deny: why('派工', '判斷不了發起方是不是審查席(對照表讀不到)。', '稍後再派一次。') }
      const parent = found
      const cwdOf = (fallback: string) => (typeof e?.cwd === 'string' && e.cwd !== '' ? e.cwd : fallback)
      let seat: Seat | null = null
      if (parent) seat = { ...parent, cwd: cwdOf(parent.cwd) }
      else {
        const m = parseMarker(e?.prompt)
        if (m.kind === 'bad') {
          return { deny: why('派工', `派工詞第一行像審查席標記但寫壞了:${m.why}。`, '是審查席就修好第一行再派;不是審查席,第一行別用 lumos-seat 這個詞開頭(改寫第一行,不用刪內文)。') }
        }
        if (m.kind === 'seat') {
          seat = { loop: m.loop, round: m.round, name: m.name, cwd: cwdOf(sessionCwd) }
        }
      }
      if (!seat) return next(e)
      const gen = endGen.get(session) ?? 0
      const p = pending.get(session) ?? { n: 0, waiters: [] }
      p.n += 1
      pending.set(session, p)
      try {
        const r = await next(e)
        if (r && typeof r.agentId === 'string' && (endGen.get(session) ?? 0) === gen) {
          seats.set(r.agentId, seat)
          sessionOf.set(r.agentId, session)
          if (!bySession.has(session)) bySession.set(session, new Set())
          bySession.get(session)!.add(r.agentId)
          await Promise.race([save(), io.sleep(SAVE_MS)]) // 派工自己也設上限:前面排了好幾格時不累加(代碼審 r5)
        }
        return r
      } finally {
        release(session, p)
      }
    },
    // tool.call:回擋下理由或 null(放行)
    async call(session: string, e: any): Promise<string | null> {
      const id = e?.agentId
      if (typeof id !== 'string') return null // 主會談
      const found = await lookup(id)
      // 判不出是不是審查席:Bash 與寫檔工具寧可擋,讀取放行(代碼審 r3 把寫檔也收進來)
      if (found === 'error') return WRITE_TOOLS.has(String(e?.tool)) ? why('寫檔', '判斷不了是不是審查席(對照表讀不到)。', '稍後再試。') : e?.tool === 'Bash' ? BASH_ERROR : null
      let seat = found
      if (!seat && pending.has(session)) {
        let timedOut = false
        const timer = io.sleep(WAIT_MS).then(() => { timedOut = true })
        while (!seat && !timedOut && pending.has(session)) {
          const p = pending.get(session)!
          await Promise.race([new Promise<void>(res => p.waiters.push(res)), timer])
          seat = seats.get(id)
        }
        if (!seat && timedOut) io.toast(`lumos-guard 逾時放行:子代理 ${id} 等了 ${WAIT_MS / 1000} 秒還沒登記完`)
      }
      if (!seat) return null
      try {
        return await checkTool(io, seat, e)
      } catch (err) {
        if (e?.tool === 'Bash') return why('Bash', `判斷出錯(${String((err as Error)?.message ?? err).slice(0, 100)})。`, '換個寫法再試。')
        return null // 外掛自己出錯:放行
      }
    },
    // keep:/clear 或 resume 時行程換個會談編號繼續跑,背景的審查席可能還活著,席位不刪(代碼審 r3、r4)
    // keep 時會談其實沒死:不算結束、不清啟動中清單,派工途中的席回來照常登記(代碼審 r4)
    end(session: string, keep = false): Promise<void> {
      if (keep) return Promise.resolve()
      endGen.set(session, (endGen.get(session) ?? 0) + 1)
      const p = pending.get(session)
      pending.delete(session)
      if (p) wake(p)
      for (const id of bySession.get(session) ?? []) seats.delete(id)
      for (const [id, s] of sessionOf) if (s === session) { seats.delete(id); sessionOf.delete(id) }
      bySession.delete(session)
      return save(session)
    },
    // 出錯時要不要當審查席處理:判不出來(熱重載後記憶體不全、$.state 可能讀不到)寧可當是——
    // 有子代理編號就算;主會談沒有編號,不算(代碼審 r2)
    seatish(id: unknown): boolean {
      return typeof id === 'string'
    },
    _state: { seat: (id: string) => seats.get(id), pending: (session: string) => pending.get(session)?.n ?? 0 },
  }
}

// 讀回 $.state 的值要先驗形狀(別的外掛可以掛 state 事件改寫它;代碼審 r2)
function validSeat(s: unknown): s is Seat {
  const o = s as any
  return !!o && typeof o === 'object' && ['loop', 'round', 'name'].every(k => segOk(o[k])) && typeof o.cwd === 'string'
}

export function makeIo($: any): Io {
  return {
    // 型別檔 FsStat:懸空連結照樣回結果、只是沒有 realPath(回 undefined → 擋);不存在才丟錯(代碼審 r3 核對)
    real: async path => (await $.fs.stat(path, { resolve: true })).realPath,
    now: () => Date.now(),
    sleep: ms => $.clock.sleep(ms),
    toast: text => {
      try { $.ui.toast(text) } catch { /* 沒有介面 */ }
    },
    loadSeats: async () => (await $.state.get({ plugin: 'lumos-guard', key: 'seats' })).value ?? {},
    loadVersioned: async () => {
      const held = await $.state.get({ plugin: 'lumos-guard', key: 'seats' })
      return { seats: held.value ?? {}, version: typeof held.version === 'number' ? held.version : undefined }
    },
    saveSeats: async (seats, ifVersion) => {
      const r = await $.state.set({ plugin: 'lumos-guard', key: 'seats' }, seats, ifVersion === undefined ? undefined : { ifVersion })
      return r?.isSet !== false
    },
  }
}

export type State = { guard: ReturnType<typeof createGuard> | null }

export async function onSpawn(st: State, $: any, e: any, next: (e: any) => Promise<any>) {
  let session = ''
  let cwd = ''
  try {
    if (!st.guard) st.guard = createGuard(makeIo($))
    session = await $.session.id()
    cwd = await $.session.cwd()
  } catch {
    return next(e) // 外掛自己出錯:放行
  }
  return st.guard.spawn(session, cwd, e, next)
}

// 出錯時:審查席(或判不出是不是)的 Bash 擋,其他放行;主會談一律放行
export function seatishOf(st: State, e: any): boolean {
  if (typeof e?.agentId !== 'string') return false
  return st.guard === null || st.guard.seatish(e.agentId)
}

export async function onCall(st: State, $: any, e: any): Promise<string | null> {
  try {
    if (!st.guard) st.guard = createGuard(makeIo($))
    return await st.guard.call(await $.session.id(), e)
  } catch {
    return e?.tool === 'Bash' && seatishOf(st, e) ? BASH_ERROR : null
  }
}

// tool.call 的接線:有擋下理由就回 { deny },沒有才交下去(代碼審 r3:接線抽成函式才測得到)
export async function onTool(st: State, $: any, e: any, next: (e: any) => any): Promise<any> {
  const deny = await onCall(st, $, e)
  return deny === null ? next(e) : { deny }
}

// 會談結束:等存回 $.state 做完才回,免得引擎接著關掉時那一場的席還留在存檔裡
export async function onEnd(st: State, e: any) {
  try {
    await st.guard?.end(e.sessionId, e?.reason === 'clear' || e?.reason === 'resume')
  } catch { /* 同上 */ }
}

// tool.call 掛鉤自己出錯時怎麼辦(S8)。.catch 裡的 next 不會重跑:工具已經跑過(called)就交回原本的結果,
// 不謊稱擋下;還沒跑時審查席的 Bash 擋、其他交下去(型別檔 Caught)
export function onCallFailed(e: any, next: any, seatish: boolean): any {
  if (next?.called === true) return next(e)
  return e?.tool === 'Bash' && seatish ? { deny: BASH_ERROR } : next(e)
}

export const register: Register = on => {
  const st: State = { guard: null }

  // 掛鉤自己丟錯時引擎會跳過它(等於放行);.catch 寫明出錯怎麼辦:派工放行,Bash 擋、其他工具放行(S8)
  on('agent.spawn', async ($, e, next) => onSpawn(st, $, e, next))
    .catch(($, e, next) => next(e))

  on('tool.call', async ($, e, next) => onTool(st, $, e, next))
    .catch(($, e, next) => onCallFailed(e, next, seatishOf(st, e)))

  on('session.end', async ($, e, next) => {
    await onEnd(st, e)
    return next(e)
  })
}
