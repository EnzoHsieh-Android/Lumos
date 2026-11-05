fun a(resp: Response): String {
    val text = resp.body!!.string() // GOOD 讀一次存起來
    Log.d("t", text)
    return text
}
fun b(resp: Response): InputStream = resp.body!!.byteStream() // GOOD 串流
fun c(resp: Response) = resp.body!!.string() // GOOD 不同函式各讀一次
fun d(resp: Response) = resp.body!!.string() // GOOD
