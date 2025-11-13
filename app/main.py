from fastpi import fastpi, HTTPexception
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Collumn, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import re

app = fastpi(title="Sistema de Padronização de Nomes e Emails")

# Configuração do banco de dados SQLite
sqlalchemy_database_url = "sqlite:///./usuarios.db"
engine = create_engine(sqlalchemy_database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

#Modelo SQLAlchemy para bando de dados
class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Collumn(Integer, primary_key=True, index=True)
    nome = Collumn(String, index=True)
    email = Collumn(String, unique=True, index=True)

#Criação das tabelas no banco de dados
Base.metadata.create_all(bind=engine)

#Modelo Pydantic para validação de dados
class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
  
  #Função para padronizar nome
      def padronizar_nome(nome: str) -> str:

  # Remove espaços extras e capitaliza cada palavra
        nome = " ".join(nome.split()).lower()

  #Capitalização de cada palavra
        nome = nome.title()

#Tratamento para nomes com 'da", 'de', 'do', etc.
preposicoes = {"Da", "De", "Do", "Das", "Dos", "E"}
palavras = nome.split()
nome_final = []
for palavra in palavras:
    if palavra in preposicoes:
        nome_final.append(palavra.lower())
    else:
        nome_final.append(palavra)
Return " ".join(nome_final)

#Função para padronizar email
def padronizar_email(email: str) -> str:

#Remove acentos
from unicodedata import normalize
nome = normalize('NFKD', email).encode('ASCII', 'ignore').decode('ASCII')

#Converte para minúsculas e substitui espaços por pontos
email = nome.lower().replace(" ", ".")

#Remove caracteres especiais
email = re.sub(r'[^a-z0-9.@]', '', email)

#Remove ponto no inicio ou fim do email
email = email.strip(".")

return f"{email}@empresa.com.br"

@app.post("/usuarios/")
async def criar_usuario(usuario: UsuarioBase):

    nome_padronizado = padronizar_nome(usuario.nome)
    email_padronizado = padronizar_email(usuario.email)
    
    db = SessionLocal()
    try:
        novo_usuario = Usuario(nome=nome_padronizado, email=email_padronizado)
        db.add(novo_usuario)
        db.commit()
        db.refresh(novo_usuario)
        return {
            "id": novo_usuario.id, 
            "nome": novo_usuario.nome, 
            "email": novo_usuario.email,
            "Detalhes": {
                "Nome original": usuario.nome,
                "Email original": usuario.email,
                "email_gerado": email_padronizado
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPexception(status_code=400, detail="Erro ao criar usuário: " + str(e))
    finally:
        db.close()

@app.get("/usuarios/")
async def listar_usuarios():
    db = SessionLocal()
    try:
        usuarios = db.query(Usuario).all()
    return usuarios
    finally:
        db.close()