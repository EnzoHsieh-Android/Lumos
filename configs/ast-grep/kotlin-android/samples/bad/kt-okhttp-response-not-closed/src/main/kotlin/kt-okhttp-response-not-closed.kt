fun a(client: OkHttpClient, req: Request): Int {
    val r = client.newCall(req).execute() // BAD
    return r.code
}
fun b(client: OkHttpClient, req: Request): Boolean =
    client.newCall(req).execute().isSuccessful // BAD
