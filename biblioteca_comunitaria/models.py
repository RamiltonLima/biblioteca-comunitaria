from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date, DateTime, LargeBinary, Boolean, Enum
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import pandas as pd

engine = create_engine('sqlite:///biblioteca.db')
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class ModeloBase(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    registrado_em = Column(DateTime, nullable=False, default=datetime.now)
    ultima_edicao_em = Column(DateTime, nullable=True)
    modificado = Column(Boolean, nullable=False, default=False)
    excluido_em = Column(DateTime, nullable=True)
    excluido = Column(Boolean, nullable=False, default=False)

    @classmethod
    def retornar(cls, campo='id', valor=None, unico_registro=True, session=session):
        filtro = True if valor is None else getattr(cls, campo) == valor
        if unico_registro is None:
            return session.query(cls).filter(filtro, (not cls.excluido)).first()
        else:
            return session.query(cls).filter(filtro, (not cls.excluido)).all()

    @classmethod
    def editar(cls, campo='id', valor=None, campo_edicao=None, novo_valor=None, unico_registro=True, session=session):
         
        objeto = cls.retornar(campo=campo, valor=valor, unico_registro=unico_registro, session=session)

        if not objeto:
            return None
        elif isinstance(objeto, list):
            editando = objeto
        else:
            editando = [objeto]
            setattr(objeto, campo, novo_valor)

        editados = []
        for item in editando:
            setattr(item, campo_edicao, novo_valor)
            setattr(item, 'ultima_edicao_em', datetime.now())
            setattr(item, 'modificado', True)
            session.commit()
            editados.append(item)

        return editados
        
    @classmethod
    def excluir(cls, campo='id', valor=None, unico_registro=True, session=session):
        cls.editar(
            campo=campo,
            valor=valor,
            campo_edicao='excluido_em',
            novo_valor=datetime.now(),
            unico_registro=unico_registro,
            session=session
        )

        cls.editar(
            campo=campo,
            valor=valor,
            campo_edicao='excluido_por',
            unico_registro=unico_registro,
            session=session
        )
        
        return cls.editar(
            campo=campo,
            valor=valor,
            campo_edicao='excluido',
            novo_valor=True,
            unico_registro=unico_registro,
            session=session
        )

    @classmethod
    def em_dataframe(cls, campo=None, valor=None, session=session):
        
        objetos = cls.retornar(campo=campo, valor=valor, unico_registro=False, session=session)

        objetos_dict = [objeto.em_dict() for objeto in objetos]
        df = pd.DataFrame(objetos_dict)

        return pd.DataFrame(objetos_dict)

    

    def em_dict(self):
        objeto_dict = {}
        for attr, value in self.__dict__.items():
            objeto_dict[attr] = value
        return objeto_dict

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"


class Usuario(ModeloBase):
    __tablename__ = 'usuarios'

    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    emprestimos = relationship('Emprestimo', back_populates='leitor')
    doacao = relationship('Livro', back_populates='doador')   


class Livro(ModeloBase):
    __tablename__ = 'livros'
    tempo_emprestimo_padrao = lambda : 1

    titulo = Column(String, nullable=False)
    doador_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    foto_capa = Column(LargeBinary, nullable=False)
    extensao_foto_capa = Column(String, nullable=False)
    tempo_emprestimo = Column(Integer, nullable=False, default=tempo_emprestimo_padrao)

    doador = relationship('Usuario', back_populates='doacao')
    emprestimos = relationship('Emprestimo', back_populates='livro')

    


class Emprestimo(ModeloBase):
    __tablename__ = 'emprestimos'

    leitor_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    livro_id = Column(Integer, ForeignKey('livros.id'), nullable=False)
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    terminado = Column(Boolean, nullable=False, default=False)

    leitor = relationship('Usuario', back_populates='emprestimos')
    livro = relationship('Livro', back_populates='emprestimos')

Base.metadata.create_all(engine)
