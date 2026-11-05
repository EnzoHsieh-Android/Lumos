package bad

// case: assign-true
@AndroidEntryPoint
class AD1Fragment : Fragment() {
    override fun onCreate(s: Bundle?) { super.onCreate(s); retainInstance = true }
}
// case: setter-call
@AndroidEntryPoint
class AD2Fragment : Fragment() {
    init { setRetainInstance(true) }
}
