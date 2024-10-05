import streamlit as st
import google.generativeai as genai
import openai
import os
from dotenv import load_dotenv
from PIL import Image
import requests
from io import BytesIO

# Carrega as variáveis de ambiente
load_dotenv()

# Configura as APIs
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
openai.api_key = os.getenv('OPENAI_API_KEY')

def gerar_resenha(livro):
    # [O código da função gerar_resenha permanece o mesmo]
    # ... [mantenha todo o código existente da função]

def criar_prompt_imagem(resenha, livro):
    """Cria um prompt otimizado para o DALL-E 3"""
    model = genai.GenerativeModel('gemini-pro')
    
    prompt_para_gemini = f"""Com base nesta resenha do livro '{livro}':
    {resenha[:1000]}...
    
    Crie um prompt artístico para o DALL-E 3 que:
    1. Capture a essência e os temas principais do livro
    2. Inclua elementos visuais específicos e simbólicos
    3. Especifique estilo artístico e atmosfera
    4. Mantenha proporção 9:6
    5. Seja detalhado e específico
    6. Use linguagem que o DALL-E 3 entenda bem
    
    Formato: "Create a 9:6 [estilo] illustration showing [descrição detalhada]"
    """
    
    response = model.generate_content(prompt_para_gemini)
    return response.text.strip()

def gerar_imagem_dalle(prompt):
    """Gera uma imagem usando DALL-E 3"""
    try:
        response = openai.Image.create(
            model="dall-e-3",
            prompt=f"{prompt} Use 9:6 aspect ratio.",
            size="1792x1024",  # Proporção 9:6
            quality="standard",
            n=1,
        )
        return response.data[0].url
    except Exception as e:
        st.error(f"Erro ao gerar imagem com DALL-E: {str(e)}")
        return None

def gerar_descricao_gemini(resenha):
    """Gera uma descrição conceitual usando Gemini"""
    model = genai.GenerativeModel('gemini-pro')
    
    prompt_descricao = f"""Analise esta resenha e crie uma descrição artística conceitual:
    {resenha[:500]}...
    
    Descreva:
    1. Os elementos visuais principais que representam a obra
    2. O simbolismo presente
    3. A atmosfera e tom visual
    4. Como estes elementos se conectam com os temas do livro
    """
    
    try:
        response = model.generate_content(prompt_descricao)
        return response.text
    except Exception as e:
        st.error(f"Erro ao gerar descrição conceitual: {str(e)}")
        return None

def main():
    st.title("Antes de comprar, escreva sua própria resenha do livro")

    # Inicializa session state se necessário
    if 'image_url' not in st.session_state:
        st.session_state.image_url = None

    # Usando forms para capturar o Enter
    with st.form(key='resenha_form'):
        livro = st.text_input("Digite o título do livro e o autor para gerar a resenha, separados por vírgula:")
        submit_button = st.form_submit_button(label='Gerar Resenha')

        if submit_button and livro:
            with st.spinner('Gerando resenha e imagem...'):
                try:
                    # Gera a resenha
                    resenha = gerar_resenha(livro)
                    st.subheader("Resenha Gerada:")
                    st.write(resenha)
                    
                    # Gera o prompt para o DALL-E
                    st.subheader("Visualização Artística:")
                    with st.spinner('Gerando imagem...'):
                        # Gera o prompt otimizado
                        prompt_dalle = criar_prompt_imagem(resenha, livro)
                        
                        # Gera a imagem com DALL-E
                        image_url = gerar_imagem_dalle(prompt_dalle)
                        if image_url:
                            st.session_state.image_url = image_url
                            # Baixa e mostra a imagem
                            response = requests.get(image_url)
                            img = Image.open(BytesIO(response.content))
                            st.image(img, caption="Imagem gerada pelo DALL-E 3", use_column_width=True)
                            
                            # Mostra o prompt usado
                            with st.expander("Ver prompt usado para gerar a imagem"):
                                st.write(prompt_dalle)
                        
                        # Gera e mostra a descrição conceitual do Gemini
                        descricao = gerar_descricao_gemini(resenha)
                        if descricao:
                            with st.expander("Ver análise conceitual da visualização"):
                                st.write(descricao)
                    
                except Exception as e:
                    st.error(f"Erro ao processar sua solicitação: {str(e)}")
        elif submit_button:
            st.warning("Por favor, insira o título e autor do livro.")

if __name__ == "__main__":
    main()
