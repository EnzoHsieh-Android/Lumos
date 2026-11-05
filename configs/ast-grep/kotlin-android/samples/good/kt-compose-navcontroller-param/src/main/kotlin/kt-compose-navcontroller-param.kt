package good

@Composable
fun AppNav(navController: NavHostController = rememberNavController()) {
    NavHost(navController, startDestination = "a") {
        composable("a") { ItemRow(item, onOpen = { navController.navigate("d") }) }
    }
}

@Composable
fun ItemRow(item: Item, onOpen: () -> Unit) { Text(item.name) }

fun helper(nav: NavController) = nav.navigate("x")
