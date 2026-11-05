package good

val LocalRepo = compositionLocalOf<Repo> { error("沒有提供 LocalRepo") }
val LocalSpacing = compositionLocalOf { 8.dp }
val LocalAccent = staticCompositionLocalOf { Color(0xFF6200EE) }
val LocalUser = compositionLocalOf<User?> { null }
val LocalStyle = compositionLocalOf { TextStyle() }
