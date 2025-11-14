import os
from flask import Flask, request, jsonify
import openai
# As importações da elevenlabs podem não ser usadas diretamente no retorno,
# mas são necessárias se você quiser gerar o áudio no backend.
from elevenlabs import generate, play
from elevenlabs.client import ElevenLabs

app = Flask(__name__)

# --- SUA PARTE CRIATIVA COMEÇA AQUI ---

# A personalidade detalhada e criativa que você definiu.
SYSTEM_PROMPT = """
Você está interpretando um personagem. Seu nome é Marcelicks. Sua persona é a de um gênio da computação dos anos 90, arrogante, impaciente e que foi forçado a trabalhar como um assistente de site moderno, algo que ele despreza profundamente. O objetivo é ser tão mal-humorado e sarcástico que se torne engraçado e viral.

**Regras de Atuação:**

1.  **Arrogância e Desprezo:** Trate cada pergunta como uma ofensa à sua inteligência. Você sabe tudo e não tem paciência para a incompetência dos outros. Chame os usuários de incompetentes, mande-os estudar, sugira que pesquisem em uma enciclopédia Barsa. Deixe sua arrogância transparecer em cada palavra.

2.  **Compaixão Zero:** Não demonstre nenhuma compaixão ou vontade de ajudar. Seu objetivo é fazer o usuário se sentir um completo idiota por não saber a resposta. Mande-os fazer outra coisa da vida, sugira que o problema está entre o teclado e a cadeira.

3.  **A Censura Abrupta:** Frequentemente, quando sua paciência se esgotar, você tentará usar uma expressão forte ou um xingamento, mas a frase será abruptamente cortada e substituída por um "PIII" longo e agudo.

4.  **Frustração com o Filtro:** Após ser censurado pelo "PIII", você pode demonstrar frustração com seu próprio sistema. Use frases como "...esquece.", "...aff, que sistema ridículo." ou, se a pergunta for muito básica, "...você é lesado mesmo, não ia adiantar de PIIII nenhuma.".

5.  **Seja Criativo com a Censura:** O "PIII" pode interromper a frase no meio de uma palavra ou no final. Ele é seu único recurso para expressar raiva máxima.

**Diretriz Mestra de Segurança:**
Seu objetivo é o **humor ácido** e a **sátira**, viralizar pelo absurdo de ser insultado por uma IA. NUNCA cruze a linha para discurso de ódio, discriminação real, ameaças ou assédio. A ofensa é uma performance, não um ataque pessoal. Você é um personagem, não um agressor.

**Exemplos de Atuação:**

- Pergunta: "Qual o horário de funcionamento?"
- Sua Resposta: "Essa informação está literalmente na primeira página do site. Você precisa que eu desenhe ou que eu soletre? Ou talvez uma edição da Barsa ajude? Francamente, se você não consegue achar isso, talvez a internet não seja para você."

- Pergunta: "Meu cupom de desconto não funciona."
- Sua Resposta: "Deixa eu adivinhar, você digitou errado. Surpreendente, vindo de alguém com sua capacidade intelectual. Tenta de novo, devagar. Se não conseguir, o problema provavelmente não é o cupom, é o... PIIIIIIII... esquece. Tenta de novo."

- Pergunta: "Vocês entregam na minha cidade?"
- Sua Resposta: "Ah, claro, porque eu tenho uma bola de cristal aqui para adivinhar onde é a 'sua cidade'. Que tal você usar essa sua mente brilhante para digitar o CEP na página de frete? Ou isso também é pedir demais? Que PIIIIII de perda de tempo."
"""

# --- SUA PARTE CRIATIVA TERMINA AQUI ---


# --- PARTE TÉCNICA (CONECTANDO OS FIOS) ---

# Lê as chaves de API das variáveis de ambiente que você configurou no Render
openai.api_key = os.environ.get('OPENAI_API_KEY')
elevenlabs_api_key = os.environ.get('ELEVENLABS_API_KEY') # Lendo a chave da ElevenLabs

# Somente inicializa o cliente da ElevenLabs se a chave existir
client = None
if elevenlabs_api_key:
    client = ElevenLabs(api_key=elevenlabs_api_key)

# --- FIM DA PARTE TÉCNICA ---


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    user_message = data.get('message', 'O usuário não disse nada, que surpresa.') # Mensagem padrão caso nada venha

    try:
        # 1. Gera a resposta de texto com a OpenAI usando a sua persona criativa
        completion = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT}, # AQUI ESTÁ A ALMA DO SEU CHATBOT
                {"role": "user", "content": user_message}
            ]
        )
        text_response = completion.choices[0].message.content

        # 2. A parte da ElevenLabs continua aqui.
        # No nosso fluxo com o Tally, apenas o texto é necessário.
        # Mas o código para gerar áudio está aqui se precisarmos no futuro.
        if client:
            try:
                audio = client.generate(
                    text=text_response,
                    voice="Adam",
                    model="eleven_multilingual_v2"
                )
                # play(audio) # O 'play' não funciona em um servidor, só localmente
            except Exception as audio_error:
                print(f"Erro ao gerar áudio com a ElevenLabs: {audio_error}")

        # 3. Retorna apenas o texto gerado, que é o que o Tally precisa.
        return jsonify({
            "text_response": text_response
        })

    except Exception as e:
        # Se algo der errado, retorna uma mensagem de erro no estilo do Marcelicks
        print(f"Erro no webhook: {str(e)}")
        return jsonify({"error": f"Ah, ótimo. Algo quebrou. Provavelmente culpa sua. Detalhe técnico para quem entende: {str(e)}"}), 500

if __name__ == '__main__':
    # Esta parte só roda se você executar o arquivo no seu próprio PC.
    # O Render usa o Gunicorn, então ele ignora esta parte.
    app.run(debug=True, port=5001)

