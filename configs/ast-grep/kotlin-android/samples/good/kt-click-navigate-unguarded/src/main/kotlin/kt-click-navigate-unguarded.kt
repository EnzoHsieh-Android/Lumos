package good

// case: dropUnlessResumed
@Composable
fun Home2(nav: NavHostController = rememberNavController()) {
    NavHost(nav, startDestination = "home") {
        composable("home") { Button(onClick = dropUnlessResumed { nav.navigate("help") }) { Text("Help") } }
    }
}
// case: currentDestination-guard
class E2Fragment : Fragment() {
    fun bind(b: View) {
        b.setOnClickListener {
            val nc = findNavController()
            if (nc.currentDestination?.id == R.id.home) nc.navigate(R.id.action_x)
        }
    }
}
// case: onclick-callback-up
@Composable
fun Card1(onOpen: () -> Unit) {
    Button(onClick = { onOpen() }) { Text("Open") }
}
