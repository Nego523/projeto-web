from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView, TemplateView
from importacao.models import Aluno, Turma, Curso


class Inicio(TemplateView):
    template_name= 'interface/inicio.html'

class Sobre(TemplateView):
    template_name = 'interface/sobre.html'

class AlunoListView(ListView):
    model = Aluno
    template_name = 'interface/aluno_list.html'
    context_object_name = 'alunos'
    paginate_by = 14

class AlunoDetailView(DetailView):
    model = Aluno
    template_name = 'interface/aluno_detail.html'
    context_object_name =  'aluno'

class TurmaListView(ListView):
    model = Turma
    template_name = 'interface/turma_list.html'
    context_object_name = 'turmas'
    
class TurmaDetailView(DetailView):
    model = Turma
    template_name = 'interface/turma_detail.html'
    context_object_name = 'turma'

    def get_object(self):
        id = self.kwargs.get('id')
        ano = self.kwargs.get('ano')
        return get_object_or_404(Turma, id=id, ano=ano)
    
class CursoDetailView(DetailView):
    model = Curso
    template_name = 'interface/curso_detail.html'
    context_object_name = 'curso'
