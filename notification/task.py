import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Настройки SMTP
smtp_server = 'smtp.jino.ru'
smtp_port = 587
username = 'main@skynet.expert'
password = 'nd-VfP9nbxWu'
# Создание письма

msg = MIMEMultipart("alternative")
msg["Subject"] = "✨ Приветственное письмо"
msg['From'] = username
msg['To'] = 'ytdzpipt@gmail.com'



try:
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.set_debuglevel(1)           # Включаем отладку
        server.starttls()                  # Активируем TLS
        server.login(username, password)  # Аутентификация
        server.send_message(msg)          # Отправка
        print("Письмо успешно отправлено!")
except Exception as e:
    print(f"Ошибка: {e}")
