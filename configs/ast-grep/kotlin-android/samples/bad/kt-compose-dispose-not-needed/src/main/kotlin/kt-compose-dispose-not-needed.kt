package bad

@Composable
fun Screen(id: String) {
    DisposableEffect(id) {  // BAD
        analytics.log("open $id")
        onDispose { }
    }
}

@Composable
fun Banner() {
    DisposableEffect(Unit) {  // BAD
        onDispose {}
    }
}
