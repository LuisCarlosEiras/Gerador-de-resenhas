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
