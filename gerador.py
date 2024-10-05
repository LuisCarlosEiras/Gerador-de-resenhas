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

    # Prompt mais específico para aumentar a precisão
    prompt_base = f"""Como um crítico literário especializado, escreverei uma resenha acadêmica detalhada e precisa do livro '{livro}'. 
    A resenha deve incluir:
    - Análise do contexto histórico e literário
    - Avaliação crítica do estilo narrativo e técnicas literárias
    - Discussão dos temas principais e sua relevância
    - Conclusão com uma avaliação objetiva da obra"""
    
    paragraph1 = gerar_paragrafo(f"{prompt_base}\n\nPrimeiro parágrafo focando na contextualização e apresentação geral da obra:")
    paragraph2 = gerar_paragrafo("Segundo parágrafo analisando aspectos técnicos e estilísticos:", f"{prompt_base}\n{paragraph1}")
    paragraph3 = gerar_paragrafo("Terceiro parágrafo explorando temas e significados:", f"{prompt_base}\n{paragraph1}\n{paragraph2}")
    paragraph4 = gerar_paragrafo("Quarto parágrafo com conclusão e avaliação final:", f"{prompt_base}\n{paragraph1}\n{paragraph2}\n{paragraph3}")

    def formatar_paragrafo(paragrafo):
        sentences = paragrafo.split('.')
        formatted_sentences = [s.strip() + '.' for s in sentences if s.strip()]
        return ' '.join(formatted_sentences)

    paragraphs = [formatar_paragrafo(p) for p in [paragraph1, paragraph2, paragraph3, paragraph4]]
    
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
        # Aqui você implementaria a lógica para salvar/exibir a imagem
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
