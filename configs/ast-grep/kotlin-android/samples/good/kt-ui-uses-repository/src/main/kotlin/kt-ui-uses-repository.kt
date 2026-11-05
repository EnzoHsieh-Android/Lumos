package good

// case: fragment-vm
class AC3Fragment : Fragment() {
    private val vm: AC3ViewModel by viewModels()
}
// case: vm-takes-repo
class AC3ViewModel(private val repo: UserRepository) : ViewModel()
// case: composable-takes-vm
@Composable
fun Profile2(vm: ProfileViewModel = hiltViewModel()) { }
