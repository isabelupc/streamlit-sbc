import pandas as pd

class CBR:
   
    def __init__(self):
        # Llegim els csv
        self.books=pd.read_csv('Books.csv',low_memory=False)
        self.cases=pd.read_csv('Cases.csv')
        self.users=pd.read_csv('Users.csv')

        # Definim les variables d'atributs
        self.genre_options = ['Històrica', 'Ciencia Ficció', 'Comèdia', 'Ficció', 'Romàntica', 'Fantasia', 'Ciència', 'Creixement personal', 'Policiaca', 'Juvenil']
        self.sex_options=['Dona','Home','Altres']
        self.film_options=['Si','No','Indiferent']
        self.bestseller_options=['Si','No','Indiferent']
        self.saga_options=['Si','No','Indiferent']
        self.reading_options=['Densa','Fluida','Indiferent']
        self.title = 'Recomanador de Llibres 📚'



    ## GETTERS 
    def get_genre_options(self):
        return self.genre_options
    def get_sex_options(self):
        return self.sex_options
    def get_film_options(self):
        return self.film_options
    def get_bestseller_options(self):
        return self.bestseller_options
    def get_saga_options(self):
        return self.saga_options
    def get_reading_options(self):
        return self.reading_options
    
    # Recupera el id maxim assignat a un lector
    def last_user(self):
        return len(self.users)
    
    # Afegim un nou usuari buit
    def add_user(self):
        self.users.loc[self.last_user()] = [self.last_user()+1,'']
  

    # Recupera les dades del user que està utilitzant el recomanador, per mostrarli un formulari per default amb les seves ultimes preferencies
    def user_data(self,id):
        usuari = self.users.loc[self.users['id_usuari'] == id].iloc[0]
        nom=usuari[1]
        data = {}

        # Usuari previament registrat
        try:
            # Ultim cop que l'usuari s'ha registrat
            aux = self.cases[self.cases["id_usuari"] == id].tail(1).to_dict(orient='records')[0] 

            # Recuperem les dades de l'ultim cop que ha utilitzat el recomanador
            data['year'] = aux['any_naixement']
            data['sex'] = self.sex_options.index(aux['genere_persona'])
            generes_defecte = []
            columnes = ['Historica', 'Ciencia_Ficcio', 'Comedia', 'Ficcio', 'Romance', 'Fantasia', 'Ciencia', 'Creixement_personal', 'Policiaca', 'Juvenil']
            for genere, columna in zip(self.genre_options, columnes):
                if aux[columna] == 1:
                    generes_defecte.append(genere)
            data['genre'] = generes_defecte
            data['film'] = self.film_options.index(aux['pref_adaptacio_peli'])
            data['bestseller'] = self.bestseller_options.index(aux['pref_best_seller'])
            data['saga'] = self.saga_options.index(aux['pref_sagues'])
            data['reading'] = self.reading_options.index(aux['pref_tipus_lectura'])
            data['pages'] = aux['pagines_max']
            


        # Si es un usuari nou li posem les següents dades per defecte
        except:
            data['year'] = 2000
            data['sex'] = 0
            data['genre'] = []
            data['film'] = 2
            data['bestseller'] = 2
            data['saga'] = 2
            data['reading'] = 2
            data['pages'] = 1000

        return nom, data
   

    # Recuperem els llibres que s'ha llegit l'usuari
    def read(self,id):
        df = self.cases[self.cases['id_usuari'] == id]
        llegits = pd.merge(df[['id_usuari','score','id_llibre']],self.books[['id_llibre','titol' ,'escrit_per']], on='id_llibre')
        # Per ordenar les columnes
        llegits = llegits[['titol', 'escrit_per', 'score','id_llibre','id_usuari']]
        camps_no_editables =('titol','escrit_per')   
        # Diccionari amb confirguracio de les columnes: None=no surt, Nom=surt amb aquest nom
        configuracio ={'id_usuari':[None], 'id_llibre':[None],'titol':['Titol'],'escrit_per':['Autor'],'score':['Puntuacio']}
        return llegits,camps_no_editables,configuracio
   
    # Re-guardem el nom si l'usuari el modifica
    def change_user_name(self,id,nom):
        self.users.loc[self.users["id_usuari"]==id,'nom'] = nom
        #self.users.to_csv('Users.csv', encoding='utf-8', index=False)
    
    def actualitzar_puntuacions(self,modificats):
        for idx,fila in modificats.iterrows():
            self.cases.loc[(self.cases['id_usuari']==fila['id_usuari']) & (self.cases['id_llibre']==fila['id_llibre']),'score']=fila['score']
    
    def recomanacions(self,user_id,data):
        # Lineas a descomentar un cop estiguin les funcions programades

        #filtre = self.retrieve(lector,data)
        #possibles_llibres = self.reuse(filtre,lector,data)

        # EX SIMULADOR
        df = self.books.head(user_id*3).tail(3) #me'n torna tres qualsevols
        llista=[]
        for idx,fila in df.iterrows():
            lectors = fila['num_lectures']
            punts = fila['valoracio']
            # EX TRAÇA
            llista.append((fila['titol'],fila['escrit_per'],f'La recomanació es perquè aquest llibre té {lectors:.2f} lectors i té una puntuació mitjana de {punts:.2f}',
                          fila['id_llibre'],user_id))
        return llista

    

    ##########################################
    ############## THE FOUR R's ##############
    ##########################################


    def retrieve(self,user,data):
        #data es un diccionari amb tots els atributs que ha marcat l'usuari
        #retornar node amb els casos similars
        pass

    def reuse(self, filtered_cases, user, data):
        # aplicar funcio de similitud en els casos del node
        pass

    def revise(self):
        # aplicar adaptacio (vigilar que l'usuari no s'hagi llegit aquell llibre)
        pass
    
    def retain(self,user,data,book,rate):
        valors=[]
        for columna in self.genre_options:
            if columna in data['genre']:
                valors.append(1)
            else:
                valors.append(0)

        self.cases.loc[len(self.cases)] = [user,book,rate,data['sex'],data['year'],data['film'],data['bestseller'],
                                           data['reading'],data['saga']]+valors+[data['pages']]
        

        valoracio = self.books[self.books['id_llibre'] == book]['valoracio']
        num_lectors = self.books[self.books['id_llibre'] == book]['num_lectures']

        # Calcul nova valoracio mitjana
        nova_valoracio = (valoracio*num_lectors + rate) / (num_lectors+1)

        self.books[self.books['id_llibre'] == book]['valoracio'] = nova_valoracio
        self.books[self.books['id_llibre'] == book]['num_lectures'] = num_lectors + 1


        # Un cop funcioni el recomenador, amb la seguent linea guardarem els casos al csv permanentment i books
        #self.cases.to_csv('Cases.csv', encoding='utf-8', index=False)
        #self.books.to_csv('Books.csv', encoding='utf-8', index=False)
