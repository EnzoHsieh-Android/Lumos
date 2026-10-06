import type { Register } from 'claude-code'

// lumos-ledger:只觀察、不擋、不改、不注入(Projects/Lumos事件帳_計劃)。
// 每個會談的回合、工具呼叫、子代理寫成事件帳,放在主 checkout 的 governance/runtime/events/<會談編號>/。
// 核心邏輯在 createLedger,讀寫檔與跑指令由外面注入,測試可以換成假的(ledger.test.ts)。
// 會談編號、圖譜判定、主 checkout 判定三條規則跟 Python 讀取端各寫一份,兩邊都拿 rules-fixture.ts 的案例測。

export type RunResult = { exitCode: number; stdout: string; stderr: string }
export type Entry = { name: string; kind: string; isLink?: boolean }
export type StatResult = { kind: string; isLink: boolean } | null
export type Io = {
  // 逾時或起不來時丟錯誤(引擎的 $.process.run 就是這樣)
  run: (argv: readonly string[], cwd: string) => Promise<RunResult>
  list: (path: string) => Promise<readonly Entry[]>
  // 路徑通到哪種東西、它自己是不是連結;不存在回 null
  stat: (path: string) => Promise<StatResult>
  exists: (path: string) => Promise<boolean>
  write: (path: string, text: string) => Promise<void>
  now: () => number
  rand8: () => string
}

type Verdict =
  | { kind: 'write'; main: string; worktree: string | null; at: number }
  | { kind: 'skip'; at: number }
  | { kind: 'temp'; at: number }
type Item = { cwd: string; ev: Record<string, unknown> }
// 以會談編號為鍵;每筆事件帶自己收到時的 cwd,寫的時候照到達順序、把連續寫到同一處的合成一塊
type Buf = { items: Item[]; dropped: number; err: string | null; lost: number }

export const EVENTS_REL = 'governance/runtime/events'
export const FLUSH_AT = 50 // 緩衝滿 50 筆就寫一塊
export const BUF_MAX = 500 // 判定一直失敗時最多留 500 筆,多的丟最舊的
const FRESH_MS = 10 * 60 * 1000 // 「寫到某處」「這裡不記」10 分鐘後重判
const RETRY_MS = 5 * 60 * 1000 // 「暫時失敗」同一個 cwd 5 分鐘內不重試 git
const VERDICT_KEEP = 20 // 位置判定只留最近 20 個 cwd
const SESSION_RE = /^[A-Za-z0-9][A-Za-z0-9._-]*$/ // 讀取端 _EVENTS_SESSION_RE;兩邊用 rules-fixture.ts 對齊

export function sessionOk(session: string): boolean {
  return SESSION_RE.test(session)
}

// 主 checkout:git-common-dir 是 .git 資料夾就取上一層,否則就是 show-toplevel(讀取端 _events_root 同一條)
export function pickMain(top: string, common: string): string {
  return common.endsWith('/.git') ? common.slice(0, -'/.git'.length) : top
}

// 跟 lumos 的 _vault_in 同三種:docs/*-knowledge/、docs/knowledge/、頂層就是獨立 vault;資料夾是連結時跟著連結走
export async function vaultIn(io: Pick<Io, 'list' | 'stat'>, main: string): Promise<boolean> {
  const isDir = async (base: string, e: Entry) =>
    e.kind === 'dir' || (e.isLink === true && (await io.stat(`${base}/${e.name}`))?.kind === 'dir')
  try {
    for (const e of await io.list(`${main}/docs`)) {
      if ((e.name === 'knowledge' || e.name.endsWith('-knowledge')) && (await isDir(`${main}/docs`, e))) return true
    }
  } catch { /* 沒有 docs */ }
  try {
    const dirs = new Set<string>()
    for (const e of await io.list(main)) if (await isDir(main, e)) dirs.add(e.name)
    return dirs.has('MOC') && (dirs.has('Systems') || dirs.has('Verification'))
  } catch {
    return false
  }
}

// 一次工具呼叫要記的欄位;threw=next 丟錯(例如被中斷),照樣記一筆
export function toolExtra(e: any, r: any, threw: boolean): Record<string, unknown> {
  const paths = ['file_path', 'path', 'notebook_path'].map(k => e?.[k]).filter((x: unknown) => typeof x === 'string')
  const extra: Record<string, unknown> = {
    tool: e?.tool,
    ok: !threw && !(r?.isError === true) && typeof r?.deny !== 'string',
    denied: typeof r?.deny === 'string',
  }
  if (threw) extra.interrupted = true
  if (paths.length) extra.paths = paths
  if (e?.tool === 'Bash' && typeof e?.command === 'string') extra.cmd = e.command.slice(0, 500)
  return extra
}

export function createLedger(io: Io) {
  const bufs = new Map<string, Buf>()
  const verdicts = new Map<string, Verdict>()
  const floors = new Map<string, number>() // 會談資料夾 → 已知最大塊名毫秒(新載入的實例也排在舊塊之後)
  let lastMs = 0
  let queue: Promise<void> = Promise.resolve()

  function fresh(cwd: string): Verdict | undefined {
    const v = verdicts.get(cwd)
    if (!v) return undefined
    const age = io.now() - v.at
    return age < (v.kind === 'temp' ? RETRY_MS : FRESH_MS) ? v : undefined
  }

  function remember(cwd: string, v: Verdict): Verdict {
    verdicts.delete(cwd)
    verdicts.set(cwd, v)
    while (verdicts.size > VERDICT_KEEP) verdicts.delete(verdicts.keys().next().value as string)
    return v
  }

  async function resolve(cwd: string, cachedOnly: boolean): Promise<Verdict> {
    const known = fresh(cwd)
    if (known) return known
    if (cachedOnly) return { kind: 'temp', at: io.now() } // 會談結束時等不起 git
    let r: RunResult
    try {
      r = await io.run(['git', 'rev-parse', '--path-format=absolute', '--show-toplevel', '--git-common-dir'], cwd)
    } catch {
      return remember(cwd, { kind: 'temp', at: io.now() })
    }
    if (r.exitCode !== 0) {
      const not = /not a git repository/i.test(r.stderr)
      return remember(cwd, { kind: not ? 'skip' : 'temp', at: io.now() })
    }
    const [top, common] = r.stdout.trim().split('\n').map(s => s.trim())
    if (!top || !common || !top.startsWith('/') || !common.startsWith('/')) {
      return remember(cwd, { kind: 'temp', at: io.now() })
    }
    const main = pickMain(top, common)
    if (!(await vaultIn(io, main))) return remember(cwd, { kind: 'skip', at: io.now() })
    return remember(cwd, { kind: 'write', main, worktree: main === top ? null : top, at: io.now() })
  }

  // 事件帳路徑從主 checkout 往下每一層都不能是連結(讀取端 _events_path_safe 同一條;連結會把寫入導到 repo 外)。
  // 用列上一層看「它自己是不是連結」,不跟連結,懸空的連結也算;一路查到要寫的 .gitignore 與會談資料夾。
  async function pathSafe(main: string, session: string): Promise<boolean> {
    let parent = main
    for (const part of [...EVENTS_REL.split('/'), session]) {
      let kids: readonly Entry[]
      try {
        kids = await io.list(parent)
      } catch {
        return true // 這一層還不存在:底下也還沒有東西,寫的時候會新建成一般資料夾
      }
      if (kids.some(e => e.name === part && e.isLink)) return false
      if (part === 'events' && kids.length && (await io.list(`${parent}/${part}`).catch(() => [] as Entry[]))
        .some(e => e.name === '.gitignore' && e.isLink)) return false
      parent = `${parent}/${part}`
    }
    return true
  }

  async function loadFloor(dir: string): Promise<void> {
    if (floors.has(dir)) return
    let max = 0
    try {
      for (const e of await io.list(dir)) {
        const m = /^(\d{13})-/.exec(e.name)
        if (m) max = Math.max(max, Number(m[1]))
      }
    } catch { /* 還沒有這個資料夾 */ }
    floors.set(dir, max)
  }

  function chunkName(dir: string): string {
    // 同一個行程裡嚴格遞增(時鐘倒退、同一毫秒也一樣),也排在這個資料夾既有的塊之後;不同行程靠隨機字串避免撞名
    const ms = Math.max(io.now(), lastMs + 1, (floors.get(dir) ?? 0) + 1)
    lastMs = ms
    floors.set(dir, ms)
    return `${String(ms).padStart(13, '0')}-${io.rand8()}.jsonl`
  }

  async function writeSession(session: string, cachedOnly: boolean): Promise<void> {
    const b = bufs.get(session)
    if (!b || b.items.length === 0) return
    const n = b.items.length
    const vs = new Map<string, Verdict>()
    for (const it of b.items.slice(0, n)) if (!vs.has(it.cwd)) vs.set(it.cwd, await resolve(it.cwd, cachedOnly))
    for (const v of vs.values()) if (v.kind === 'write') await loadFloor(`${v.main}/${EVENTS_REL}/${session}`)
    // ★同一個同步步驟裡:取走能寫的那一段(到第一筆判不了的為止)、切成連續同一處的段、決定塊名★
    // 判定等待期間新進來、或被溢位擠到前面的事件沒有判定:當暫時判不了,留著下次再寫
    let end = b.items.findIndex((it, i) => i >= n || !vs.has(it.cwd) || vs.get(it.cwd)!.kind === 'temp')
    if (end < 0) end = b.items.length
    const taken = b.items.splice(0, end)
    const segs: { v: Extract<Verdict, { kind: 'write' }>; evs: Record<string, unknown>[]; name: string }[] = []
    for (const it of taken) {
      const v = vs.get(it.cwd)!
      if (v.kind !== 'write') continue // 這裡不記:丟
      const last = segs[segs.length - 1]
      const ev = { ...it.ev, worktree: v.worktree }
      if (last && last.v.main === v.main) last.evs.push(ev)
      else segs.push({ v, evs: [ev], name: '' })
    }
    for (const s of segs) s.name = chunkName(`${s.v.main}/${EVENTS_REL}/${session}`)
    for (const s of segs) {
      const dir = `${s.v.main}/${EVENTS_REL}`
      const ts = new Date(io.now()).toISOString()
      const head: Record<string, unknown>[] = []
      if (b.err) head.push(base(session, null, s.v.worktree, ts, 'ledger_error', { what: b.err, lost: b.lost }))
      if (b.dropped) head.push(base(session, null, s.v.worktree, ts, 'ledger_error',
                                    { what: '暫時判不了寫入位置,丟了最舊的幾筆', lost: b.dropped }))
      const [err, lost, dropped] = [b.err, b.lost, b.dropped]
      b.err = null
      b.lost = 0
      b.dropped = 0
      try {
        if (!(await pathSafe(s.v.main, session))) { // 上層是連結:不寫(讀取端也不會讀),之前的錯誤留著
          b.err = err ?? '事件帳路徑有符號連結,沒寫'
          b.lost = lost + s.evs.length
          b.dropped = dropped
          continue
        }
        if (!(await io.exists(`${dir}/.gitignore`))) await io.write(`${dir}/.gitignore`, '*\n')
        await io.write(`${dir}/${session}/${s.name}`, [...head, ...s.evs].map(l => JSON.stringify(l)).join('\n') + '\n')
      } catch (e) {
        // 不重試這一塊;下一塊開頭補一筆 ledger_error,帶第一個原因與累計丟了幾筆
        b.err = err ?? String((e as Error)?.message ?? e).slice(0, 200)
        b.lost = lost + s.evs.length
        b.dropped = dropped
      }
    }
  }

  function enqueue(session: string, cachedOnly = false): Promise<void> {
    queue = queue.then(() => writeSession(session, cachedOnly)).catch(() => {})
    return queue
  }

  return {
    // 收到的當下就用收到時的會談編號與 cwd 進緩衝;不回傳佇列,收事件的 hook 不必等寫檔
    add(session: string, cwd: string, ev: Record<string, unknown>): void {
      if (!sessionOk(session)) return
      if (fresh(cwd)?.kind === 'skip') return // 這裡不記:直接丟,不累積
      let b = bufs.get(session)
      if (!b) bufs.set(session, (b = { items: [], dropped: 0, err: null, lost: 0 }))
      b.items.push({ cwd, ev })
      if (b.items.length > BUF_MAX) {
        b.items.shift()
        b.dropped += 1
      }
      if (b.items.length >= FLUSH_AT) void enqueue(session)
    },
    flushSession(session: string): Promise<void> {
      return enqueue(session)
    },
    // session.end:判定沒有快取時不跑 git(等不起),那幾筆直接放棄
    flushSessionCachedOnly(session: string): Promise<void> {
      return enqueue(session, true)
    },
    drop(session: string): void {
      bufs.delete(session)
      for (const k of [...floors.keys()]) if (k.endsWith(`/${session}`)) floors.delete(k)
    },
    _state: {
      pending: (session: string) => bufs.get(session)?.items.length ?? 0,
      dropped: (session: string) => bufs.get(session)?.dropped ?? 0,
      lost: (session: string) => bufs.get(session)?.lost ?? 0,
    },
  }
}

export function base(session: string, agent: string | null, worktree: string | null, ts: string, ev: string,
                     extra: Record<string, unknown>): Record<string, unknown> {
  return { v: 1, ts, session, agent, worktree, ev, ...extra }
}

const hex8 = () => Array.from({ length: 8 }, () => Math.floor(Math.random() * 16).toString(16)).join('')

// 每次載入(含熱重載)一份;模組變數在重載時歸零,塊名靠讀既有塊與隨機字串避免排錯、撞名
type State = { ledger: ReturnType<typeof createLedger> | null; turnNo: Map<string, number>; origin: Map<string, string> }

function makeIo($: any): Io {
  return {
    run: async (argv, cwd) => {
      const r = await $.process.run(argv, { cwd, timeoutMs: 3000, env: { LC_ALL: 'C' } })
      return { exitCode: r.exitCode, stdout: r.stdout, stderr: r.stderr }
    },
    list: path => $.fs.list(path),
    stat: async path => {
      try {
        const s = await $.fs.stat(path)
        return { kind: s.kind, isLink: s.isLink === true }
      } catch {
        return null
      }
    },
    exists: path => $.fs.exists(path),
    write: (path, text) => $.fs.write(path, text),
    now: () => Date.now(),
    rand8: hex8,
  }
}

// 收事件:取收到當下的會談編號與 cwd;任何錯都吞掉,不影響本業
async function record(st: State, $: any, agent: string | null | undefined, ev: string, extra: Record<string, unknown>) {
  try {
    if (!st.ledger) st.ledger = createLedger(makeIo($))
    const session: string = await $.session.id()
    const cwd: string = await $.session.cwd()
    st.ledger.add(session, cwd, base(session, agent ?? null, null, new Date().toISOString(), ev, extra))
  } catch { /* 觀察壞掉不能影響本業 */ }
}

async function onPrompt(st: State, $: any, e: any) {
  try {
    if (!e.agentId) st.origin.set(await $.session.id(), String(e.origin?.kind ?? ''))
  } catch { /* 同上 */ }
}

async function onTurnStart(st: State, $: any, e: any) {
  try {
    const s: string = await $.session.id()
    const n = (st.turnNo.get(s) ?? 0) + 1
    st.turnNo.set(s, n)
    await record(st, $, null, 'turn_start', { turn: n, origin: st.origin.get(s) ?? null, prompt_len: String(e.text ?? '').length })
  } catch { /* 同上 */ }
}

// 主會談的回合用數字 turn(這個行程裡數的,重載或 resume 後從 1 重算);子代理沒有 turn.start,用引擎給的 turn_id
async function onTurnEnd(st: State, $: any, e: any) {
  try {
    const s: string = await $.session.id()
    const which = e.agentId ? { turn_id: e.turnId } : { turn: st.turnNo.get(s) ?? null }
    await record(st, $, e.agentId, 'turn_end', { ...which, reason: e.reason })
    if (st.ledger) void st.ledger.flushSession(s) // 不等寫檔
  } catch { /* 同上 */ }
}

async function onSpawn(st: State, $: any, e: any, r: any) {
  await record(st, $, e.agentId, 'spawn', {
    agent_type: e.subagentType ?? null,
    model: r?.model ?? null,
    child: r?.agentId ?? null,
    denied: typeof r?.deny === 'string',
  })
}

// 會談結束:整條鏈共用一個很短的時間上限,只用它的八成;判定沒有快取的塊直接放棄
async function onEnd(st: State, $: any, e: any, remainingMs: number) {
  try {
    if (st.ledger) {
      const budget = Math.max(0, Math.floor((Number.isFinite(remainingMs) ? remainingMs : 1000) * 0.8))
      await Promise.race([st.ledger.flushSessionCachedOnly(e.sessionId), $.clock.sleep(budget)])
      st.ledger.drop(e.sessionId)
    }
    st.turnNo.delete(e.sessionId)
    st.origin.delete(e.sessionId)
  } catch { /* 同上 */ }
}

export const register: Register = on => {
  const st: State = { ledger: null, turnNo: new Map(), origin: new Map() }

  on('session.append', { door: 'prompt' } as any, async ($, e, next) => {
    await onPrompt(st, $, e)
    return next(e)
  })

  on('turn.start', async ($, e, next) => {
    await onTurnStart(st, $, e)
    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    await onTurnEnd(st, $, e)
    return next(e)
  })

  on('tool.call', async ($, e, next) => {
    let r: any
    try {
      r = await next(e)
    } catch (err) {
      await record(st, $, (e as any).agentId, 'tool', toolExtra(e, undefined, true)) // 被中斷也留一筆,再照原樣丟出去
      throw err
    }
    await record(st, $, (e as any).agentId, 'tool', toolExtra(e, r, false))
    return r
  })

  on('agent.spawn', async ($, e, next) => {
    const r = await next(e)
    await onSpawn(st, $, e, r)
    return r
  })

  on('session.end', async ($, e, next) => {
    await onEnd(st, $, e, (next as any).budget?.remainingMs)
    return next(e)
  })
}
