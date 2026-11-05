package good

// case: hilt-false
@AndroidEntryPoint
class AD3Fragment : Fragment() {
    override fun onCreate(s: Bundle?) { super.onCreate(s); retainInstance = false }
}
// case: non-hilt-retain
class AD4Fragment : Fragment() {
    override fun onCreate(s: Bundle?) { super.onCreate(s); retainInstance = true }
}
