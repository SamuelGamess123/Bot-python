# Importar as bibliotecas necessárias
import requests
import telebot
import os

# Criar um bot do telegram com o token fornecido
TOKEN = "6650035920:AAFAZg7PD7vgsLvC4cJWBPowgCMCuld4zls"
bot = telebot.TeleBot(TOKEN)

# Definir uma função para verificar se uma mensagem é um link válido
def is_link(message):
    # Verificar se a mensagem começa com http ou https
    if message.startswith("http://") or message.startswith("https://"):
        # Tentar fazer uma requisição para o link e verificar o status
        try:
            response = requests.get(message)
            if response.status_code == 200:
                # O link é válido
                return True
            else:
                # O link é inválido
                return False
        except:
            # Ocorreu um erro na requisição
            return False
    else:
        # A mensagem não é um link
        return False

# Definir uma função para obter o código-fonte de uma página web
def get_source(link):
    # Fazer uma requisição para o link com o prefixo view-source
    response = requests.get("view-source:" + link)
    # Retornar o texto da resposta
    return response.text

# Definir uma função para salvar o código-fonte em um arquivo HTML
def save_html(source, filename):
    # Abrir um arquivo com o nome fornecido no modo de escrita
    with open(filename, "w") as file:
        # Escrever o código-fonte no arquivo
        file.write(source)

# Definir uma função para enviar um arquivo HTML para o usuário
def send_html(chat_id, filename):
    # Abrir o arquivo com o nome fornecido no modo de leitura binária
    with open(filename, "rb") as file:
        # Enviar o arquivo para o usuário
        bot.send_document(chat_id, file)

# Definir um manipulador para as mensagens recebidas
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Obter o id do chat e o texto da mensagem
    chat_id = message.chat.id
    text = message.text
    # Verificar se a mensagem é um link válido
    if is_link(text):
        # Obter o código-fonte da página web
        source = get_source(text)
        # Gerar um nome de arquivo aleatório com a extensão .html
        filename = os.urandom(16).hex() + ".html"
        # Salvar o código-fonte em um arquivo HTML
        save_html(source, filename)
        # Enviar o arquivo HTML para o usuário
        send_html(chat_id, filename)
        # Deletar o arquivo HTML do servidor
        os.remove(filename)
    else:
        # Enviar uma mensagem de erro para o usuário
        bot.reply_to(message, "Desculpe, isso não é um link válido.")

# Iniciar o bot
bot.polling()