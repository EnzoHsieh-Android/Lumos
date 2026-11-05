package bad

// case: in-onclick
class W1Fragment : Fragment() {
    fun onPick() { registerForActivityResult(GetContent()) { uri -> use(uri) }.launch("image/*") }
}
// case: conditional-in-onCreate
class W2Activity : AppCompatActivity() {
    override fun onCreate(s: Bundle?) {
        super.onCreate(s)
        if (needsCamera) { launcher = registerForActivityResult(TakePicture()) { } }
    }
}
// case: lazy-property
class W3Activity : AppCompatActivity() {
    private val launcher by lazy { registerForActivityResult(StartActivityForResult()) { } }
}

// case: extension-block-body(代碼審 r2 規則A F7:擴充函式本體裡註冊,在點擊處理器呼叫就會拋例外)
fun Fragment.setup() { val l = registerForActivityResult(GetContent()) { } }
