import streamlit as st
from streamlit_option_menu import option_menu
from models import Livro, Usuario, Emprestimo, session
import pandas as pd

from collections import namedtuple

Aba = namedtuple('Aba',field_names=['nome_aba', 'titulo_aba'])

class PaginaBase:
    __nome = None
    navegavel = True
    __todas_subclasse = dict()
    navegaveis = dict()
    paginas = []

    nomes_abas = []
    


    @classmethod
    @property
    def nome(cls):
        if cls.__nome is not None:
            return cls.__nome
        else: 
            cls.__nome = cls.__name__
            return cls.__nome
        

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.navegavel:
            PaginaBase.navegaveis[cls.nome] = cls
            PaginaBase.paginas.append(cls.nome)
        PaginaBase.__todas_subclasse[cls.nome] = cls

    def __init__(self) -> None:
        st.header(self.nome,divider='orange')


class Home(PaginaBase):
    def __init__(self) -> None:
        super().__init__()



class Estante(PaginaBase):
    nome = 'Estande de Livros'
    nomes_abas = ['Ver','Adicionar', 'Editar', 'Excluir']
    

    def __init__(self) -> None:
        super().__init__()
        
        abas = st.tabs(self.nomes_abas)

        with abas[0]:
            st.write('d')
            st.dataframe(self.ver_estante())

        with abas[1]:
            self.adicionar_livro()

    def ver_estante(self):
        dados = Livro.em_dataframe()
        return dados
    
    def adicionar_livro(self):

        coluna1, coluna2 = st.columns(2)
        with coluna1:
            foto_ou_imagem = st.radio('Vamos pegar uma imagem do livro.', options=['Carregar imagem','Abrir camera'])
            
            if foto_ou_imagem == 'Carregar imagem':
                imagem_livro = st.file_uploader('Imagem do livro', type=[])
            else:
                foto_livro = st.camera_input('Adicione uma foto do livro')
            
        with coluna2:
            nome_livro = st.text_input('Qual nome do livro?')
            st.caption('Caso o doador não esteja na lista, cadastre-o antes, na seção de "Pessoas"')
            doador = st.selectbox('Quem está doando?', options=['Ninguem'])
            prazo_emprestimo = st.number_input('Quantos dias será o emprestimo do livro', min_value=1)





class Pessoas(PaginaBase):
    def __init__(self) -> None:
        super().__init__()


class Empréstimos(PaginaBase):
    def __init__(self) -> None:
        super().__init__()


class Dados(PaginaBase):
    nome = 'Gestão dos dados'

    def __init__(self) -> None:
        super().__init__()
        st.button('teste')





class Biblioteca:
    def __init__(self) -> None:
        self.menu()


    def menu(self):
        with st.sidebar:
            destino = option_menu(
                menu_title="Vamos lá!",
                menu_icon="cast",
                default_index=0,
                orientation="vertical",
                options=PaginaBase.paginas,
                styles={
                    "container": {"background-color": "transparent"}
                }
            )
        PaginaBase.navegaveis[destino]()


Biblioteca()
    # menu_icon="cast", default_index=0, orientation="horizontal",
    # styles={
    #     "container": {"padding": "0!important", "background-color": "#fafafa"},
    #     "icon": {"color": "orange", "font-size": "25px"}, 
    #     "nav-link": {"font-size": "25px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
    #     "nav-link-selected": {"background-color": "green"},
    # }