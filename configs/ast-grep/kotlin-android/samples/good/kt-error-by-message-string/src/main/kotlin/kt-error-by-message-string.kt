fun a(e: Exception) = when (e) { is SocketTimeoutException -> Timeout; is UnknownHostException -> Offline; else -> Other } // GOOD
fun b(chat: List<Msg>, q: String) = chat.filter { it.message?.contains(q) == true } // GOOD 聊天訊息,不是例外
fun c(m: Mail) = m.message.contains("hi") // GOOD
