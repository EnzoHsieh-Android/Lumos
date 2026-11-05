package bad

val LocalRepo = compositionLocalOf { FakeRepo() } // BAD
val LocalAnalytics = staticCompositionLocalOf<Analytics> { NoopAnalytics() } // BAD
