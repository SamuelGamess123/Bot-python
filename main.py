from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ServiceChrome
from webdriver_manager.chrome import ChromeDriverManager
import telebot
import logging
import os  # Importe o módulo os para definir as configurações do Flask

from flask import Flask  # Importe a classe Flask do módulo flask

# Configurações do Gunicorn
bind = '0.0.0.0:8000'  # Endereço e porta em que o servidor estará escutando
workers = 4  # Número de processos de trabalho para o Gunicorn
timeout = 60  # Tempo limite máximo para as requisições em segundos
keepalive = 2  # Tempo em segundos que as conexões do cliente serão mantidas abertas

# Inicializar a aplicação Flask
app = Flask(__name__)

# Inicializar o bot do Telegram
# Coloque aqui o token do seu bot
TOKEN = '6986018501:AAFMZ0VCxW1toU9bqvz6zlrrlI_dW345b6s'

# Inicializar o bot do Telegram
bot = telebot.TeleBot(TOKEN)

# Função para lidar com o comando /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Olá! Como posso ajudar?")

# Função para lidar com as mensagens do usuário
@bot.message_handler(func=lambda message: True)
def echo(message):
    text = message.text
    bot.send_message(message.chat.id, "Carregando...")
    # Inicializar o driver do Selenium
    driver = webdriver.Chrome(service=ServiceChrome(ChromeDriverManager().install()))

    # Acessar o site alvo
    driver.get('https://www.craiyon.com')

    # Enviar a mensagem do usuário para a textarea
    prompt = driver.find_element(By.ID, 'prompt')
    prompt.send_keys(text)

    # Clicar no botão de geração
    generate_button = driver.find_element(By.ID, 'generateButton')
    generate_button.click()

    try:
        # Esperar até que a imagem seja carregada (timeout de 2 minutos)
        wait = WebDriverWait(driver, 120)
        image = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'img.h-full.w-full.object-cover.object-center.transition-all.duration-300.sm:group-hover:scale-105')))
        image_src = image.get_attribute('src')

        # Enviar a imagem para o usuário
        bot.send_photo(message.chat.id, image_src)

    except TimeoutException:
        # Caso a imagem não seja encontrada dentro do tempo limite
        bot.send_message(message.chat.id, "Não foi possível obter a imagem dentro do tempo limite.")

    # Fechar o driver do Selenium
    driver.quit()

# Iniciar o bot usando o método polling
def run_bot():
    bot.polling()

# Verificar se o módulo está sendo executado diretamente e iniciar o bot
if __name__ == "__main__":
    # Iniciar o bot em uma thread separada
    import threading
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

if __name__ == '__main__':
    # Iniciar o Gunicorn com o aplicativo Flask
    from gunicorn.app.base import BaseApplication

    class StandaloneApplication(BaseApplication):
        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super().__init__()

        def load_config(self):
            config = {key: value for key, value in self.options.items()
                      if key in self.cfg.settings and value is not None}
            for key, value in config.items():
                self.cfg.set(key.lower(), value)

        def load(self):
            return self.application

    options = {
        'bind': bind,
        'workers': workers,
        'timeout': timeout,
        'keepalive': keepalive,
    }

    StandaloneApplication(app, options).run()
