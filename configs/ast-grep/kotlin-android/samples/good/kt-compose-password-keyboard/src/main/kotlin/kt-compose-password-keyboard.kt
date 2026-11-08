@Composable
fun LoginPassword(password: String, onChange: (String) -> Unit) {
    OutlinedTextField(
        value = password,
        onValueChange = onChange,
        visualTransformation = PasswordVisualTransformation(),
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
    )
}

@Composable
fun Pin(pin: String, onChange: (String) -> Unit) {
    TextField(
        value = pin,
        onValueChange = onChange,
        visualTransformation = PasswordVisualTransformation(),
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.NumberPassword, imeAction = ImeAction.Done),
    )
}

@Composable
fun NewPassword(state: TextFieldState) {
    SecureTextField(state = state)
}
