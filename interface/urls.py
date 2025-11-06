from django.urls import path
from .views import (
    Inicio, Sobre,
    AlunoListView, AlunoDetailView,
    TurmaListView, TurmaDetailView,
    CursoDetailView
)

urlpatterns = [
    path('', Inicio.as_view(), name= 'inicio'),
    path('sobre/', Sobre.as_view(), name= 'sobre'),
    path('alunos/', AlunoListView.as_view(), name= 'aluno_list'),
    path('alunos/<str:pk>/', AlunoDetailView.as_view(), name='aluno_detail'),
    path('turmas/', TurmaListView.as_view(), name= 'turma_list'),
    path('turmas/str:<id>/int:<ano>/', TurmaDetailView.as_view(), name= 'turma_detail'),
    path('cursos/<int:pk>/', CursoDetailView.as_view(), name='curso_detail')
]