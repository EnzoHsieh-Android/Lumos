package bad

@Composable
fun T(d: Density) {
    Text("a", fontSize = 16.dp.value.sp) // BAD
    val s = with(d) { 14.dp.toSp() } // BAD
}
