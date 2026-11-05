package bad

// case: fragment-inject-repo
@AndroidEntryPoint
class AC1Fragment : Fragment() {
    @Inject lateinit var repo: UserRepository
    fun onSave() { lifecycleScope.launch { repo.save() } }
}
// case: composable-usecase-param
@Composable
fun Profile(getUser: GetUserUseCase) { }
// case: activity-ctor-like-property
class AC2Activity : AppCompatActivity() {
    private val repo: OrderRepository by inject()
}
