import datetime
import json

from flask import Flask, jsonify, request, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_mail import Mail, Message

####### APP CONFIG (APP, DB, MAIL) #######
from sqlalchemy import func, engine

import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
cors = CORS(app)
#DEVELOPMENT DATABASE
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/is2flask'
#DEPLOYMENT DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://equipo9:brsqlg@localhost/equipo9'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'surveycadocl@gmail.com'
app.config['MAIL_PASSWORD'] = 'atlldekvrqynwapr'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)

####### MODELOS Y SCHEMAS #######
Tag_encuesta = db.Table('Tag_encuesta', #TABLA MANY TO MANY QUE RELACIONA A ENCUESTADO CON ENCUESTA
    db.Column('tag', db.String(30), db.ForeignKey('tag.tag')),
    db.Column('id_encuesta', db.Integer, db.ForeignKey('encuesta.id_encuesta'))
)

Contesta_encuesta = db.Table('Contesta_encuesta',  #TABLA MANY TO MANY QUE RELACIONA A ENCUESTADO CON ENCUESTA
    db.Column('correo_encuestado', db.String(40), db.ForeignKey('encuestado.correo_encuestado')),
    db.Column('id_encuesta', db.Integer, db.ForeignKey('encuesta.id_encuesta')),
    db.Column('fecha_contestacion', db.String(30), default=datetime.datetime.now().date())
)

class Encuestado(db.Model):  # CLASE ENCUESTADO
    correo_encuestado = db.Column(db.String(40), primary_key=True)
    hash_encuestado = db.Column(db.String(40))
    suscrito = db.Column(db.Boolean, default=True)
    tiempo_resuscripcion = db.Column(db.Integer, default=0)
    encuestas = db.relationship('Encuesta', secondary=Contesta_encuesta, backref=db.backref('Encuestados_backref'),
                                lazy='dynamic')

    def __init__(self, correo_encuestado, hash_encuestado, suscrito, tiempo_resuscripcion):
        self.correo_encuestado = correo_encuestado
        self.hash_encuestado = hash_encuestado
        self.suscrito = suscrito
        self.tiempo_resuscripcion = tiempo_resuscripcion



class Tag(db.Model): #CLASE TAG
    id_tag = db.Column(db.Integer, unique=True)
    tag = db.Column(db.String(30), primary_key=True)
    encuestas = db.relationship('Encuesta', secondary=Tag_encuesta, backref=db.backref('Tags_backref'), lazy = 'dynamic')

    def __init__(self, tag):
        self.tag = tag


class Editor(db.Model): #CLASE EDITOR
    id_editor = db.Column(db.Integer, primary_key=True)
    username_editor = db.Column(db.String(30), unique=True)
    correo_editor = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(30))
    encuestas = db.relationship('Encuesta', backref='editor')

    def __init__(self, id_editor, username_editor, correo_editor, password):
        self.id_editor = id_editor
        self.username_editor = username_editor
        self.correo_editor = correo_editor
        self.password = password


class Pregunta(db.Model):  # CLASE PREGUNTA
    id_pregunta = db.Column(db.Integer, primary_key=True)
    id_encuesta = db.Column(db.Integer, db.ForeignKey('encuesta.id_encuesta'))
    enunciado_pregunta = db.Column(db.String(200))
    alternativas = db.relationship('Alternativa', backref='pregunta')

    def __init__(self, id_pregunta, id_encuesta, enunciado_pregunta):
        self.id_pregunta = id_pregunta
        self.id_encuesta = id_encuesta
        self.enunciado_pregunta = enunciado_pregunta


class Alternativa(db.Model): #CLASE ALTERNATIVA
    id_alternativa = db.Column(db.Integer, primary_key=True)
    id_pregunta = db.Column(db.Integer, db.ForeignKey('pregunta.id_pregunta'))
    enunciado_alternativa = db.Column(db.String(200))
    contador = db.Column(db.Integer)

    def __init__(self, id_alternativa, id_pregunta, enunciado_alternativa, contador):
        self.id_alternativa = id_alternativa
        self.id_pregunta = id_pregunta
        self.enunciado_alternativa = enunciado_alternativa
        self.contador = contador


class Encuesta(db.Model): #CLASE ENCUESTA
    id_encuesta = db.Column(db.Integer, primary_key=True)
    id_editor = db.Column(db.Integer, db.ForeignKey('editor.id_editor'))
    titulo_encuesta = db.Column(db.String(200))
    descripcion_encuesta = db.Column(db.String(200))
    fecha_creacion = db.Column(db.String(30))
    encuestados = db.relationship('Encuestado', secondary=Contesta_encuesta, backref=db.backref('encuestas_backref'), lazy = 'dynamic')
    tags = db.relationship('Tag', secondary=Tag_encuesta, backref=db.backref('encuestas_backref'), lazy='dynamic')
    preguntas = db.relationship('Pregunta', backref='encuesta')

    def __init__(self, id_encuesta, id_editor, titulo_encuesta, descripcion_encuesta, fecha_creacion):
        self.id_encuesta = id_encuesta
        self.id_editor = id_editor
        self.titulo_encuesta = titulo_encuesta
        self.descripcion_encuesta= descripcion_encuesta
        self.fecha_creacion = fecha_creacion


db.create_all()


class EditorSchema(ma.Schema):
    class Meta:
        fields = ('id_editor', 'username_editor', 'correo_editor', 'password')

editor_schema = EditorSchema()
editor_schema = EditorSchema(many=True)


class TagSchema(ma.Schema):
    class Meta:
        fields = ('id_tag', 'tag')

tag_schema = TagSchema()
tags_schema = TagSchema(many=True, only=['tag'])


class EncuestadoSchema(ma.Schema):
    class Meta:
        #attribute = 'correo_encuestado'
        fields = ('correo_encuestado','suscrito')

encuestado_schema = EncuestadoSchema()
encuestados_schema = EncuestadoSchema(many=True)

class EncuestaSchema(ma.Schema):
    class Meta:
        fields = ('id_encuesta', 'id_editor', 'titulo_encuesta', 'descripcion_encuesta', 'fecha_creacion')

encuesta_schema = EncuestaSchema()
encuesta_schema = EncuestaSchema(many=True)


class PreguntaSchema(ma.Schema):
    class Meta:
        fields = ('id_pregunta', 'id_encuesta', 'enunciado_pregunta')

pregunta_schema = PreguntaSchema()
pregunta_schema = PreguntaSchema(many=True)


class AlternativaSchema(ma.Schema):
    class Meta:
        fields = ('id_alternativa', 'id_pregunta', 'enunciado_alternativa', 'contador')

alternativa_schema = AlternativaSchema()
alternativa_schema = AlternativaSchema(many=True)


####### RUTAS #######

###ENCUESTADO###
@app.route("/saveRespuestas", methods=['PUT'])
def saveRespuestas():
    data = request.get_json()
    for datos in data['dict']:
        for [key,value] in datos.items():
            if(key == 'idEnc'):
                id = value
            elif(key == 'corrEnc') :
                correo = value

    exists = db.session.query(db.exists().where(Encuestado.correo_encuestado == correo)).scalar()
    encuesta = db.session.query(Encuesta).filter(Encuesta.id_encuesta == id).first()
    if exists is False:  # si es un correo nuevo, se añade
        #hash_encuestado = ''
        while True:
            print('hola')
            hash_encuestado = str(hash(correo))  # da valores aleatorios, por eso se usa while
            if '-' in hash_encuestado:
                hash_encuestado = hash_encuestado[1:]
            exists = db.session.query(db.exists().where(Encuestado.hash_encuestado == hash_encuestado)).scalar()
            if exists is False:
                break
        print(hash_encuestado)
        encuestado = Encuestado(correo_encuestado=correo,
                                hash_encuestado=hash_encuestado,
                                suscrito=True,
                                tiempo_resuscripcion=0)
        # encuestado.encuestas.append(encuesta)
        db.session.add(encuestado)
        db.session.commit()
    encuestado = db.session.query(Encuestado).filter(Encuestado.correo_encuestado == correo).first()
    contestada = False
    for enc in encuestado.encuestas:
        if(enc.id_encuesta == id):
            contestada = True
    if contestada is True:
        return Response("Ya ha contestado esta encuesta", status=400)
    else:
        db.engine.execute(Contesta_encuesta.insert(), correo_encuestado=correo, id_encuesta=id, fecha_contestacion=datetime.datetime.now())

    #actualiza los contadores de alternativas
    for alts in data['dict']:
        for [key,value] in alts.items():
            if(key == 'idAlt'):
                alt = Alternativa.query.get(value)
                alt.contador = alt.contador+1

    db.session.commit()
    return Response("Contestada correctamente", status=200)


###EDITOR###
@app.route("/login",methods=['GET','POST'])
def login():
    data = request.get_json()
    correo=data['correo']
    password=data['password']
    if request.method=='POST':
        existe = db.session.query(exists().where(Editor.correo_editor == correo)).scalar()
        if existe:
            editor = db.session.query(Editor).where(Editor.correo_editor == correo)
            editorDump = editor_schema.dump(editor)
            for data in editorDump:
                for [key, value] in data.items():
                    if(key == 'password'):
                        password_editor = value
                    elif(key == 'correo_editor'):
                        mail_editor = value
                    elif(key == 'id_editor'):
                        id_Editor = value
            if password_editor == password:
                return jsonify([id_Editor, mail_editor, password_editor])
            else:
                return 'Correo o contraseña incorrectos'
        else:
            return 'Correo o contraseña incorrectos'


@app.route("/signup", methods=['POST'])
def signup():
#def signup(username,correo,password):
    if request.method == 'POST':
        data = request.get_json()
        username=data['username']
        correo = data['correo']
        password = data['password']
        exists_u = db.session.query(db.exists().where(Editor.username_editor == username)).scalar()
        if exists_u is True:
            return 'Nombre ya registrado'
        exists_c = db.session.query(db.exists().where(Editor.correo_editor==correo)).scalar()
        if exists_c is True:
            return 'Correo ya registrado'
        if db.session.query(func.max(Editor.id_editor)).scalar() == None:
            id_editor = 1
        else:
            id_editor = db.session.query(func.max(Editor.id_editor)).scalar() + 1
        editor = Editor(id_editor=id_editor,correo_editor=correo,username_editor=username,password=password)
        db.session.add(editor)
        db.session.commit()
        return 'Registrado exitosamente'

@app.route("/unsuscribe/<int:hash_encuestado>",methods=['GET','POST'])
def unsuscribe(hash_encuestado):
    if request.method=='POST':
        print(hash_encuestado)
        encuestado = db.session.query(Encuestado).filter_by(hash_encuestado = str(hash_encuestado)).first()
        if encuestado is not None:
            tiempo_resuscripcion=request.get_json()
            if tiempo_resuscripcion["tiempo_resuscripcion"] == "semana":
                encuestado.tiempo_resuscripcion= 7
            elif tiempo_resuscripcion["tiempo_resuscripcion"] == "mes":
                encuestado.tiempo_resuscripcion = 30
            elif tiempo_resuscripcion["tiempo_resuscripcion"] == "año":
                encuestado.tiempo_resuscripcion = 365
            if tiempo_resuscripcion["tiempo_resuscripcion"] == "permanente":
                encuestado.tiempo_resuscripcion = -1
            encuestado.suscrito = False
            db.session.add(encuestado)
            db.session.commit()
            #envia correo de confirmacion
            with mail.connect() as conn:
                #DEVELOPMENT
                #suslink="http://localhost:3000/resuscribe/"+encuestado.hash_encuestado
                #DEPLOYMENT
                suslink = "http://152.74.52.191:3000/resuscribe/" + encuestado.hash_encuestado
                msg=Message('Cancelación de suscripción', sender=("Surveycado 🥑",'surveycadocl@gmail.com'),recipients=[''.join(encuestado.correo_encuestado)])
                msg.body="Se ha desuscrito exitosamente.\nSi desea volver a suscribirse, haga click en el siguiente link "+suslink
                mail.send(msg)
            print(tiempo_resuscripcion)
            return 'Desuscrito exitosamente'
        else:
            return 'Usuario no existe'


@app.route("/resuscribe/<int:hash_encuestado>",methods=['GET'])
def resuscribe(hash_encuestado): #por alguna razon backend llama 2 veces
    encuestado = db.session.query(Encuestado).filter_by(hash_encuestado = str(hash_encuestado)).first()
    print(encuestado)
    if encuestado is not None and encuestado.suscrito is False:
        encuestado.suscrito = True
        encuestado.tiempo_resuscripcion = 0
        db.session.add(encuestado)
        db.session.commit()
        #envia correo de confirmacion
        with mail.connect() as conn:
            msg=Message('Suscripción exitosa', sender=("Surveycado 🥑",'surveycadocl@gmail.com'),recipients=[''.join(encuestado.correo_encuestado)])
            msg.body="Se ha suscrito exitosamente."
            mail.send(msg)
        return 'Suscrito exitosamente'
    elif encuestado.suscrito is True:
        return 'Usuario ya está suscrito'
    else:
        return 'Usuario no existe'

@app.route("/getUser/<idEd>", methods=['GET'])
def getUser(idEd):
    editor = db.session.query(Editor).where(Editor.id_editor == idEd)
    result = editor_schema.dump(editor)
    return jsonify(result)

@app.route("/getTags",methods=['GET'])
def getTags():
    tags = db.session.query(Tag).all()
    result = tags_schema.dump(tags)
    return jsonify(result)

@app.route("/editEncuesta/<idE>", methods=["POST"])
def editEncuesta(idE):
    #DELETE ENCUESTA
    result = deleteEncuesta(idE)

    #CREA UNA NUEVA ENCUESTA CON EL MISMO ID
    # Extraigo el JSON de la request
    abc = request.get_json()
    data = json.dumps(abc['dict'])
    data = json.loads(data)
    # Se obtienen los id máximos de las encuestas, preguntas y alternativas
    id_encuesta = idE

    if db.session.query(func.max(Pregunta.id_pregunta)).scalar() == None:
        max_id_pregunta = 1
    else:
        max_id_pregunta = db.session.query(func.max(Pregunta.id_pregunta)).scalar() + 1

    if db.session.query(func.max(Alternativa.id_alternativa)).scalar() == None:
        max_id_alternativa = 1
    else:
        max_id_alternativa = db.session.query(func.max(Alternativa.id_alternativa)).scalar() + 1

    # Se extraen los datos de la encuesta
    for element in data:
        for att, value in element.items():
            if att == 'idEditor':
                id_editor = value
            if att == 'titulo_encuesta':
                titulo_encuesta = value
            if att == 'descripcion_encuesta':
                descripcion_encuesta = value
            if att == 'tag_encuesta':
                tag_encuesta = value
            if att == 'preguntas':
                preguntas = value

    # Se crea una nueva encuesta
    fecha_creacion = datetime.datetime.now().date()
    new_encuesta = Encuesta(id_encuesta, id_editor, titulo_encuesta, descripcion_encuesta, fecha_creacion)
    # Se añade el objeto encuesta a la BD
    db.session.add(new_encuesta)
    # Se itera por la preguntas
    for p in preguntas:
        # Se extraen los datos de las preguntas
        for att, value in p.items():
            if att == 'enunciado_pregunta':
                enunciado_pregunta = value
                # Se crea la nueva pregunta y se almacena
                new_pregunta = Pregunta(max_id_pregunta, id_encuesta, enunciado_pregunta)
                db.session.add(new_pregunta)
            if att == 'alternativas':
                alternativas = value
                # Se itera por las alternativas de una pregunta
                for a in alternativas:
                    # Se extraen los datos de las alternativas
                    for att, value in a.items():
                        if att == 'enunciado_alternativa':
                            enunciado_alternativa = value
                            # Se crea la nueva alternativa y se almacena
                            new_alternativa = Alternativa(max_id_alternativa, max_id_pregunta, enunciado_alternativa, 0)
                            db.session.add(new_alternativa)
                            max_id_alternativa += 1
        max_id_pregunta += 1
    # Se guardan los cambios realizados en la BD
    db.session.commit()
    db.engine.execute(Tag_encuesta.insert(), tag=tag_encuesta, id_encuesta=id_encuesta)
    return 'editado'

@app.route("/deleteEncuesta/<idE>", methods=['DELETE'])
def deleteEncuesta(idE):
    pregs = Pregunta.query.filter(Pregunta.id_encuesta == idE)
    for p in pregs:
        Alternativa.query.filter(Alternativa.id_pregunta == p.id_pregunta).delete()
        #alts = Alternativa.query.filter(Alternativa.id_pregunta == p.id_pregunta)
        #    print(a.id_alternativa)
        #    print("***********")
        db.session.delete(p)
    db.session.query(Contesta_encuesta).filter(Contesta_encuesta.c.id_encuesta==idE).delete()
    db.session.commit()
    db.session.query(Tag_encuesta).filter(Tag_encuesta.c.id_encuesta == idE).delete()
    db.session.commit()
    Encuesta.query.filter(Encuesta.id_encuesta == idE).delete()
    db.session.commit()
    return 'eliminada'


@app.route("/listadoEncuestas/<idEditor>", methods=['GET'])
def listaEncuestas(idEditor):
    encuestasEd = db.session.query(Encuesta).where(Encuesta.id_editor == idEditor)
    result = encuesta_schema.dump(encuestasEd)
    return jsonify(result)


@app.route("/showEncuesta/<idEncuesta>", methods=['GET'])
def showEncuesta(idEncuesta):
    if request.method == 'GET':
        encuesta = db.session.query(Encuesta).where(Encuesta.id_encuesta == idEncuesta)
        tag = db.session.query(Tag_encuesta.c.tag).filter(Tag_encuesta.c.id_encuesta == idEncuesta).first()
        preguntas = db.session.query(Pregunta).where(Pregunta.id_encuesta == idEncuesta)
        alternativas = db.session.query(Alternativa).join(Pregunta).where(Alternativa.id_pregunta == Pregunta.id_pregunta and Pregunta.id_encuesta == idEncuesta).all()
        resultE = encuesta_schema.dump(encuesta)
        resultP = pregunta_schema.dump(preguntas)
        resultA = alternativa_schema.dump(alternativas)
        return jsonify(resultE, resultP, resultA, tag[0])


@app.route("/saveEncuesta", methods=['POST'])
def saveEncuesta():
    if request.method == 'POST':
        #Extraigo el JSON de la request
        abc = request.get_json()
        data = json.dumps(abc['dict'])
        data =json.loads(data)
        #Se obtienen los id máximos de las encuestas, preguntas y alternativas
        if db.session.query(func.max(Encuesta.id_encuesta)).scalar() == None:
            id_encuesta = 1
        else:
            id_encuesta = db.session.query(func.max(Encuesta.id_encuesta)).scalar()+1;

        if db.session.query(func.max(Pregunta.id_pregunta)).scalar() == None :
            max_id_pregunta = 1
        else:
            max_id_pregunta = db.session.query(func.max(Pregunta.id_pregunta)).scalar()+1

        if db.session.query(func.max(Alternativa.id_alternativa)).scalar() == None:
            max_id_alternativa = 1
        else:
            max_id_alternativa = db.session.query(func.max(Alternativa.id_alternativa)).scalar()+1

        #Se extraen los datos de la encuesta
        for element in data:
            for att, value in element.items():
                if att == 'idEditor':
                    id_editor = value
                if att == 'titulo_encuesta':
                    titulo_encuesta = value
                if att == 'descripcion_encuesta':
                    descripcion_encuesta = value
                if att == 'tag_encuesta':
                    tag_encuesta = value
                if att == 'preguntas':
                    preguntas = value

        # Se crea una nueva encuesta
        fecha_creacion = datetime.datetime.now().date()
        new_encuesta = Encuesta(id_encuesta, id_editor, titulo_encuesta, descripcion_encuesta, fecha_creacion)
        # Se añade el objeto encuesta a la BD
        db.session.add(new_encuesta)
        #Se itera por la preguntas
        for p in preguntas:
            # Se extraen los datos de las preguntas
            for att, value in p.items():
                if att == 'enunciado_pregunta':
                    enunciado_pregunta = value
                    # Se crea la nueva pregunta y se almacena
                    new_pregunta = Pregunta(max_id_pregunta, id_encuesta, enunciado_pregunta)
                    db.session.add(new_pregunta)
                if att == 'alternativas':
                    alternativas = value
                    # Se itera por las alternativas de una pregunta
                    for a in alternativas:
                        # Se extraen los datos de las alternativas
                        for att, value in a.items():
                            if att == 'enunciado_alternativa':
                                enunciado_alternativa = value
                                # Se crea la nueva alternativa y se almacena
                                new_alternativa = Alternativa(max_id_alternativa, max_id_pregunta,enunciado_alternativa, 0)
                                db.session.add(new_alternativa)
                                max_id_alternativa += 1
            max_id_pregunta += 1
        #Se guardan los cambios realizados en la BD
        db.session.commit()
        db.engine.execute(Tag_encuesta.insert(), tag=tag_encuesta, id_encuesta=id_encuesta)
        return "creada correctamente"


'''@app.route("/viewCorreos/",methods=['GET','POST']) #POST es para editar correo
def viewCorreos():
    if request.method=='POST': #editar correo
        correo=request.form('correo_encuestado')
        encuestado=Encuestado.query.get_or_404(correo)
        encuestado.correo_encuestado=correo
        db.session.add(encuestado)
        db.session.commit()
    return'''

@app.route("/viewCorreos/",methods=['GET'])
def viewCorreos():
    correos=Encuestado.query.with_entities(Encuestado.correo_encuestado).all()
    correos=[tuple(row)[0] for row in correos]
    #return Response(json.dumps(correos), mimetype='application/json')
    return jsonify(correos)

'''@app.route("/<int:id_encuestado>/ingresarCorreo/",methods=['POST'])
def ingresarCorreo(correo):
    encuestado=Encuestado(correo_encuestado=correo)
    db.session.add(encuestado)
    db.session.commit()
    return redirect(url_for('index')) #cambiar link

@app.route("/<int:id_encuestado>/eliminarCorreo/",methods=['POST'])
def eliminarCorreo(correo): #¿se refiere a eliminar al usuario?
    #tal vez deberia usarse correo como id
    encuestado=Encuestado.query.get_or_404(correo)
    db.session.delete(encuestado)
    db.session.commit()
    return redirect(url_for('index')) #Cambiar link

@app.route("/filtrarCorreo",methods=['GET','POST'])
def filtrarCorreo(tag):
    if request.method=='POST':
        #obtiene lista de correos filtrados
        correos=db_session.query(Encuestado).join(Tag_encuesta).filter(Tag_encuesta.id_tag==tag)
        #enviar a front end la lista de correos filtrados
        return jsonify(correos)
    return render_template('index.html')'''

#@app.post("/<int:id_encuesta>/sendCorreos/")
#def sendCorreos(id_encuesta):
#surveylink="surveycado.com/encuesta/"+string(id_encuesta)
@app.route("/sendCorreos/",methods=['POST']) #envia los correos para una encuesta dada a toda la lista de correos
def sendCorreos():
    id_encuesta = request.get_json()

    #DEVELOPMENT URL
    #surveylink="http://localhost:3000/encuesta/"+str(id_encuesta["idEncuesta"])
    #DEPLOYMENT URL
    surveylink = "http://152.74.52.191:3000/encuesta/" + str(id_encuesta["idEncuesta"])
    titulo=(Encuesta.query.get(id_encuesta["idEncuesta"])).titulo_encuesta
    users=Encuestado.query.filter_by(suscrito = True).with_entities(Encuestado.correo_encuestado).all() #recibir solo correos
    with mail.connect() as conn:
        for user in users:
            encuestado=Encuestado.query.get_or_404(user)
            #DEVELOPMENT URL
            #deletelink="http://localhost:3000/unsuscribe/"+encuestado.hash_encuestado
            #DEPLOYMENT URL
            deletelink="http://152.74.52.191:3000/unsuscribe/"+encuestado.hash_encuestado
            msg=Message('Encuesta Surveycado🥑: '+titulo, sender=("Surveycado 🥑",'surveycadocl@gmail.com'),recipients=[''.join(user)])
            msg.body="Link a encuesta "+surveylink+"\n\nSi desea dejar de recibir estos correos, haga click en el siguiente link "+deletelink
            mail.send(msg)
    return "Mensajes enviados."

@app.route("/listaTags/",methods=['GET'])
def listaTags():
    lista_tags=Tag.query.with_entities(Tag.tag).all()
    lista_tags=[tuple(row)[0] for row in lista_tags]
    return jsonify(lista_tags)

@app.route("/tagsEncuestados/<tag>",methods=['GET'])
def tagsEncuestados(tag):
    result = db.session.execute('''SELECT c.correo_encuestado, t.tag FROM contesta_encuesta 
    AS c INNER JOIN encuesta AS e ON c.id_encuesta = e.id_encuesta JOIN tag_encuesta 
    AS t ON e.id_encuesta = t.id_encuesta 
    WHERE t.tag = :tag''', {"tag": tag})
    correos = list(map(lambda r : r[0], result)) #lambda es f anon, toma cada alemento del arreglo del elemento result
    return jsonify(correos)

#chequea el tiempo de resuscripcion para cada encuestado que haya desactivado la suscripcion
def check_subscription():
    with app.app_context():
        print("check")
        encuestados = db.session.query(Encuestado).where(Encuestado.suscrito == False).all() #no se si funcionara
        #se debe crear el atributo tiempo_resuscripcion, el cual es el tiempo en horas
        for encuestado in encuestados:
            if encuestado.tiempo_resuscripcion > 1:
                encuestado.tiempo_resuscripcion=encuestado.tiempo_resuscripcion-1
            elif encuestado.tiempo_resuscripcion == -1:
                continue
            else:
                encuestado.tiempo_resuscripcion=0
                encuestado.suscrito=True
                with mail.connect() as conn:
                    msg=Message('Suscripción exitosa', sender=("Surveycado 🥑",'surveycadocl@gmail.com'),recipients=[''.join(encuestado.correo_encuestado)])
                    msg.body="Se ha suscrito exitosamente."
                    mail.send(msg)
            db.session.add(encuestado)
        db.session.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(func=check_subscription, trigger="interval", seconds=60) #cada 1 dia
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5009)
