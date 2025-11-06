from django.http import HttpResponse
import pandas as pd
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from datetime import datetime
from .forms import TurmaCompletaImportForm, PERIODO_CHOICES
from importacao.PandasClass import Pandas
from .models import (
    Turma, Aluno, AlunoTurma, Disciplina, Boletim, Curso, Serie, Turno, DisciplinaCursoSerie
)

@transaction.atomic
def importar_turma(request):

    """
    View para upload e importação de planilha de notas (mapa).
    Estrutura: 'novo código' (forms, messages, GET/POST)
    Lógica: 'código antigo' (extração do cabeçalho, validação, 
    criação de turma baseada na planilha)
    """
    
    # --- Parte 1: Lógica GET (do 'novo código') ---
    # Comentário: Se o usuário apenas visitar a página, 
    # exibe o formulário vazio.
    if request.method != 'POST':
        form = TurmaCompletaImportForm()
        # O template 'interface/upload.html' é do seu 'novo código'
        return render(request, 'interface/upload.html', {'form': form})

    # --- Parte 2: Lógica POST (Início do 'novo código') ---
    # Comentário: Se o usuário enviou o formulário, 
    # processa os dados e o arquivo.
    form = TurmaCompletaImportForm(request.POST, request.FILES)
    if form.is_valid():
        cleaned_data = form.cleaned_data
        
        # Comentário: Dados vindos do formulário
        planilha = cleaned_data['planilha']
        periodo = cleaned_data['periodo_importacao']

        try:
            # --- Parte 3: Processamento Pandas (Usando a Classe) ---
            # Comentário: Substituímos a lógica pandas do 'novo código'
            # pela classe que encapsula a lógica do 'código antigo'.
            pandas = Pandas(planilha)
            df_informacoes = pandas.get_informacoes_turma()
            bloco_final = pandas.get_dados_processados()
            
            # Comentário: Pegamos os dados separados para usar na 
            # lógica de cadastro (exatamente como no 'código antigo')
            df_dados_alunos = pandas.get_dados_alunos()
            materias = pandas.get_lista_materias()
            
            
            # --- Parte 4: Validação (Lógica do 'código antigo') ---
            # Comentário: Extraindo dados do cabeçalho para validar
            string_curso = df_informacoes["CURSO"].iloc[0]
            string_turma = df_informacoes["TURMA"].iloc[0]
            string_turno = df_informacoes["TURNO"].iloc[0]
            string_ano = df_informacoes["ANO"].iloc[0]
            string_serie = df_informacoes["SÉRIE"].iloc[0]

            # Comentário: Usando suas funções helper para consultar o BD
            curso_obj = consultar_curso(string_curso)
            serie_obj = consultar_serie(string_serie)
            turno_obj = consultar_turno(string_turma)
            ano_validado = getAno(string_ano)
            
            # Comentário: Bloco de validação do 'código antigo', mas
            # usando 'raise Exception' para ser pego pelo 'try/except'
            # e exibido como uma 'message' (padrão do 'novo código').
            if not curso_obj:
                raise Exception(f"ERRO: O curso '{string_curso}' da planilha não foi encontrado no banco de dados.")
            
            if not serie_obj:
                raise Exception(f"ERRO: A série '{string_serie}' da planilha não foi encontrada no banco de dados.")
            
            if not turno_obj:
                raise Exception(f"ERRO: O turno '{string_turno}' da planilha não foi encontrado no banco de dados.")
            
            if not ano_validado:
                raise Exception(f"ERRO: O Ano '{string_ano}' da planilha não foi reconhecido como um ano válido.")
            
            
            # --- Parte 5: Cadastro de Alunos e Disciplinas (Lógica do 'código antigo') ---
            
            # Comentário: Cadastro de alunos do 'código antigo'
            for _, row in df_dados_alunos.iterrows():
                aluno_obj, criado = Aluno.objects.get_or_create(
                    matricula = str(int(row["MATRÍCULA"])), # Convertido para int e str
                    defaults={ "nome": row["NOME"] }
                )

            # Comentário: Cadastro disciplina_curso_serie do 'código antigo'
            for disciplina in materias:
                disciplina_obj = consultar_disciplina(disciplina)
                if disciplina_obj:
                    disciplina_curso_serie_obj, criado = DisciplinaCursoSerie.objects.get_or_create(
                        disciplina = disciplina_obj,
                        curso = curso_obj,
                        serie = serie_obj
                    )
                else:
                    # Comentário: É bom avisar no log do servidor
                    print(f"AVISO: A disciplina '{disciplina}' da planilha foi ignorada porque não está cadastrada no bd.")


            # --- Parte 6: Cadastro da Turma (Lógica do 'código antigo') ---
            # Comentário: Lógica de geração do ID da Turma
            codigo_curso = {
                "TÉCNICO EM INFORMÁTICA": '5', 
                "TÉCNICO EM ELETROTÉCNICA": '4', 
                "TÉCNICO EM EDIFICAÇÕES": '2', 
                "TÉCNICO EM SEGURANÇA DO TRABALHO": 'S'
            }
            
            primeiro_char = None
            for nome_curso, codigo in codigo_curso.items():
                if curso_obj.descricao.upper() in nome_curso:
                    primeiro_char = str(codigo)
                    break
            
            if primeiro_char is None:
                raise Exception(f"ERRO: Não foi possível determinar o código para o curso '{curso_obj.descricao}'.")

            segundo_char = str(turno_obj.id)
            terceiro_char = str(serie_obj.id)

            descricao_turma = f"{primeiro_char}{segundo_char}{terceiro_char}"
            descricao_turma_anterior = f"{primeiro_char}{segundo_char}{int(terceiro_char) - 1}"

            defaults = {
                "descricao" : descricao_turma,
                "curso" : curso_obj,
                "serie" : serie_obj,
                "turno" : turno_obj
            }

            # Comentário: Tentativa de buscar turma anterior
            if descricao_turma_anterior and serie_obj.id > 1: # Só busca se não for 1a série
                try:
                    turma_anterior_obj = Turma.objects.get(
                        id = descricao_turma_anterior,
                        ano = ano_validado # Assume que a turma anterior é do mesmo ano
                        # Se a turma anterior for do ano ANTERIOR, mude para:
                        # ano = ano_validado - 1 
                    )
                    defaults["turma_id"] = turma_anterior_obj.id
                    defaults["turma_ano"] = turma_anterior_obj.ano
                except Turma.DoesNotExist:
                    print(f"AVISO: A turma anterior '{descricao_turma_anterior}' não foi encontrada.")

            # Comentário: Criação/Atualização da Turma (LÓGICA EXISTENTE)
            nova_turma, turma_criada = Turma.objects.update_or_create(
                id = descricao_turma, 
                ano = ano_validado,
                defaults= defaults
            )

            # --- [NOVO] INÍCIO: Verificação Retroativa ---
            # Comentário: Esta é a lógica que você pediu.
            # Agora que esta turma (ex: 1º ano) foi criada,
            # vamos verificar se a turma do ano SEGUINTE (ex: 2º ano)
            # já existe no banco e está "esperando" por esta.
            
            try:
                # 1. Calcula o ID da turma "filha" (próxima série)
                #    Usa as mesmas variáveis de ID (primeiro_char, segundo_char...)
                id_turma_seguinte = f"{primeiro_char}{segundo_char}{int(terceiro_char) + 1}"
                
                # 2. Busca pela turma "filha" no mesmo ano
                turma_seguinte_obj = Turma.objects.get(
                    id = id_turma_seguinte,
                    ano = ano_validado,
                    turma_id__isnull=True  # 3. Importante: Só pega se ela NÃO tiver um link ainda
                )

                # 4. Se encontrou, atualiza o link dela para apontar para a turma
                #    que acabamos de criar ('nova_turma')
                turma_seguinte_obj.turma_id = nova_turma.id
                turma_seguinte_obj.turma_ano = nova_turma.ano
                turma_seguinte_obj.save()
                
                # (Opcional) Log para o console do servidor
                print(f"AVISO: Turma '{turma_seguinte_obj.id}' ({turma_seguinte_obj.ano}) atualizada retroativamente para se vincular à '{nova_turma.id}'.")

            except Turma.DoesNotExist:
                # Isso é normal e esperado. Significa que a turma "filha" (ex: 2º ano)
                # ainda não foi importada, ou ela já tem um link. Nada a fazer.
                pass
            except Exception as e:
                # Captura outros erros (ex: falha no 'int(terceiro_char) + 1')
                print(f"AVISO: Falha na verificação retroativa de turma: {e}")
            
            # --- [NOVO] FIM: Verificação Retroativa ---

            # --- Parte 7: Mapeamento e Cadastro de Boletins (LÓGICA EXISTENTE) ---
            # Comentário: Esta seção é do 'novo código'. Ela é crucial 
            # para que o 'periodo_importacao' do formulário funcione.
            
            
            campos_por_periodo = {
                'B1': ['bimestre1'], 'B2': ['bimestre1', 'bimestre2'], 'R1': ['bimestre1', 'bimestre2', 'recusem1'],
                'B3': ['bimestre1', 'bimestre2', 'recusem1', 'bimestre3'],
                'B4': ['bimestre1', 'bimestre2', 'recusem1', 'bimestre3', 'bimestre4'],
                'R2': ['bimestre1', 'bimestre2', 'recusem1', 'bimestre3', 'bimestre4', 'recusem2'],
                'RF': ['bimestre1', 'bimestre2', 'recusem1', 'bimestre3', 'bimestre4', 'recusem2', 'recfinal'],
                'COMPLETO': ['bimestre1', 'bimestre2', 'recusem1', 'bimestre3', 'bimestre4', 'recusem2', 'recfinal', 'final', 'faltas', 'faltaspercent', 'status']
            }
            campos_fixos_parcial = ['faltas', 'faltaspercent', 'status']
            
            # Comentário: Mapa adaptado para as colunas do 'bloco_final' 
            # (que vêm do seu 'código antigo')
            mapa_planilha_modelo = {
                'B1': 'bimestre1', 'B2': 'bimestre2', 'R1': 'recusem1', 
                'B3': 'bimestre3', 'B4': 'bimestre4', 'R2': 'recusem2',
                'MÉDIA R FINAL': 'recfinal', 'MÉDIA FINAL': 'final', 
                'FALTAS': 'faltas', 'FALTAS %': 'faltaspercent', 
                'SITUAÇÃO': 'status'
            }
            
            campos_a_atualizar = campos_por_periodo.get(periodo).copy()
            if periodo != 'COMPLETO':
                campos_a_atualizar.extend(campos_fixos_parcial)

            # Comentário: Função 'to_decimal' do 'novo código'
            def to_decimal(value):
                if pd.isna(value): return None
                try: return Decimal(str(value).replace(',', '.'))
                except InvalidOperation: return None

            
            # --- Parte 8: Loop Principal (Fusão 'novo' e 'antigo') ---
            # Comentário: Este loop salva AlunoTurma e Boletim.
            # A estrutura é do 'novo código', mas usa objetos 
            # ('nova_turma', 'disciplina_obj') definidos pela 
            # lógica do 'código antigo'.
            
            for index, row in bloco_final.iterrows():
                # 1. Garante o Aluno (já feito, mas 'aluno_obj' é necessário)
                try:
                    aluno_obj = Aluno.objects.get(matricula=str(int(row['MATRÍCULA'])))
                except Aluno.DoesNotExist:
                    print(f"AVISO: Aluno {row['MATRÍCULA']} do 'bloco_final' não foi encontrado no passo de criação.")
                    continue
                
                # 2. Cadastro AlunoTurma (lógica correta do 'novo código')
                AlunoTurma.objects.get_or_create(
                    aluno_matricula=aluno_obj, 
                    turma_id=nova_turma.id, 
                    turma_ano=nova_turma.ano
                )
                
                # 3. Busca Disciplina (usando a função do 'código antigo')
                disciplina_obj = consultar_disciplina(row['MATÉRIA'])
                if not disciplina_obj:
                    continue # Pula esta linha do boletim

                # 4. Constrói o dicionário de dados (lógica do 'novo código')
                dados_para_atualizar = {}
                for nome_planilha, nome_modelo in mapa_planilha_modelo.items():
                    
                    if nome_modelo in campos_a_atualizar:
                        valor = row.get(nome_planilha)
                        
                        if nome_modelo == 'status':
                            if periodo != 'COMPLETO':
                                dados_para_atualizar['status'] = "MATRICULADO"
                            else:
                                dados_para_atualizar['status'] = row.get('SITUAÇÃO')
                        else:
                            dados_para_atualizar[nome_modelo] = to_decimal(valor)
                print(f"Salvando: [Aluno: {aluno_obj.nome}, Disciplina: {disciplina_obj.descricao}] -> DADOS: {dados_para_atualizar}")
                # 5. Salva o Boletim (lógica 'update_or_create' do 'novo código')
                
                Boletim.objects.update_or_create(
                    aluno_matricula=aluno_obj,
                    disciplina=disciplina_obj,
                    turma_id=nova_turma.id,
                    turma_ano=nova_turma.ano,
                    defaults=dados_para_atualizar.copy()
                )
                

            # --- Parte 9: Sucesso (Lógica do 'novo código') ---
            # Comentário: Mensagem de sucesso para o usuário
            nome_periodo = dict(PERIODO_CHOICES).get(periodo)
            if turma_criada:
                messages.success(request, f"Turma '{nova_turma.descricao} ({nova_turma.ano})' criada com sucesso! Dados importados até: {nome_periodo}.")
            else:
                messages.success(request, f"Turma '{nova_turma.descricao} ({nova_turma.ano})' atualizada com sucesso! Dados importados até: {nome_periodo}.")
            
            # Recria o formulário vazio e renderiza a página
            form = TurmaCompletaImportForm()
            return render(request, 'interface/upload.html', {'form': form})

        except Exception as e:
            # --- Parte 10: Erro (Lógica do 'novo código') ---
            # Comentário: Captura qualquer erro (das validações ou do BD) 
            # e exibe para o usuário.
            messages.error(request, f"Ocorreu um erro crítico durante a importação: {e}")
            return render(request, 'interface/upload.html', {'form': form})

    # --- Parte 11: Formulário Inválido (Lógica do 'novo código') ---
    return render(request, 'interface/upload.html', {'form': form})


def consultar_disciplina(string_disciplina):
    string_disciplina = string_disciplina.strip().upper()
    return Disciplina.objects.filter(descricao__iexact=string_disciplina).first()

'''def consultar_disciplina(string_disciplina):
    disciplinas = Disciplina.objects.all()
    string_disciplina = string_disciplina.upper()
    for disciplina in disciplinas:
        if disciplina.descricao.upper() in string_disciplina:
            return (disciplina)
    return(None)'''


def consultar_curso(string_curso):
    cursos = Curso.objects.all()
    string_curso = string_curso.upper()
    for curso in cursos:
        if  curso.descricao.upper() in string_curso:
            return (curso)
    return(None)


def consultar_turno(string_turno):
    turnos = Turno.objects.all()
    string_turno = string_turno.upper()
    for turno in turnos:
        if turno.descricao.upper() in string_turno:
            return (turno)
    return(None)


def consultar_serie(string_serie):
    string_serie = string_serie.upper()
    series = Serie.objects.all()
    for serie in series:
        if serie.descricao.upper() in string_serie:
            return (serie)
    return(None)


def getAno(string_ano):
    try:
        ano_atual = datetime.now().year
        ano_planilha = int(str(string_ano)[:4])
    except (ValueError, TypeError):
        return None
    
    if (ano_atual >= ano_planilha >= 2000):
        return(ano_planilha)
    
    return(None)
