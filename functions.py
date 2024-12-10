import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import tiktoken


class ChunkSummary():
    def __init__(self, model_name, apikey, text, window_size, overlap_size):
        self.text = text
        if isinstance(self.text, str):
            self.text = [self.text]
        self.window_size = window_size
        self.overlap_size = overlap_size
        # Aplicacao dos chunks
        self.chunks = self.__text_to_chunks()
        self.model = self.__create_model(apikey, model_name)


    def __create_model(self, apikey, model_name):
        genai.configure(api_key=apikey)
        self.prompt_base = f"""
        ### Contexto
        Você é um assessor parlamentar que deve preparar um resumo das proposições dos deputados.


        Você deve retornar a resposta em um formato JSON com a seguinte estrutura:
    
        ```json
        
            "id1": "Resumo 1",
            "id2": "Resumo 2",
            "id3": "Resumo 3"
        
        ```


        """
        safety_settings={
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        generation_config = {
            'temperature': 0.2,
            'top_p': 0.8,
            'top_k': 20,
            'max_output_tokens': 1000
        }
        return genai.GenerativeModel(
            model_name,
            system_instruction=self.prompt_base,
            generation_config = generation_config,
            safety_settings=safety_settings
        )


    
    def __text_to_chunks(self):       
        n = self.window_size  # Tamanho de cada chunk
        m = self.overlap_size  # overlap entre chunks
        return [self.text[i:i+n] for i in range(0, len(self.text), n-m)]


    def __create_chunk_prompt(self, chunk):
        episode_lines = '\n'.join(chunk)
        prompt = f"""
        #subtitles#
        {episode_lines}
        ######
        Summarize it.
        """
        return prompt
        
    
    def __summarize_chunks(self):
        # Loop over chunks
        chunk_summaries = []
        for i, chunk in enumerate(self.chunks):
            print(f'Summarizing chunk {i+1} from {len(self.chunks)}')
            # Create prompt
            prompt = self.__create_chunk_prompt(chunk)
            response = self.model.generate_content(prompt)
            # Apendar resposta do chunk
            chunk_summaries.append(response.text)
            
            # if i == 4: break

        return chunk_summaries


    def summarize(self):
        print('Summarizing text')
        # Chamar o sumario dos chunks
        self.chunk_summaries = self.__summarize_chunks()
        # Prompt final
        summaries = '- ' + '\n- '.join(self.chunk_summaries)
        prompt = f"""
        ### Contexto
        Você é um assessor parlamentar que deve preparar um resumo das proposições dos deputados.

        ### Instrução

        Resuma as proposições, uma a uma, dos deputados constantes no seguintes dados:
        {summaries}


        Você deve retornar a resposta em um formato JSON com a seguinte estrutura:
    
        ```json
        
            "id1": "Resumo 1",
            "id2": "Resumo 2",
            "id3": "Resumo 3"
        
        ```
        """
        print('Final summarization')
        response = self.model.generate_content(prompt)
        
        return response.text


# Função para estimar número de tokens
def estimar_tokens(texto):
    encoder = tiktoken.get_encoding("cl100k_base")  # Exemplo de codificação
    tokens = encoder.encode(texto)
    return tokens
