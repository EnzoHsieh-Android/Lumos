package bad

@Composable
fun ItemRow(item: Item, nav: NavController) { // BAD
    Text(item.name, Modifier.clickable { nav.navigate("d/${item.id}") })
}

@Composable
fun Detail(
    id: String,
    navController: NavHostController, // BAD
) { Text(id) }
