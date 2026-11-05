package good

// case: screen-level
@Composable
fun UserListScreen() {
    val vm: UserListViewModel = hiltViewModel()
}
// case: default-param
@Composable
fun PriceCard2(vm: PriceViewModel = viewModel()) { }
// case: navhost-destination
@Composable
fun AppNav(nav: NavHostController) {
    NavHost(nav, startDestination = "home") {
        composable("home") { val vm = hiltViewModel<HomeViewModel>() }
    }
}
