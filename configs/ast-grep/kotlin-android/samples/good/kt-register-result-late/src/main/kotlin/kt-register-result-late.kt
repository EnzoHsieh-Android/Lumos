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

// case: extension-helper(代碼審 r1 m3:擴充函式 helper,供屬性初始化或 onCreate 呼叫)
fun ComponentActivity.registerPick(cb: ActivityResultCallback<Uri?>) = registerForActivityResult(GetContent(), cb)
