import pandas as pd

class Pandas:
    """
    Encapsula a lógica para processar um "Mapa de Notas" do Excel,
    extraindo informações do cabeçalho e convertendo os dados 
    dos alunos de um formato 'largo' para 'longo'.
    
    Uso:
        processador = ProcessadorPlanilha(arquivo_planilha)
        info_turma = processador.get_informacoes_turma()
        dados_finais = processador.get_dados_processados()
    """
    
    # --- Constantes de Configuração (baseadas no código fornecido) ---
    
    # Posições do Cabeçalho
    _SLICE_CABECALHO_CTT = (slice(1, 4), slice(0, 2))   # Linhas 2-4, Colunas A-B
    _CHAVE_CABECALHO_CTT = "Unnamed: 0"
    _VALOR_CABECALHO_CTT = "Unnamed: 1"

    _SLICE_CABECALHO_CAS = (slice(1, 4), slice(14, 16)) # Linhas 2-4, Colunas O-P
    _CHAVE_CABECALHO_CAS = "Unnamed: 14"
    _VALOR_CABECALHO_CAS = "Unnamed: 15"
    
    _COLUNAS_CABECALHO_FINAL = ["CURSO", "TURMA", "TURNO", "CAMPUS", "ANO", "SÉRIE"]
    
    # Posições dos Dados dos Alunos
    _LINHA_INICIO_DADOS = 7      # Linha 8 no Excel
    _LINHA_NOMES_MATERIAS = 5  # Linha 6 no Excel
    
    _SLICE_ALUNOS = slice(1, 3)     # Colunas B e C (Matrícula, Nome)
    _SLICE_MATERIAS_NOTAS = slice(3, -1) # Da coluna D até a penúltima
    _COLUNA_SITUACAO = -1           # Última coluna

    _COLUNAS_NOTAS_RENOMEADAS = [
        "B1", "B2", "R1", "B3", "B4", "R2", "MÉDIA ANUAL", 
        "MÉDIA R FINAL", "MÉDIA FINAL", "FALTAS", "FALTAS %"
    ]
    _COLUNAS_POR_MATERIA = len(_COLUNAS_NOTAS_RENOMEADAS) # 11
    
    #--------------------------------------------------------------------------

    def __init__(self, planilha_file):
        self.df_raw = pd.read_excel(planilha_file)
        
        # Atributos para armazenar (cache) os dados processados
        self._informacoes_turma = None
        self._dados_processados = None

    # --- Métodos Públicos (Getters) ---

    def get_informacoes_turma(self) -> pd.DataFrame:
        if self._informacoes_turma is None:
            # Se ainda não foi processado, executa a extração
            self._extrair_informacoes_cabecalho()
        return self._informacoes_turma

    def get_dados_processados(self) -> pd.DataFrame:
        """
        Retorna um DataFrame longo (o 'bloco_final') com os dados
        dos alunos, notas por matéria e situação.
        
        Processa os dados apenas na primeira chamada.
        """
        if self._dados_processados is None:
            # Se ainda não foi processado, executa a extração
            self._processar_e_montar_dados_finais()
        return self._dados_processados
    
    # ====================================================================
    # ▼▼▼ COPIE E COLE ESTES DOIS MÉTODOS PARA DENTRO DA SUA CLASSE 'Pandas' ▼▼▼
    # ====================================================================

    def get_dados_alunos(self) -> pd.DataFrame:
        """ Extrai a lista de Alunos (Matrícula, Nome) """
        if not hasattr(self, '_dados_alunos'):
            df_dados_alunos = self.df_raw.iloc[self._LINHA_INICIO_DADOS:, self._SLICE_ALUNOS].reset_index(drop=True)
            df_dados_alunos = df_dados_alunos.dropna()
            df_dados_alunos.columns = ["MATRÍCULA", "NOME"]
            self._dados_alunos = df_dados_alunos
        return self._dados_alunos

    def get_lista_materias(self) -> list:
        """ Extrai a lista de matérias (com tradução de ESPANHOL) """
        if not hasattr(self, '_lista_materias'):
            materias = []
            series_materias = self.df_raw.iloc[self._LINHA_NOMES_MATERIAS, self._SLICE_MATERIAS_NOTAS].reset_index(drop=True)
            series_materias = series_materias.dropna()
            
            for materia in series_materias:
                nome_materia_padronizado = str(materia).strip().upper()
                if nome_materia_padronizado == 'ESPANHOL':
                    materias.append('LÍNGUA ESPANHOLA')
                else:
                    materias.append(materia)
            self._lista_materias = materias
        return self._lista_materias

    # --- Métodos Privados (Lógica de Extração) ---

    def _extrair_informacoes_cabecalho(self):
        """
        Extrai os dados do cabeçalho e os armazena em self._informacoes_turma.
        """
        try:
            # curso, turma e turno > ctt
            df_ctt = self.df_raw.iloc[self._SLICE_CABECALHO_CTT].set_index(
                self._CHAVE_CABECALHO_CTT)[self._VALOR_CABECALHO_CTT]
            
            # campos, ano e serie > cas
            df_cas = self.df_raw.iloc[self._SLICE_CABECALHO_CAS].set_index(
                self._CHAVE_CABECALHO_CAS)[self._VALOR_CABECALHO_CAS]

            # junção
            df_informacoes = pd.concat([df_ctt, df_cas]).to_frame().T
            df_informacoes.columns = self._COLUNAS_CABECALHO_FINAL
            
            self._informacoes_turma = df_informacoes
        except Exception as e:
            raise RuntimeError(f"Erro ao processar o cabeçalho da planilha. Verifique as posições e nomes das colunas. Detalhe: {e}")

    def _processar_e_montar_dados_finais(self):
        """
        Processa o corpo principal da planilha (alunos, notas, matérias)
        e armazena o resultado em self._dados_processados.
        """
        try:
            # 1. Dados alunos
            df_dados_alunos = self.df_raw.iloc[self._LINHA_INICIO_DADOS:, self._SLICE_ALUNOS].reset_index(drop=True)
            df_dados_alunos = df_dados_alunos.dropna()
            df_dados_alunos.columns = ["MATRÍCULA", "NOME"]

            # 2. Situação
            df_situacao = self.df_raw.iloc[self._LINHA_INICIO_DADOS:, self._COLUNA_SITUACAO].reset_index(drop=True)
            df_situacao.name = "SITUAÇÃO"

            # 3. Matérias (com a tradução)
            materias = []
            series_materias = self.df_raw.iloc[self._LINHA_NOMES_MATERIAS, self._SLICE_MATERIAS_NOTAS].reset_index(drop=True)
            series_materias = series_materias.dropna()
            
            for materia in series_materias:
                nome_materia_padronizado = str(materia).strip().upper()
                if nome_materia_padronizado == 'ESPANHOL':
                    materias.append('LÍNGUA ESPANHOLA') # Faz a "tradução"
                else:
                    materias.append(materia) # Adiciona o nome original
            
            # 4. Separando dados (o bloco de notas)
            df_dados_materias = self.df_raw.iloc[self._LINHA_INICIO_DADOS:, self._SLICE_MATERIAS_NOTAS].reset_index(drop=True)

            # 5. Montando os blocos
            blocos = []
            contagem_materia = 0
            
            for i in range(0, df_dados_materias.shape[1], self._COLUNAS_POR_MATERIA):
                # Pega o bloco de colunas da matéria
                inicio_col = i
                fim_col = i + self._COLUNAS_POR_MATERIA
                bloco_notas = df_dados_materias.iloc[:, inicio_col:fim_col].copy()
                
                # Validação
                if len(bloco_notas.columns) != self._COLUNAS_POR_MATERIA:
                    raise ValueError(f"Bloco de matéria incompleto. Esperava {self._COLUNAS_POR_MATERIA} colunas, mas encontrou {len(bloco_notas.columns)}.")
                
                bloco_notas.columns = self._COLUNAS_NOTAS_RENOMEADAS
                
                # Validação
                if contagem_materia >= len(materias):
                    raise ValueError(f"Mais blocos de notas ({contagem_materia+1}) do que matérias ({len(materias)}) encontradas na linha 6.")

                bloco_notas["MATÉRIA"] = materias[contagem_materia]
                contagem_materia += 1

                # Concatena Alunos + Bloco de Notas + Situação
                bloco_completo = pd.concat([
                    df_dados_alunos.reset_index(drop=True),
                    bloco_notas.reset_index(drop=True),
                    df_situacao.reset_index(drop=True)
                ], axis=1)
                
                blocos.append(bloco_completo)

            # 6. Parte final
            self._dados_processados = pd.concat(blocos, axis=0, ignore_index=True)
        
        except Exception as e:
            raise RuntimeError(f"Erro ao processar os dados dos alunos e notas. Verifique se as linhas {self._LINHA_INICIO_DADOS+1} (início) e {self._LINHA_NOMES_MATERIAS+1} (matérias) estão corretas. Detalhe: {e}")