import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
import requests
from io import BytesIO

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

def criar_prompt_imagem(resenha, livro):
    """
    Cria um prompt otimizado para o modelo de geração de imagens Google Imagen 3 (hipotético)
    """
    model = genai.GenerativeModel('gemini-pro')
    
    prompt_para_gemini = f"""Com base nesta resenha do livro '{livro}':
    {resenha[:1000]}...
    
    Crie um prompt artístico CONSERVADOR e SEGURO para uma ilustração abstrata que:
    1. Foque em elementos abstratos e simbólicos que representem os temas do livro
    2. Evite menções a violência, conteúdo adulto ou temas sensíveis
    3. Use metáforas visuais apropriadas para todos os públicos
    4. Enfatize cores, formas e composição
    5. Mantenha um tom profissional e artístico
    
    Regras:
    - Evite pessoas específicas ou rostos reconhecíveis
    - Evite referências a marcas ou direitos autorais
    - Use linguagem neutra e apropriada
    - Foque em paisagens, natureza, objetos simbólicos ou padrões abstratos
    """
    
    try:
        response = model.generate_content(prompt_para_gemini)
        prompt_gerado = response.text.strip()
        prompt_final = f"{prompt_gerado} Style: digital art, professional, elegant, suitable for all audiences."
        return prompt_final
    except Exception as e:
        st.error(f"Erro ao gerar prompt: {str(e)}")
        return None

def gerar_imagem_google(prompt):
    """
    Gera uma imagem usando o Google Imagen (hipotético)
    """
    try:
        # Supondo que o Google disponibilize um método para gerar imagens
        response = genai.Imagen.create(
            model="imagen-3",
            prompt=prompt,
            size="1792x1024",
        )
        return response.data[0].url
    except Exception as e:
        st.error(f"Erro ao gerar imagem: {str(e)}")
        return None

def main():
    st.title("Antes de comprar, escreva sua própria resenha do livro")
    
    # Inicializa session state
    if 'image_url' not in st.session_state:
        st.session_state.image_url = None

    # Input direto (sem botão)
    livro = st.text_input("Digite o título do livro e o autor para gerar a resenha, separados por vírgula:")

    if livro:
        with st.spinner('Gerando resenha...'):
            try:
                # Gera a resenha
                resenha = gerar_resenha(livro)
                st.write(resenha)
                
                # Gera a visualização
                with st.spinner('Gerando imagem...'):
                    # Gera o prompt
                    prompt_google = criar_prompt_imagem(resenha, livro)
                    
                    if prompt_google:
                        # Gera a imagem
                        image_url = gerar_imagem_google(prompt_google)
                        if image_url:
                            st.session_state.image_url = image_url
                            # Baixa e mostra a imagem
                            response = requests.get(image_url)
                            img = Image.open(BytesIO(response.content))
                            st.image(
                                img,
                                caption="Imagem gerada pelo Google Imagen",
                                use_column_width=True
                            )
            
            except Exception as e:
                st.error(f"Erro ao processar sua solicitação: {str(e)}")

if __name__ == "__main__":
    main()
