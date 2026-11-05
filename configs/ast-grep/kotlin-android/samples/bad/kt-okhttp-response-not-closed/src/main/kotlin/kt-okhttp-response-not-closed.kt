fun a(client: OkHttpClient, req: Request): Int {
    val r = client.newCall(req).execute() // BAD
    return r.code
}
fun b(client: OkHttpClient, req: Request): Boolean =
    client.newCall(req).execute().isSuccessful // BAD

// 代碼審 r2(規則A F5):讀的是別的 body,execute() 回來的那個沒關
fun ok1(c: OkHttpClient, req: Request, other: Response): String { val r = c.newCall(req).execute(); val x = other.body?.string(); return "a" } // BAD
