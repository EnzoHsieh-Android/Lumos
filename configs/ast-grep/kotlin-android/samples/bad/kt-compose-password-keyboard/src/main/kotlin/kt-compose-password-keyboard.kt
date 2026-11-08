@Composable
fun LoginPassword(password: String, onChange: (String) -> Unit) {
    OutlinedTextField(
        value = password,
        onValueChange = onChange,
        label = { Text("密碼") },
        visualTransformation = PasswordVisualTransformation(), // BAD 只遮字,鍵盤會記住
    )
}

@Composable
fun Pin(pin: String, onChange: (String) -> Unit) {
    TextField(
        value = pin,
        onValueChange = onChange,
        visualTransformation = PasswordVisualTransformation(),
        keyboardOptions = KeyboardOptions(imeAction = ImeAction.Done), // BAD 寫了鍵盤選項卻沒設密碼鍵盤
    )
}
