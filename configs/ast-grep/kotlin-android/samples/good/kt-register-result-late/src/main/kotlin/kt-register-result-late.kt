package good

// case: member-property
class W4Fragment : Fragment() {
    private val pick = registerForActivityResult(GetContent()) { uri -> use(uri) }
}
// case: unconditional-onCreate
class W5Activity : AppCompatActivity() {
    override fun onCreate(s: Bundle?) { super.onCreate(s); launcher = registerForActivityResult(TakePicture()) { } }
}
// case: compose-remember-launcher
@Composable
fun Picker() { val l = rememberLauncherForActivityResult(GetContent()) { } }
