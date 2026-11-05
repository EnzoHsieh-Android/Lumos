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
