fun a(resp: Response): String {
    Log.d("t", resp.body!!.string())
    return resp.body!!.string() // BAD
}
fun b(resp: Response) {
    val s1 = resp.body?.string()
    val s2 = resp.body?.string() // BAD
}
