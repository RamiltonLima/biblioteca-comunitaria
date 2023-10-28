from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date, LargeBinary, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

HEROI_INONIMADO = "Herói Inonimado"

Base = declarative_base()

class Leitor(Base):
    __tablename__ = 'leitores'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    emprestimos = relationship('Emprestimo', back_populates='leitor')

    # TODO: Registrar quem e quando cadastrou este leitor

    def representacao(self):
        return {'ID': self.id, 'Nome': self.nome, 'E-mail': self.email}
    
    def __str__(self):
        return f'({self.id}) {self.nome}'

class Livro(Base):
    __tablename__ = 'livros'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    apoiador_nome = Column(String)
    apoiador_email = Column(String)
    emprestimos = relationship('Emprestimo', back_populates='livro')
    
    # TODO: Registrar quem e quando guardou cada livro

    def representacao(self):

        apoiador_nome = self.apoiador_nome if self.apoiador_nome else HEROI_INONIMADO

        return {
            'ID': self.id,
            'Nome': self.nome,
            'Nome do Apoiador': apoiador_nome,
            'E-mail do Apoiador': self.apoiador_email
        }

    
    def __str__(self):
        return f'({self.id}) {self.nome}'

        



class Emprestimo(Base):
    __tablename__ = 'emprestimos'
    id = Column(Integer, primary_key=True)
    leitor_id = Column(Integer, ForeignKey('leitores.id'), nullable=False)
    livro_id = Column(Integer, ForeignKey('livros.id'), nullable=False)
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    terminado = Column(Boolean, nullable=False, default=False)

    leitor = relationship('Leitor', back_populates='emprestimos')
    livro = relationship('Livro', back_populates='emprestimos')

    def representacao(self):
        return {
            'ID': self.id,
            'Leitor': f'{self.leitor.nome}({self.leitor_id})',  
            'Livro': f'{self.livro.nome}{(self.livro_id)}',
            'Retirada em': self.data_inicio,
            'Devolver em': self.data_fim,
            'Devolvido' : self.terminado
        }


# class Ebook(Base):
#     __tablename__ = 'ebooks'
#     id = Column(Integer, primary_key=True)
#     nome = Column(String, nullable=False)
#     conteudo = Column(LargeBinary, nullable=False)

#     def __repr__(self):
#         return f"<Ebook(titulo='{self.titulo}')>"
    

#     def representacao(self):
#         return {
#             'ID': self.id,
#             'Nome': self.nome,
#         }
    


engine = create_engine('sqlite:///estoque.db')
Base.metadata.create_all(engine)
