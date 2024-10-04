import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Configura a API do Google Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

def gerar_resenha(livro):
    # Configura o modelo
    model = genai.GenerativeModel('gemini-pro')
    
    # Função auxiliar para gerar parágrafos
    def gerar_paragrafo(prompt, contexto=""):
        response = model.generate_content(
            f"{contexto}\n\n{prompt}",
            generation_config={"temperature": 0.7}
        )
        return response.text.strip()

    # Gera os parágrafos
    prompt_base = f"Como estudioso de literatura, escreverei uma resenha do livro '{livro}'."
    
    paragraph1 = gerar_paragrafo(f"{prompt_base}\n\nPrimeiro parágrafo:")
    paragraph2 = gerar_paragrafo("Escreva o segundo parágrafo da resenha:", f"{prompt_base}\n{paragraph1}")
    paragraph3 = gerar_paragrafo("Escreva o terceiro parágrafo da resenha:", f"{prompt_base}\n{paragraph1}\n{paragraph2}")
    paragraph4 = gerar_paragrafo("Escreva o quarto parágrafo da resenha:", f"{prompt_base}\n{paragraph1}\n{paragraph2}\n{paragraph3}")

    # Formata os parágrafos
    def formatar_paragrafo(paragrafo):
        sentences = paragrafo.split('.')
        formatted_sentences = [s.strip() + '.' for s in sentences if s.strip()]
        return ' '.join(formatted_sentences)

    paragraphs = [formatar_paragrafo(p) for p in [paragraph1, paragraph2, paragraph3, paragraph4]]
    
    return '\n\n'.join(paragraphs)

def main():
    st.title("Antes de comprar, escreva a resenha do livro")

    livro = st.text_input("Digite o título do livro e o autor para gerar a resenha, separados por vírgula:")

    if st.button("Gerar Resenha"):
        if livro:
            with st.spinner('Gerando resenha...'):
                try:
                    resenha = gerar_resenha(livro)
                    st.subheader("Resenha Gerada:")
                    st.write(resenha)
                except Exception as e:
                    st.error(f"Erro ao gerar resenha: {str(e)}")
        else:
            st.warning("Por favor, insira o título e autor do livro.")

if __name__ == "__main__":
    main()
