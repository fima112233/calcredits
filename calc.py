from flask import Flask, request, render_template_string
import math

app = Flask(__name__)

# HTML шаблон с жёстким стеклом и НЕЗАКРЫВАЕМЫМ рекламным окном
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Калькулятор кредитов — EFMStudio</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            font-family: 'Segoe UI', 'Roboto', sans-serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        /* Жёсткое стекло (glassmorphism) */
        .glass {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(12px);
            border-radius: 32px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }

        .container {
            max-width: 550px;
            width: 100%;
            padding: 30px;
        }

        h1 {
            text-align: center;
            color: #fff;
            font-size: 28px;
            margin-bottom: 8px;
            letter-spacing: 1px;
        }

        .subtitle {
            text-align: center;
            color: rgba(255, 255, 255, 0.7);
            font-size: 14px;
            margin-bottom: 25px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            padding-bottom: 15px;
        }

        .input-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            color: #fff;
            margin-bottom: 8px;
            font-weight: 500;
            font-size: 14px;
        }

        input {
            width: 100%;
            padding: 12px 16px;
            background: rgba(255, 255, 255, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 16px;
            color: #fff;
            font-size: 16px;
            transition: 0.2s;
            outline: none;
        }

        input:focus {
            border-color: #00ffcc;
            background: rgba(255, 255, 255, 0.2);
            box-shadow: 0 0 8px rgba(0, 255, 204, 0.3);
        }

        input::placeholder {
            color: rgba(255, 255, 255, 0.5);
        }

        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(95deg, #00ffcc, #00b8a9);
            border: none;
            border-radius: 28px;
            color: #0f2027;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.2s;
            margin-top: 10px;
            margin-bottom: 25px;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 255, 204, 0.3);
        }

        .result {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 24px;
            padding: 20px;
            margin-top: 10px;
            border-left: 4px solid #00ffcc;
        }

        .result p {
            color: #fff;
            margin: 10px 0;
            font-size: 16px;
        }

        .result .amount {
            font-size: 24px;
            font-weight: bold;
            color: #00ffcc;
        }

        /* Рекламное окно (квадрат) - НЕЗАКРЫВАЕМОЕ */
        .ad-box {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.1));
            backdrop-filter: blur(16px);
            border-radius: 24px;
            padding: 20px;
            margin-top: 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 2px solid rgba(255, 215, 0, 0.7);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            position: relative;
        }

        .ad-box:hover {
            transform: scale(1.02);
            background: linear-gradient(135deg, rgba(255, 215, 0, 0.25), rgba(255, 215, 0, 0.15));
            border-color: rgba(255, 215, 0, 1);
        }

        .ad-title {
            font-size: 20px;
            font-weight: bold;
            color: #ffd700;
            margin-bottom: 10px;
        }

        .ad-text {
            font-size: 14px;
            color: rgba(255, 255, 255, 0.95);
            line-height: 1.5;
        }

        .ad-hint {
            font-size: 11px;
            color: rgba(255, 255, 255, 0.5);
            margin-top: 12px;
            font-style: italic;
        }

        .footer {
            text-align: center;
            margin-top: 20px;
            font-size: 11px;
            color: rgba(255, 255, 255, 0.4);
        }

        hr {
            margin: 15px 0;
            border-color: rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <div class="container glass">
        <h1>💸 Калькулятор кредитов</h1>
        <div class="subtitle">EFMStudio — честный расчёт без скрытых комиссий</div>

        <form method="POST">
            <div class="input-group">
                <label>💰 Сумма кредита (₽)</label>
                <input type="number" name="amount" value="{{ amount }}" step="1000" placeholder="Например: 1000000" required>
            </div>

            <div class="input-group">
                <label>📅 Срок (месяцев)</label>
                <input type="number" name="months" value="{{ months }}" placeholder="Например: 12" required>
            </div>

            <div class="input-group">
                <label>📈 Процентная ставка (% годовых)</label>
                <input type="number" name="rate" value="{{ rate }}" step="0.1" placeholder="Например: 15.5" required>
            </div>

            <button type="submit">📊 Рассчитать кредит</button>
        </form>

        {% if result %}
        <div class="result">
            <p>📆 <strong>Ежемесячный платёж:</strong><br>
            <span class="amount">{{ result.monthly }} ₽</span></p>
            <p>💰 <strong>Общая сумма выплат:</strong><br>
            {{ result.total_payment }} ₽</p>
            <p>📈 <strong>Переплата по кредиту:</strong><br>
            {{ result.overpayment }} ₽</p>
            <hr>
            <p style="font-size:13px; opacity:0.7;">✅ Аннуитетный платёж (фиксированный каждый месяц)</p>
        </div>
        {% endif %}

        <!-- НЕЗАКРЫВАЕМОЕ рекламное окно (квадрат) -->
        <div id="adBox" class="ad-box" onclick="location.href='/support'">
            <div class="ad-title">🍵 Поддержать EFMStudio</div>
            <div class="ad-text">
                Мы — целая команда разработчиков EFMStudio.<br>
                Мы были бы очень признательны, если бы вы поддержали нас.
            </div>
            <div class="ad-hint">✨ Нажмите, чтобы узнать реквизиты ✨</div>
        </div>

        <div class="footer">
            © 2026 EFMStudio — калькулятор кредитов. Помогаем не попасть в долговую яму.
        </div>
    </div>
</body>
</html>
"""

# Страница с поддержкой (реквизиты)
SUPPORT_PAGE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Поддержать EFMStudio</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            font-family: 'Segoe UI', 'Roboto', sans-serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .glass {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(12px);
            border-radius: 32px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            max-width: 550px;
            width: 100%;
            padding: 30px;
        }

        h1 {
            text-align: center;
            color: #ffd700;
            font-size: 28px;
            margin-bottom: 20px;
        }

        .message {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 20px;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
        }

        .message p {
            color: #fff;
            font-size: 16px;
            line-height: 1.6;
            margin: 10px 0;
        }

        .bank-details {
            background: rgba(0, 0, 0, 0.4);
            border-radius: 20px;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #ffd700;
        }

        .bank-title {
            font-size: 18px;
            font-weight: bold;
            color: #ffd700;
            margin-bottom: 15px;
        }

        .bank-item {
            margin: 12px 0;
            padding: 10px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
        }

        .bank-label {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.6);
            margin-bottom: 5px;
        }

        .bank-number {
            font-size: 18px;
            font-weight: bold;
            color: #00ffcc;
            letter-spacing: 1px;
        }

        .comment {
            background: rgba(255, 215, 0, 0.15);
            border-radius: 12px;
            padding: 12px;
            margin-top: 15px;
            text-align: center;
        }

        .comment-text {
            color: #ffd700;
            font-size: 14px;
            font-weight: bold;
        }

        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(95deg, #00ffcc, #00b8a9);
            border: none;
            border-radius: 28px;
            color: #0f2027;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 20px;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 255, 204, 0.3);
        }

        .footer {
            text-align: center;
            margin-top: 20px;
            font-size: 11px;
            color: rgba(255, 255, 255, 0.4);
        }
    </style>
</head>
<body>
    <div class="glass">
        <h1>🍵 Поддержать EFMStudio</h1>

        <div class="message">
            <p>Мы — целая команда разработчиков <strong>EFMStudio</strong>.</p>
            <p>Мы были бы очень признательны, если бы вы поддержали нас.</p>
        </div>

        <div class="bank-details">
            <div class="bank-title">💳 Реквизиты для поддержки:</div>

            <div class="bank-item">
                <div class="bank-label">Сбербанк</div>
                <div class="bank-number">+7 977 627 7844</div>
            </div>

            <div class="bank-item">
                <div class="bank-label">Т-Банк</div>
                <div class="bank-number">+7 985 512 7706</div>
            </div>

            <div class="comment">
                <div class="comment-text">⚠️ ОБЯЗАТЕЛЬНО комментарий: "Чаевые EFMStudio"</div>
                <div style="font-size: 11px; color: rgba(255,255,255,0.6); margin-top: 8px;">Это поможет нам не заблокировали карту случаем.</div>
            </div>
        </div>

        <button onclick="location.href='/'">← Вернуться к калькулятору</button>

        <div class="footer">
            © 2026 EFMStudio — спасибо за поддержку! ❤️
        </div>
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    amount = ""
    months = ""
    rate = ""
    result = None

    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount', 0))
            months = int(request.form.get('months', 0))
            rate = float(request.form.get('rate', 0))

            if amount <= 0 or months <= 0 or rate < 0:
                raise ValueError

            monthly_rate = rate / 100 / 12

            if monthly_rate == 0:
                monthly_payment = amount / months
            else:
                monthly_payment = amount * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)

            total_payment = monthly_payment * months
            overpayment = total_payment - amount

            result = {
                'monthly': f"{monthly_payment:,.2f}".replace(',', ' '),
                'total_payment': f"{total_payment:,.2f}".replace(',', ' '),
                'overpayment': f"{overpayment:,.2f}".replace(',', ' ')
            }
        except:
            result = {
                'monthly': "Ошибка ввода",
                'total_payment': "Проверьте данные",
                'overpayment': "Сумма, срок и ставка должны быть >0"
            }

    return render_template_string(HTML_TEMPLATE, amount=amount, months=months, rate=rate, result=result)

@app.route('/support')
def support():
    return render_template_string(SUPPORT_PAGE)

if __name__ == '__main__':
    app.run(debug=True)