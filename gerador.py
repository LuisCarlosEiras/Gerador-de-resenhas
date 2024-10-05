import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
import io
import base64

# Carrega as variáveis de ambiente
load_dotenv()

# Configura a API do Google Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

def gerar_resenha(livro):
    # Configura o modelo com temperatura baixa para máxima precisão
    model = genai.GenerativeModel('gemini-pro')
    
    def gerar_paragrafo(prompt, contexto=""):
        response = model.generate_content(
            f"{contexto}\n\n{prompt}",
            generation_config={
                "temperature": 0.1,  # Temperatura baixa para maior precisão
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
        )
        return response.text.strip()

    # Estrutura clara para cada parágrafo
    estrutura_resenha = f"""Como crítico literário especializado, escreverei uma resenha acadêmica do livro '{livro}' em quatro parágrafos:

    1. Introdução: Contextualização da obra e autor
    2. Análise: Aspectos técnicos e estilísticos
    3. Interpretação: Temas principais e significados
    4. Avaliação final: Contribuição para o campo literário
    """
    
    prompts = [
        (f"{estrutura_resenha}\n\nEscreva APENAS o primeiro parágrafo com foco na contextualização da obra e seu autor, incluindo informações sobre o período histórico e contexto literário:"),
        
        (f"Considerando o parágrafo anterior sobre '{livro}', escreva APENAS o segundo parágrafo, focando na análise dos aspectos técnicos como estrutura narrativa, estilo de escrita e técnicas literárias empregadas:"),
        
        (f"Com base nos parágrafos anteriores sobre '{livro}', escreva APENAS o terceiro parágrafo, explorando os temas principais, simbolismos e significados mais profundos da obra:"),
        
        (f"Para finalizar a resenha de '{livro}', escreva APENAS o parágrafo final com uma avaliação crítica da contribuição da obra para o campo literário, SEM repetir conclusões anteriores:")
    ]
    
    paragraphs = []
    contexto_atual = ""
    
    for i, prompt in enumerate(prompts):
        paragrafo = gerar_paragrafo(prompt, contexto_atual)
        paragraphs.append(paragrafo)
        contexto_atual += f"\n{paragrafo}"

    def formatar_paragrafo(paragrafo):
        sentences = paragrafo.split('.')
        formatted_sentences = [s.strip() + '.' for s in sentences if s.strip()]
        return ' '.join(formatted_sentences)

    paragraphs = [formatar_paragrafo(p) for p in paragraphs]
    
    return '\n\n'.join(paragraphs)

def gerar_imagem_da_resenha(resenha):
    # Configura o modelo para geração de imagens
    model = genai.GenerativeModel('gemini-pro-vision')
    
    # Cria um prompt para a imagem baseado na resenha
    prompt_imagem = f"""Crie uma imagem artística que capture a essência desta resenha literária:
    {resenha[:500]}...
    
    A imagem deve:
    - Ter proporção 9:6
    - Usar elementos visuais que representem os temas principais do livro
    - Incorporar elementos simbólicos relevantes
    - Ter uma composição equilibrada e profissional
    """
    
    try:
        response = model.generate_content(prompt_imagem)
        return response.text
    except Exception as e:
        st.error(f"Erro ao gerar imagem: {str(e)}")
        return None

def main():
    st.title("Antes de comprar, escreva sua própria resenha do livro")

    # Usando forms para capturar o Enter
    with st.form(key='resenha_form'):
        livro = st.text_input("Digite o título do livro e o autor para gerar a resenha, separados por vírgula:")
        submit_button = st.form_submit_button(label='Gerar Resenha')

        if submit_button and livro:
            with st.spinner('Gerando resenha e imagem...'):
                try:
                    resenha = gerar_resenha(livro)
                    st.subheader("Resenha Gerada:")
                    st.write(resenha)
                    
                    # Gera e exibe a imagem
                    st.subheader("Imagem Conceitual:")
                    imagem_descricao = gerar_imagem_da_resenha(resenha)
                    if imagem_descricao:
                        st.write("Descrição da imagem gerada:")
                        st.write(imagem_descricao)
                        st.info("Nota: Este modelo pode apenas gerar descrições de imagens. Para gerar imagens reais, você precisaria usar um serviço específico de geração de imagens como DALL-E ou Stable Diffusion.")
                    
                except Exception as e:
                    st.error(f"Erro ao processar sua solicitação: {str(e)}")
        elif submit_button:
            st.warning("Por favor, insira o título e autor do livro.")

if __name__ == "__main__":
    main()
