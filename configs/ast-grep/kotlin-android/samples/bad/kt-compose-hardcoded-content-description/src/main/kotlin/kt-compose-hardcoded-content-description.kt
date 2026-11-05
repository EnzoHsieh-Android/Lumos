package bad

@Composable
fun Bar() {
    Icon(Icons.Default.Close, contentDescription = "關閉") // BAD
    Image(p, contentDescription = "Profile photo of $name") // BAD
    Box(Modifier.semantics { contentDescription = "Loading" }) // BAD
}
