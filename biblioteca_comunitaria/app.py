import streamlit as st
from sqlalchemy import create_engine, or_, and_
from sqlalchemy.orm import sessionmaker
from models import HEROI_INONIMADO, Base, Livro, Leitor, Emprestimo  # , Ebook
import pandas as pd
import numpy as np
import re
from io import BytesIO
from datetime import datetime

engine = create_engine('sqlite:///estoque.db')
Session = sessionmaker(bind=engine)
session = Session()


class Biblioteca():

    def __init__(self) -> None:

        st.set_page_config(
            page_title="Qualiteca",
            page_icon="📚",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                'Get help': 'mailto:ramilton.silva.lima@live.com',
                'Report a bug': "mailto:ramilton.silva.lima@live.com",
                'About': "Para compartilhar livros"
            }
        )

        st.sidebar.title('Vamos lá!')

        self.secao_home = {
            'Qualiteca': self.home
        }

        self.secao_emprestimos = {
            'Emprestar': self.cadastrar_emprestimo,
            'Devolver': self.terminar_emprestimo,
            'Ver empréstimos': self.ver_emprestimos
        }

        self.secao_leitores = {
            'Leitores: Adicionar': self.cadastrar_leitor,
            'Leitores: Remover': self.remover_leitor,
            'Leitores: Ver': self.ver_leitores,
        }

        self.secao_livros = {
            'Livros: Adicionar': self.cadastrar_livro,
            'Livros: Remover': self.remover_livro,
            'Livros: Ver': self.ver_livros,
            # 'PDF também é livro' : self.ebook
        }

        self.secao_livros = {
            'Livros: Adicionar': self.cadastrar_livro,
            'Livros: Remover': self.remover_livro,
            'Livros: Ver': self.ver_livros,
            # 'PDF também é livro' : self.ebook
            'Backup dos dados' : self.backup_dados
        }

        self.todas_secoes = dict()
        self.todas_secoes.update(self.secao_home)
        self.todas_secoes.update(self.secao_emprestimos)
        self.todas_secoes.update(self.secao_leitores)
        self.todas_secoes.update(self.secao_livros)

        selecao = st.sidebar.radio(
            'Vamos lá', options=list(self.todas_secoes.keys()))

        pagina_selecionada = self.todas_secoes[selecao]
        pagina_selecionada()

    def home(self):
        st.header('Qualiteca')
        st.markdown('''Biblioteca formada com doações de livros do call center para incentivar a leitura de todos. Livros teremos o empréstimo de acordo como tamanho do livro, gibis e revistas ficarão dentro da descompressão para leitura rápida quando estiverem lá.''')

    def __validar_email(self, email):
        regex = re.compile(
            r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

        if re.fullmatch(regex, email):
            return True
        else:
            return False

    def __dataframes(self, consulta):

        df_consulta = pd.DataFrame([item.representacao() for item in consulta])

        if df_consulta.empty:
            st.write('...Na verdade, não há nada aqui ainda.')
        else:
            st.dataframe(df_consulta, hide_index=True)

    def ver_livros(self):
        st.header('Estes são os livros que temos.')
        todos_livros = session.query(Livro).all()
        self.__dataframes(todos_livros)

    def cadastrar_livro(self):
        st.header('Legal! Recebemos mais este!')

        nome = st.text_input('Nome do livro', max_chars=500,
                             help="Coloque o nome completo da obra")
        apoiador_nome = st.text_input(
            'Nome do apoiador', max_chars=200, help="Aquele responsável por esta aquisição")
        apoiador_email = st.text_input(
            'E-mail do apoiador', max_chars=200, help="E-mail dquele responsável por esta aquisição")

        if st.button('Guardar livro'):

            if nome:
                novo_livro = Livro(
                    nome=nome,
                    apoiador_nome=apoiador_nome,
                    apoiador_email=apoiador_email
                )
                session.add(novo_livro)
                session.commit()
                st.success(f'''
                Valeu! {apoiador_nome if apoiador_nome else HEROI_INONIMADO }! 
                "{ nome }" cadastrado com sucesso!
            ''')
            else:
                st.error('Preciso saber o nome do livro')

    def remover_livro(self):
        st.header('Ta bem, vamos tirar o livro da biblioteca')
        livro_id = st.number_input(
            "Qual o ID do livro que deseja remover?", step=0, value=None)

        if not st.button('Remover este livro'):
            pass

        elif not livro_id:
            st.error(f'Preciso saber qual livro quer remover.')

        else:
            livro = session.query(Livro).filter(Livro.id == livro_id).first()
            if not livro:
                st.error(
                    f'Não foi encontrado nenhum livro com o ID {livro_id}.')
            else:
                emprestimos = session.query(Emprestimo).filter(
                    Emprestimo.livro_id == livro_id).all()
                for emprestimo in emprestimos:
                    session.delete(emprestimo)

                session.delete(livro)
                session.commit()

                st.success(
                    f'O livro com ID {livro_id} - "{livro.nome}" e todos os empréstimos vinculados foram removidos com sucesso.')

    def ver_leitores(self):
        st.header('Todos os leitores cadastrados')
        todos_leitores = session.query(Leitor).all()
        self.__dataframes(todos_leitores)

    def cadastrar_leitor(self):
        st.header('Opa! Bem vindo!')

        nome = st.text_input('Nome do Leitor', max_chars=500)
        email = st.text_input('E-mail do Leitor', max_chars=200)

        if st.button('Cadastrar este Leitor'):

            if nome and email and self.__validar_email(email=email):
                novo_leitor = Leitor(
                    nome=nome,
                    email=email
                )
                session.add(novo_leitor)
                session.commit()
                st.success(
                    f'''Show! {nome}({email}) cadastrado com sucesso!''')
            else:
                st.error(
                    'Realmente é necessário saber o nome e o e-mail válido do novo leitor')

    def remover_leitor(self):
        st.header('Que pena...')
        leitor_id = st.number_input(
            "Qual o ID de quem sairá?", step=0, value=None)

        if not st.button('Remover esta pessoa'):
            pass

        elif not leitor_id:
            st.error(f'Preciso saber qual pessoa quer remover.')

        else:
            leitor = session.query(Leitor).filter(
                Leitor.id == leitor_id).first()
            if not leitor:
                st.error(f'Não foi encontrado ninguém com o ID {leitor_id}.')
            else:
                emprestimos = session.query(Emprestimo).filter(
                    Emprestimo.leitor_id == leitor_id).all()
                for emprestimo in emprestimos:
                    session.delete(emprestimo)

                session.delete(leitor)
                session.commit()

                st.success(
                    f'{leitor.nome}({leitor_id}) e todos os empréstimos vinculados foram removidos com sucesso.')

    def ver_emprestimos(self):
        st.header('Livros emprestados.')
        todos_emprestimos = session.query(Emprestimo).all()

        emprestimos = pd.DataFrame([item.representacao()
                                   for item in todos_emprestimos])

        if emprestimos.empty:
            st.write('Ops. Na verdade, nada aqui ainda.')
        else:
            mostrar_devolvido = st.checkbox('Mostar somente pendentes')
            emprestimos['Atrasado'] = emprestimos['Devolver em'].apply(lambda x: x < datetime.now().date())
            if not mostrar_devolvido:
                st.dataframe(emprestimos, hide_index=True)
            else:
                somente_pendentes = emprestimos[emprestimos['Devolvido'] == False].copy()
                st.dataframe(somente_pendentes, hide_index=True)

    def cadastrar_emprestimo(self):
        st.header('Boa! Mas atenção no prazo.')

        livros_sem_emprestimo = session.query(Livro).outerjoin(Emprestimo).group_by(Livro).having(or_(Emprestimo.id == None, and_(Emprestimo.terminado == True))).all()

        leitores = session.query(Leitor)

        if not livros_sem_emprestimo:
            st.error('Ainda não temos livros')
        elif not leitores:
            st.error('Ainda não há quem ler')

        else:
            livro = st.selectbox('Qual livro?', livros_sem_emprestimo)
            devolver_em = st.date_input(
                'Vai devolver em?', min_value=datetime.today())
            leitor = st.selectbox('Quem?', leitores)

            if st.button("Pegar emprestado"):

                if not livro or not leitor or not devolver_em:
                    st.error("Vamos lá, é simples, Qual? Quando? Quem?")

                else:
                    novo_emprestimo = Emprestimo(
                        leitor_id=leitor.id,
                        livro_id=livro.id,
                        data_inicio=datetime.now().date(),
                        data_fim=devolver_em
                    )
                    session.add(novo_emprestimo)
                    session.commit()
                    st.success(f'Pronto! o "{livro.nome}" foi emprestado para {leitor}, de {datetime.now().date()} até {devolver_em}')


    def terminar_emprestimo(self):
        st.header('Obrigado! Parabéns! Volte sempre.')
        emprestimo_id = st.number_input(
            "Qual o id do emprestimo?", step=0, value=None)

        if not st.button('Devolver o empréstimo'):
            pass
        elif not emprestimo_id:
            st.error(f'Informe o numero do empréstimo')

        else:
            emprestimo = session.query(Emprestimo).filter(
                Emprestimo.id == emprestimo_id, Emprestimo.terminado == False).first()
            if not emprestimo:
                st.error(
                    f'Não foi possivel encontrar nenhum emprestimo em aberto com este id')
            else:
                emprestimo.terminado = True
                emprestimo.data_fim = datetime.now().date()
                session.commit()
                st.success(f'Obrigado! Devolvido com sucesso')

    def backup_dados(self):
        st.header('Baixe os dados da Biblioteca, quem sabe precise...')

        todos_livros = session.query(Livro).all()
        todos_leitores = session.query(Leitor).all()
        todos_emprestimos = session.query(Emprestimo).all()

        def gerar_botao(consulta, nome_arquivo):
            buffer = BytesIO()
            dados = [item.backup() for item in consulta]
            df = pd.DataFrame(dados)
            if not df.empty:
                df.to_csv(buffer, index=False, encoding='utf-8-sig', sep=';')

                st.download_button(
                    label=nome_arquivo,
                    data=buffer,
                    file_name=f'{nome_arquivo}.csv',
                )

        gerar_botao(todos_livros, 'Livros')
        gerar_botao(todos_leitores, 'Leitores')
        gerar_botao(todos_emprestimos, 'Emprestimos')



biblioteca = Biblioteca()
