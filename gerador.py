import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Configura as APIs
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

def gerar_resenha(livro):
    """
    Gera uma resenha estruturada do livro usando o modelo Gemini Pro, sem títulos nos parágrafos
    """
    model = genai.GenerativeModel('gemini-pro')

    def gerar_paragrafo(prompt, contexto=""):
        response = model.generate_content(
            f"{contexto}\n\n{prompt}",
            generation_config={
                "temperature": 0.1,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
        )
        return response.text.strip()

    estrutura_resenha = f"""Escreva uma resenha acadêmica do livro '{livro}' em quatro parágrafos, sem incluir títulos:
    
    1. Contextualize a obra e o autor, mencionando o período histórico e o contexto literário.
    2. Analise aspectos técnicos, como estrutura narrativa, estilo de escrita e técnicas literárias empregadas.
    3. Explore os temas principais, simbolismos e significados mais profundos da obra.
    4. Avalie criticamente a contribuição da obra para o campo literário, sem repetir conclusões anteriores.
    """
    
    prompts = [
        (f"{estrutura_resenha}\n\nEscreva APENAS o primeiro parágrafo, contextualizando a obra e o autor:"),
        (f"Agora, escreva APENAS o segundo parágrafo, analisando os aspectos técnicos do livro:"),
        (f"Em seguida, escreva APENAS o terceiro parágrafo, explorando os temas e simbolismos principais:"),
        (f"Por fim, escreva APENAS o parágrafo final, com uma avaliação crítica da contribuição do livro para o campo literário:")
    ]
    
    paragraphs = []
    contexto_atual = ""
    
    for prompt in prompts:
        paragrafo = gerar_paragrafo(prompt, contexto_atual)
        # Filtrar comentários e texto irrelevante
        if not any(termo in paragrafo.lower() for termo in [
            "não há informações", 
            "não contém informações",
            "não há um segundo parágrafo",
            "não fornece informações",
            "não há dados disponíveis"
        ]):
            paragraphs.append(paragrafo)
        contexto_atual += f"\n{paragrafo}"

    def formatar_paragrafo(paragrafo):
        sentences = paragrafo.split('.')
        formatted_sentences = [s.strip() + '.' for s in sentences if s.strip()]
        return ' '.join(formatted_sentences)

    paragraphs = [formatar_paragrafo(p) for p in paragraphs]
    
    return '\n\n'.join(paragraphs)

def main():
    st.title("Antes de comprar, escreva a resenha do livro")
    
    # Input direto (sem botão)
    livro = st.text_input("Digite o título do livro e o autor, separados por vírgula, e tecle Enter:")

    if livro:
        with st.spinner('Gerando resenha...'):
            try:
                # Gera a resenha
                resenha = gerar_resenha(livro)
                st.write(resenha)
            
            except Exception as e:
                st.error(f"Erro ao processar sua solicitação: {str(e)}")

if __name__ == "__main__":
    main()
