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

// 容易誤報:View 的點擊導航官方沒有給標準防護寫法(dropUnlessResumed 是 Compose 的),找不到權威出處就不報
class G9Fragment : Fragment() {
    fun bind(b: View) {
        b.setOnClickListener { findNavController().navigate(R.id.action_x) }
    }
}
