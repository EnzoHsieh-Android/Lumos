package bad

@Composable
fun L() {
    LazyColumn {
        item { // BAD
            Title("a")
            Subtitle("b")
        }
        item(key = "h") { Avatar(); Name(); Bio() } // BAD
    }
}
