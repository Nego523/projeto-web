from django.core.management.base import BaseCommand
from importacao.models import AreaDoConhecimento, Curso, Disciplina, Serie, Turno
from django.db import transaction

class Command(BaseCommand):
    help = "CADASTRA DADOS DAS SEGUINTES ENTIDADES: AREA DO CONHECIMENTO, CURSO, DISCIPLINA, SÉRIE E TURNO."

    def cadastrar(self, model, dados, nome_model):
        for id_, descricao in dados.items():
            obj, criado = model.objects.get_or_create(
                id = id_,
                defaults={"descricao" : descricao}
            )
            self.stdout.write(self.style.SUCCESS(f"• {obj} cadastrado em {nome_model}."))
        self.stdout.write(self.style.SUCCESS(f"O cadastro do [{nome_model}] foi concluido."))

    @transaction.atomic
    def handle(self, *args, **options):
        area_do_conhecimento = {
            1 : "Área Técnica",
            2 : "Ciências da Natureza",
            3 : "Ciências Humanas",
            4 : "Matemática",
            5 : "Linguagens"
        }

        serie = {
            1 : "1° Ano",
            2 : "2° Ano",
            3 : "3° Ano"
        }

        turno = {
            1 : "Matutino",
            2 : "Vespertino",
            3 : "Noturno",
            4 : "Integral"
        }

        curso = {
            1 : "Edificações",
            2 : "Eletrotécnica",
            3 : "Informática",
            4 : "Segurança do Trabalho"
        }

        disciplinas = [
            #   GERAIS
            {"id" : 1, "sigla" : 'ARTES', "descricao" : 'ARTES', "horas" : (80, 66.7), "area_conhecimento" : 5},
            {"id" : 2, "sigla" : 'BIO', "descricao" : 'BIOLOGIA', "horas" : (200, 166.7), "area_conhecimento" : 2},
            {"id" : 3, "sigla" : 'EF', "descricao" : 'EDUCAÇÃO FÍSICA', "horas" : (160, 133.3), "area_conhecimento" : 5},
            {"id" : 4, "sigla" : 'FIL', "descricao" : 'FILOSOFIA', "horas" : (120, 100), "area_conhecimento" : 3},
            {"id" : 5, "sigla" : 'FIS', "descricao" : 'FÍSICA', "horas" : (240, 200), "area_conhecimento" : 2},
            {"id" : 6, "sigla" : 'GEO', "descricao" : 'GEOGRAFIA', "horas" : (200, 166.7), "area_conhecimento" : 3},
            {"id" : 7, "sigla" : 'HIS', "descricao" : 'HISTÓRIA', "horas" : (200, 166.7), "area_conhecimento" : 3},
            {"id" : 8, "sigla" : 'ESP', "descricao" : 'LÍNGUA ESPANHOLA', "horas" : (80, 66.7), "area_conhecimento" : 5},
            {"id" : 9, "sigla" : 'ING', "descricao" : 'LÍNGUA INGLESA', "horas" : (160, 133.3), "area_conhecimento" : 5},
            {"id" : 10, "sigla" : 'POR', "descricao" : 'LÍNGUA PORTUGUESA', "horas" : (320, 266.7), "area_conhecimento" : 5},
            {"id" : 11, "sigla" : 'MAT', "descricao" : 'MATEMÁTICA', "horas" : (320, 266.7), "area_conhecimento" : 4},
            {"id" : 12, "sigla" : 'QUI', "descricao" : 'QUÍMICA', "horas" : (240, 200), "area_conhecimento" : 2},
            {"id" : 13, "sigla" : 'SOC', "descricao" : 'SOCIOLOGIA', "horas" : (120, 100), "area_conhecimento" : 3},

            #   INTEGRADOR EDIF & ELETRO
            {"id" : 41, "sigla" : 'GOST', "descricao" : 'GESTÃO ORGANIZACIONAL E SEGURANÇA DO TRABALHO', "horas" : (80, 66.7), "area_conhecimento" : 1},

            #   EDIFICAÇÕES
            {"id" : 14, "sigla" : 'DARQ', "descricao" : 'DESENHO ARQUITETÔNICO', "horas" : (120, 100), "area_conhecimento" : 1},
            {"id" : 15, "sigla" : 'DEAC', "descricao" : 'DESENHO ASSISTIDO POR COMPUTADOR', "horas" : (80, 66.7), "area_conhecimento" : 1},
            {"id" : 16, "sigla" : 'ELES', "descricao" : 'ELEMENTOS ESTRUTURAIS', "horas" : (80, 66.7), "area_conhecimento" : 1},
            {"id" : 17, "sigla" : 'ESTC', "descricao" : 'ESTABILIDADE DAS CONTRUÇÕES', "horas" : (80, 66.7), "area_conhecimento" : 1},
            {"id" : 18, "sigla" : 'IHDS', "descricao" : 'INSTALAÇÕES HIDROSSANITÁRIAS', "horas" : (120, 100), "area_conhecimento" : 1},
            {"id" : 19, "sigla" : 'MTCO', "descricao" : 'MATERIAIS DE CONSTRUÇÃO', "horas" : (120, 100), "area_conhecimento" : 1},
            {"id" : 20, "sigla" : 'MSOL', "descricao" : 'MECÂNICA DOS SOLOS', "horas" : (120, 100), "area_conhecimento" : 1},
            {"id" : 21, "sigla" : 'PLAO', "descricao" : 'PLANEJAMENTO DE OBRAS', "horas" : (80, 66.7), "area_conhecimento" : 1},
            {"id" : 22, "sigla" : 'PARQ', "descricao" : 'PROJETO ARQUITETÔNICO', "horas" : (80, 66.7), "area_conhecimento" : 1},
            {"id" : 23, "sigla" : 'PIEP', "descricao" : 'PROJETO DE INSTALAÇÕES ELÉTRICAS PREDIAIS', "horas" : (80, 66.7), "area_conhecimento" : 1},
            {"id" : 24, "sigla" : 'SICO', "descricao" : 'SISTEMAS CONSTRUTIVOS', "horas" : (120, 100), "area_conhecimento" : 1},
            {"id" : 25, "sigla" : 'TOPO', "descricao" : 'TOPOGRAFIA', "horas" : (80, 66.7), "area_conhecimento" : 1},
            {"id" : 26, "sigla" : 'INFO', "descricao" : 'INFORMÁTICA', "horas" : (80, 66.7), "area_conhecimento" : 1}, #INTEGRADOR EDIF

            #   ELETROTÉCNICA
            {"id" : 27, "sigla" : 'ACEL', "descricao" : 'ACIONAMENTOS ELÉTRICOS', "horas" : (120, 100), "area_conhecimento" : 1},
            {"id" : 28, "sigla" : 'AUIN', "descricao" : 'AUTOMAÇÃO INDUSTRIAL', "horas" : (80, 66.7), "area_conhecimento" : 1},
            {"id" : 29, "sigla" : 'DEEL', "descricao" : 'DISTRIBUIÃO DE ENERGIA ELÉTRICA', "horas" : (80, 66.7), "area_conhecimento" : 1},
            {"id" : 30, "sigla" : 'EBIN', "descricao" : 'ELETRÔNICA BÁSICA E INDUSTRIAL', "horas" : (80, 66.7), "area_conhecimento" : 1},
            {"id" : 31, "sigla" : 'ELET', "descricao" : 'ELETRICIDADE', "horas" : (120, 100), "area_conhecimento" : 1},
            {"id" : 32, "sigla" : 'GEFE', "descricao" : 'GERAÇÃO E EFICIÊNCIA ENERGÉTICA', "horas" : (80, 66.7), "area_conhecimento" : 1},
            {"id" : 33, "sigla" : 'INEL', "descricao" : 'INSTALAÇÕES ELÉTRICAS', "horas" : (80, 66.7), "area_conhecimento" : 1},
            {"id" : 34, "sigla" : 'MANE', "descricao" : 'MANUTENÇÃO ELÉTRICA', "horas" : (80, 66.7), "area_conhecimento" : 1},
            {"id" : 35, "sigla" : 'MAEL', "descricao" : 'MÁQUINAS ELÉTRICAS', "horas" : (80, 66.7), "area_conhecimento" : 1},
            {"id" : 36, "sigla" : 'PRIN', "descricao" : 'PROJETOS ELÉTRICOS INDUSTRIAIS', "horas" : (120, 100), "area_conhecimento" : 1},
            {"id" : 37, "sigla" : 'PREP', "descricao" : 'PROJETOS ELÉTRICOS PREDIAIS', "horas" : (120, 100), "area_conhecimento" : 1},
            {"id" : 38, "sigla" : 'LAEL', "descricao" : 'LABORATÓRIO DE ELETRICIDADE', "horas" : (120, 100), "area_conhecimento" : 1}, #INTEGRADOR ELETRO
            {"id" : 39, "sigla" : 'INFOAE', "descricao" : 'INFORMÁTICA APLICADA : ELETRO', "horas" : (120, 100), "area_conhecimento" : 1}, #INTEGRADOR ELETRO
            {"id" : 40, "sigla" : 'DEST', "descricao" : 'DESENHO TÉCNICO', "horas" : (80, 66.7), "area_conhecimento" : 1}, #INTEGRADOR ELETRO
            
            #   INFORMÁTICA
            {"id" : 42, "sigla" : 'EMD', "descricao" : 'EMPREENDEDORISMO DIGITAL', "horas" : (80, 66.7), "area_conhecimento" : 1}, #INTEGRADOR INFO
            {"id" : 43, "sigla" : 'FIN', "descricao" : 'FUNDAMENTOS DA INFORMÁTICA', "horas" : (80, 66.7), "area_conhecimento" : 1}, #INTEGRADOR INFO
            {"id" : 44, "sigla" : 'MMC', "descricao" : 'MONTAGEM E MANUTENÇÃO DE COMPUTADORES', "horas" : (80, 66.7), "area_conhecimento" : 1}, #INTEGRADOR INFO
            {"id" : 45, "sigla" : 'SETRI', "descricao" : 'SEGURANÇA DO TRABALHO : INTEGRADOR', "horas" : (40, 33.3), "area_conhecimento" : 1}, #INTEGRADOR INFO
            {"id" : 46, "sigla" : 'BD', "descricao" : 'BANCO DE DADOS', "horas" : (120, 100), "area_conhecimento" : 1},
            {"id" : 47, "sigla" : 'ES', "descricao" : 'ENGENHARIA DE SOFTWARE', "horas" : (120, 100), "area_conhecimento" : 1},
            {"id" : 48, "sigla" : 'ISRD', "descricao" : 'INFRAESTRUTURA E SERVIÇOS DE REDES', "horas" : (160, 133.3), "area_conhecimento" : 1},
            {"id" : 49, "sigla" : 'IP', "descricao" : 'INTRODUÇÃO A PROGRAMAÇÃO', "horas" : (160, 133.3), "area_conhecimento" : 1},
            {"id" : 50, "sigla" : 'IRC', "descricao" : 'INTRODUÇÃO À REDE DE COMPUTADORES', "horas" : (80, 66.7), "area_conhecimento" : 1},
            {"id" : 51, "sigla" : 'PM', "descricao" : 'PROGRAMAÇÃO MÓVEL', "horas" : (120, 100), "area_conhecimento" : 1},
            {"id" : 52, "sigla" : 'POO', "descricao" : 'PROGRAMAÇÃO ORIENTADA A OBJETOS', "horas" : (160, 133.3), "area_conhecimento" : 1},
            {"id" : 53, "sigla" : 'PWEB', "descricao" : 'PROGRAMAÇÃO WEB', "horas" : (160, 133.3), "area_conhecimento" : 1},
            {"id" : 54, "sigla" : 'SO', "descricao" : 'SISTEMAS OPERACIONAIS', "horas" : (80, 66.7), "area_conhecimento" : 1},

            #   SEGURANÇA
            {"id" : 55, "sigla" : 'ELTI', "descricao" : 'ELABORAÇÃO DO TRABALHO INTELECTUAL', "horas" : (80, 66.7), "area_conhecimento" : 1}, #INTEGRADOR
            {"id" : 56, "sigla" : 'DTAT', "descricao" : 'DESENHO TÉCNICO APLICADO E SUAS TECNOLOGIAS', "horas" : (120, 100), "area_conhecimento" : 1}, #INTEGRADOR
            {"id" : 57, "sigla" : 'INFOAS', "descricao" : 'INFORMÁTICA APLICADA : SEGURANÇA', "horas" : (80, 66.7), "area_conhecimento" : 1}, #INTEGRADOR
            {"id" : 58, "sigla" : 'ERGO', "descricao" : 'ERGONOMIA FÍSICA, COGNITIVA E ORGANIZACIONAL', "horas" : (120, 100), "area_conhecimento" : 1},
            {"id" : 59, "sigla" : 'ESAP', "descricao" : 'ESTATÍSTICA APLICADA', "horas" : (80, 66.7), "area_conhecimento" : 1},
            {"id" : 60, "sigla" : 'GERI', "descricao" : 'GERÊNCIA DE RISCOS', "horas" : (80, 66.7), "area_conhecimento" : 1},
            {"id" : 61, "sigla" : 'HGTR', "descricao" : 'HIGIENE DO TRABALHO', "horas" : (120, 100), "area_conhecimento" : 1},
            {"id" : 62, "sigla" : 'LEST', "descricao" : 'LEGISLAÇÃO EM SEGURANÇA DO TRABALHO', "horas" : (120, 100), "area_conhecimento" : 1},
            {"id" : 63, "sigla" : 'MTPS', "descricao" : 'MÉTODOS E TÉCNICAS DE PRIMEIROS SOCORROS', "horas" : (80, 66.7), "area_conhecimento" : 1},
            {"id" : 64, "sigla" : 'PSST', "descricao" : 'PROGRAMAS DE SAÚDE E SEGURANÇA DO TRABALHO', "horas" : (120, 100), "area_conhecimento" : 1},
            {"id" : 65, "sigla" : 'PPCI', "descricao" : 'PROJETOS DE PREVENÇÃO E COMBATE A INCÊNDIO E PÂNICO', "horas" : (120, 100), "area_conhecimento" : 1},
            {"id" : 66, "sigla" : 'SAOC', "descricao" : 'SÁUDE OCUPACIONAL', "horas" : (80, 66.7), "area_conhecimento" : 1},
            {"id" : 67, "sigla" : 'SETR', "descricao" : 'SEGURANÇA DO TRABALHO', "horas" : (120, 100), "area_conhecimento" : 1},
            {"id" : 68, "sigla" : 'SIGE', "descricao" : 'SISTEMAS INTEGRADOS DE GESTÃO', "horas" : (80, 66.7), "area_conhecimento" : 1},
            {"id" : 69, "sigla" : 'TEPI', "descricao" : 'TECNOLOGIAS E PROCESSOS INDUSTRIAIS', "horas" : (120, 100), "area_conhecimento" : 1}
        ]
        
        self.cadastrar(AreaDoConhecimento, area_do_conhecimento, "Área do Conhecimento")
        self.cadastrar(Serie, serie, "Série")
        self.cadastrar(Turno, turno, "Turno")
        self.cadastrar(Curso, curso, "Curso")

        for disciplina in disciplinas:
            obj, criado = Disciplina.objects.get_or_create(
                id = disciplina["id"],
                defaults={
                    "sigla" : disciplina["sigla"],
                    "descricao" : disciplina["descricao"],
                    "horas" : disciplina["horas"][0],
                    "area_do_conhecimento_id" : disciplina["area_conhecimento"]
                }
            )
            self.stdout.write(self.style.SUCCESS(f"• {obj} cadastrado em Disciplina."))
        self.stdout.write(self.style.SUCCESS("O cadastro da [Disciplina] foi concluido."))