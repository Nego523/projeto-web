from django import forms
from .models import Curso, Serie, Turno, Turma # Importações do 'novo código'

# ========================================================================
# EXPLICAÇÃO (PERIODO_CHOICES):
# 
# Esta é a lista de opções que o usuário verá no dropdown.
# É crucial que as "chaves" (o valor da esquerda, ex: 'B1', 'COMPLETO')
# sejam EXATAMENTE as mesmas chaves usadas no dicionário 'campos_por_periodo'
# da sua 'views.py'. O valor da direita (ex: '1º Bimestre') é 
# apenas o texto amigável que o usuário vê.
# ========================================================================
PERIODO_CHOICES = [
    ('B1', '1º Bimestre'),
    ('B2', '2º Bimestre'),
    ('R1', 'Recuperação 1º Semestre'),
    ('B3', '3º Bimestre'),
    ('B4', '4º Bimestre'),
    ('R2', 'Recuperação 2º Semestre'),
    ('RF', 'Recuperação Final'),
    ('COMPLETO', 'Completo (com Status Final)'),
]

class TurmaCompletaImportForm(forms.Form):
    """
    Este formulário define os campos que o usuário preencherá 
    na tela de upload.
    """
    
    # ====================================================================
    # EXPLICAÇÃO (planilha):
    #
    # forms.FileField() cria o campo de upload de arquivo.
    # A 'view' acessa este arquivo via 'cleaned_data['planilha']'.
    # ====================================================================
    planilha = forms.FileField(
        label="Planilha de Importação (.xlsx)",
        help_text="Selecione o arquivo Excel no formato de mapa de notas."
    )
    
    # ====================================================================
    # EXPLICAÇÃO (periodo_importacao):
    #
    # forms.ChoiceField() cria um campo <select> (dropdown).
    # - 'choices=PERIODO_CHOICES': Diz ao campo para usar a lista acima.
    # - 'initial='COMPLETO'': Define "Completo" como a opção padrão.
    # A 'view' acessa o valor escolhido via 'cleaned_data['periodo_importacao']'.
    # ====================================================================
    periodo_importacao = forms.ChoiceField(
        choices=PERIODO_CHOICES,
        label="Importar dados até o período:",
        help_text="Define quais colunas da planilha serão lidas e atualizadas.",
        initial='COMPLETO'
    )

    # ====================================================================
    # EXPLICAÇÃO (__init__):
    #
    # Este método é opcional, mas muito útil.
    # Ele adiciona classes de CSS (do Bootstrap) automaticamente
    # a todos os campos do formulário. Isso faz com que o formulário
    # já venha estilizado no HTML, sem precisarmos de 
    # {{ field.css_classes }} no template.
    # 'form-control' é para campos de texto/arquivo.
    # 'form-select' é para campos <select> (dropdown).
    # ====================================================================
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            
            # Define a classe padrão
            css_class = 'form-control' 
            
            # Se for um ChoiceField (dropdown), usa 'form-select'
            if isinstance(field, forms.ChoiceField):
                css_class = 'form-select'
                
            field.widget.attrs['class'] = css_class