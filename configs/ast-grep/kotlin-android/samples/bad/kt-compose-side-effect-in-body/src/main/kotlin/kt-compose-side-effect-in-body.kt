package bad

@Composable
fun Home(ctx: Context, prefs: SharedPreferences) {
    Toast.makeText(ctx, "hi", Toast.LENGTH_SHORT).show() // BAD
    analytics.logEvent("home_view", null) // BAD
    prefs.edit().putBoolean("seen", true).apply() // BAD
    Column {
        prefs.edit { putInt("n", 1) } // BAD
    }
}
