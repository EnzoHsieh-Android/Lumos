package good

@Composable
fun Home(ctx: Context, prefs: SharedPreferences) {
    LaunchedEffect(Unit) { analytics.logEvent("home_view", null) }
    SideEffect { prefs.edit().putBoolean("seen", true).apply() }
    Button(onClick = { Toast.makeText(ctx, "hi", Toast.LENGTH_SHORT).show() }) { Text("t") }
    TextField(value = v, onValueChange = { prefs.edit { putString("v", it) } })
    val text = remember { analyticsLabel.format(1) }
}

fun track() { analytics.logEvent("x", null) }

// 容易誤報(代碼審 r1 M3):rememberLauncherForActivityResult 的回呼、組建內的區域函式
@Composable
fun AskPermission(ctx: Context) {
    val perm = rememberLauncherForActivityResult(RequestPermission()) { ok -> if (!ok) Toast.makeText(ctx, "x", 0).show() }
}

@Composable
fun Tracked(analytics: Analytics) {
    fun track() { analytics.logEvent("x") }
    Button(onClick = { track() }) { }
}
