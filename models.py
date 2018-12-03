import warnings
from sqlalchemy import exc as sa_exc
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    ForeignKey, 
    Date, 
    Float, 
    ForeignKeyConstraint, 
    UniqueConstraint, 
    Enum, 
    Boolean, 
    DateTime, 
    select, 
    Table
)

from sqlalchemy.orm import sessionmaker
from sqlalchemy_repr import PrettyRepresentableBase

DB_CONN_STRING = 'postgres://peoplecounter:peoplecounter@localhost:5432/peoplecounter'

Base = declarative_base(cls=PrettyRepresentableBase)

class Cliente(Base):
    """
    Este entidade diz respeito ao cliente (empresa/organizacao) que contratou nosso servico
    """
    __tablename__ = 'clientes'

    cliente_id = Column(Integer, primary_key=True)
    nome = Column(String(200))

    deleted_on = Column(DateTime)


class Local(Base):
    """
    Local onde o cliente deseja o servico (loja, supermercado, shopping)
    Um cliente pode ter mais de um local onde deseja o nosso servico
    """

    __tablename__ = "locais"

    local_id = Column(Integer, primary_key=True)

    cliente_id = Column(Integer, ForeignKey("clientes.cliente_id"), index=True, nullable=False)

    cep = Column(String(9), index=True)
    endereco = Column(String(200))
    cidade = Column(String(50))
    estado = Column(String(20))

    nome = Column(String(200))

    deleted_on = Column(DateTime)


class Camera(Base):
    """
    Cada local pode ter varias cameras, onde cada uma possui uma contagem diferente
    """

    __tablename__ = "cameras"

    camera_id = Column(Integer, primary_key=True)
    
    local_id = Column(Integer, ForeignKey("locais.local_id"), index=True, nullable=False)
    nome = Column(String(50), index=True)
    
    deleted_on = Column(DateTime)

    
    
class Contagem(Base):
    """
    A contagem acontece em cada camera em um determindao timestamp
    """
    __tablename__ = 'contagem'

    contagem_id = Column(Integer, primary_key=True)

    camera_id = Column(Integer, ForeignKey("cameras.camera_id"), index=True, nullable=False)

    timestamp = Column(DateTime)

    qtd_pessoas_in = Column(Integer)

    qtd_pessoas_out = Column(Integer)
   

class Execucao:

    def execute_db(self):
        engine = create_engine(DB_CONN_STRING, echo=True)

        Base.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        session = Session()

        session.add(
            Cliente(
                cliente_id=1, 
                nome='DB SUPERMERCADOS'
            )
        )
        try:
            session.commit()
        except Exception:
            session.rollback()

        session.add(
            Local(
                local_id=1,
                cliente_id=1,
                nome='DB CIDADE NOVA',
                cep = '69095-000',
                endereco='AV. NOEL NUTELS, 1762 - CIDADE NOVA',
                cidade='MANAUS',
                estado='AMAZONAS',
                
            )
        )
        
        session.add(
            Local(
                local_id=2,
                cliente_id=1,
                nome='DB PARAIBA',
                cep = '69057-021',
                endereco='AV. JORNALISTA HUMBERTO CALDERADO FILHO, 1.128 - ADRIANÓPOLIS',
                cidade='MANAUS',
                estado='AMAZONAS',
                
            )
        )
        try:
            session.commit()
        except Exception:
            session.rollback()

        session.add(
            Camera(
                camera_id=1,
                local_id=1,
                nome='CAMERA ENTRADA 1'
            )
        )

        session.add(
            Camera(
                camera_id=2,
                local_id=1,
                nome='CAMERA ENTRADA 2'
            )
        )

        session.add(
            Camera(
                camera_id=3,
                local_id=2,
                nome='CAM_ENTRADA_1'
            )
        )

        session.add(
            Camera(
                camera_id=4,
                local_id=2,
                nome='CAM_ENTRADA_2'
            )
        )
        try:
            session.commit()
        except Exception:
            session.rollback()

        print("BANCO CRIADO COM SUCESSO")


if __name__ == "__main__":
    
    app = Execucao()
    app.execute_db()
