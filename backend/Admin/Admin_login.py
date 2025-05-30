from flask import Flask, request, redirect, render_template, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # flashメッセージ用

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        code = request.form.get('company_code', '')
        password = request.form.get('password', '')

        # ログイン認証
        if code == '2230102' and password == '1203':
            return redirect(url_for('admin_home'))
        else:
            flash('ログイン失敗')
            return redirect(url_for('login'))

    return render_template('Admin_login.html')

# ログイン成功後に表示される管理者ホームページ
@app.route('/admin/home')
def admin_home():
    return render_template('Admin_home.html')

if __name__ == '__main__':
    app.run(debug=True)
