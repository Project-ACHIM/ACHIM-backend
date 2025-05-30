document.addEventListener('DOMContentLoaded', () => {
    console.log("JavaScriptが読み込まれました");

    // パスワード欄にカーソルを自動で移動させる
    const codeInput = document.getElementById('company-code');
    const passwordInput = document.getElementById('password');

    codeInput.addEventListener('input', () => {
        if (codeInput.value.length >= 7) {
            passwordInput.focus();
        }
    });
});
