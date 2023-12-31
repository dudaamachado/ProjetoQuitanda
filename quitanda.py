from flask import Flask, render_template, request, redirect, session
import sqlite3 as sql
import uuid

app = Flask(__name__)
app.secret_key = "quitandazezinho"

usuario = "zezinho"
senha = "12345"
login = False

#FUNÇÃO PARA VERIFICAR SESSÃO
def verifica_sessao():
    if "login" in session and session["login"]:
        return True
    else:
        return False
    
#CONEXÃO COM O BANCO DE DADOS
def conecta_database():
    conexao = sql.connect("db_quitanda.db")
    conexao.row_factory = sql.Row
    return conexao

#INICIAR O BANCO DE DADOS
def iniciar_db():
    conexao = conecta_database()
    with app.open_resource('esquema.sql', mode='r') as comandos:
        conexao.cursor().executescript(comandos.read())
    conexao.commit()
    conexao.close()

# ROTA DA PÁGINA INICIAL
@app.route("/")
def index():
    iniciar_db()
    conexao = conecta_database()
    produtos = conexao.execute('SELECT * FROM produtos ORDER BY id_prod DESC').fetchall()
    conexao.close()
    title = "Home"
    return render_template("home.html", produtos=produtos, title=title)

#ADICIONANDO ROTA DA PÁGINA LOGIN
@app.route("/login")
def login():
    title="Login"
    return render_template("login.html", title=title)

# ROTA DA PÁGINA ACESSO
@app.route("/acesso", methods=['post'])
def acesso():
    global usuario, senha
    usuario_informado = request.form["usuario"]
    senha_informada = request.form["senha"]
    if usuario == usuario_informado and senha == senha_informada:
        session["login"] = True
        return redirect('/adm')
    else:
        return render_template("login.html",msg="Usuário/Senha estão incorretos!")

#ROTA DE PÁGINA ADM 
@app.route("/adm")
def adm():
    if verifica_sessao():
        iniciar_db()
        conexao = conecta_database()
        produtos = conexao.execute('SELECT * FROM produtos ORDER BY id_prod DESC').fetchall()
        conexao.close
        title = "Administração"
        return render_template("adm.html", produtos=produtos, title=title)
    else:
        return redirect("/login")
    
#CÓDIGO DE LOGOUT para que o administrador possa sinalizar que já utilizou o sistema e irá sair do modo administrativo.
@app.route("/logout")
def logout():
    global login 
    login = False 
    session.clear()
    return redirect('/')

#ROTA DA PÁGINA DE CADASTRO
@app.route("/cadprodutos")
def cadprodutos():
    if verifica_sessao():
        title = "Cadastro de produtos"
        return render_template("cadastro.html", title=title)
    else:
        return redirect("/login")

#ROTA DA PÁGINA DE CADASTRO NO BANCO 
@app.route("/cadastro",methods=["post"])
def cadastro():
    if verifica_sessao():
        nome_prod=request.form['nome_prod']
        desc_prod=request.form['desc_prod']
        preco_prod=request.form['preco_prod']
        img_prod=request.files['img_prod']
        id_foto=str(uuid.uuid4().hex)
        filename=id_foto+nome_prod+'.png'
        img_prod.save("static/img/produtos/"+filename)
        conexao = conecta_database()
        conexao.execute('INSERT INTO produtos (nome_prod, desc_prod, preco_prod, img_prod) VALUES (?, ?, ?, ?)',(nome_prod, desc_prod, preco_prod, filename))
        conexao.commit()
        conexao.close()
        return redirect("/adm")
    else:
        return redirect("/login")

#ROTA DE EXCLUSÃO
@app.route("/excluir/<id>")
def excluir(id):
    if verifica_sessao():
        id = int(id)
        conexao = conecta_database()
        conexao.execute('DELETE FROM produtos WHERE id_prod = ?',(id,))
        conexao.commit()
        conexao.close()
        return redirect('/adm')
    else:
        return redirect("/login")
    
#CRIAR A ROTA DO EDITAR PRODUTOS rota anterio da edição serve para abrir o produto a ser editado
@app.route("/editprodutos/<id_prod>")
def editar(id_prod):
    if verifica_sessao():
        iniciar_db()
        conexao = conecta_database()
        produtos = conexao.execute('SELECT * FROM produtos WHERE id_prod = ?',(id_prod,)).fetchall()
        conexao.close()
        title = "Edição de Produtos"
        return render_template("editprodutos.html",produtos=produtos,title=title)
    else:
        return redirect("/login")
    
# CRIAR A ROTA PARA TRATAR A EDIÇÃO rpta para salvar aquilo que foi alterado
@app.route("/editarprodutos", methods=['POST'])
def editprod():
    conexao = conecta_database()
    id_prod = request.form['id_prod']
    nome_prod = request.form['nome_prod']
    desc_prod = request.form['desc_prod']
    preco_prod = request.form['preco_prod']
    
    if request.files['img_prod']:
        img_prod = request.files['img_prod']
        id_foto = str(uuid.uuid4().hex)
        filename = id_foto + nome_prod + '.png'
        img_prod.save("static/img/produtos/" + filename)
        conexao.execute('UPDATE produtos SET nome_prod=?, desc_prod=?, preco_prod=?, img_prod=? WHERE id_prod=?',
                        (nome_prod, desc_prod, preco_prod, filename, id_prod))
    else:
        conexao.execute('UPDATE produtos SET nome_prod=?, desc_prod=?, preco_prod=? WHERE id_prod=?',
                        (nome_prod, desc_prod, preco_prod, id_prod))
    conexao.commit()
    conexao.close()
    return redirect('/adm')

#ROTA DA PÁGINA DE BUSCA 
@app.route("/busca",methods=["post"])
def busca():
    busca = request.form['buscar']
    conexao = conecta_database
    produtos = conexao.execute('SELECT * FROM produtos WHERE nome_prod LIKE "%" || ? || "%"', (busca,)).fetchall()
    title = "Home"
    return render_template("home.html",produtos=produtos, title=title)

# FINAL DO CODIGO - EXECUTANDO O SERVIDOR
app.run(debug=True)