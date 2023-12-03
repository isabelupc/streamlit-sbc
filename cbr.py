import pandas as pd

class CBR:
   
    def __init__(self):

        self.books=pd.read_csv('Books.csv',low_memory=False)
        self.cases=pd.read_csv('Cases.csv')
        self.users=pd.read_csv('Users.csv')
       
        
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
            #ultim cop que l'usuari s'ha registrat
            aux = self.cases[self.cases["id_usuari"] == id].tail(1).to_dict(orient='records')[0] 
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
            


        # Usuari nou
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
        # Diccionari amb confirguracio de les columnes: None=no surt, Nom=surt amb aquest nom
        configuracio ={'id_usuari':[None], 'id_llibre':[None],'titol':['Titol'],'escrit_per':['Autor'],'score':['Puntuacio']}
        return llegits,configuracio
   
    # Reguardem el nom si l'usuari el modifica
    def change_user_name(self,id,nom):
        self.users.loc[self.users["id_usuari"]==id,'nom'] = nom
        #self.users.to_csv('Users.csv', encoding='utf-8', index=False)
    
    
    def recomanacions(self,user_id,data):
        #filtre = self.retrieve(lector,data)
        #possibles_llibres = self.reuse(filtre,lector,data)
        


        df = self.books.head(user_id*3).tail(3)
        llista=[]
        for idx,fila in df.iterrows():
            #lectors = fila['num_lectors']
            punts = fila['valoracio']
            # TRAÇA
            llista.append((fila['titol'],fila['escrit_per'],f'la recomanació es per que aquest llibre te una puntuacio mitjana de {punts:.2f}',
                          fila['id_llibre'],user_id))
        return llista

    


    
    ##########################################
    ############## THE FOUR R's ##############
    ##########################################


    def retrieve(self,user,data):
        #retornar node amb els casos similars
        pass

    def reuse(self, filtered_cases, user, data):
        # aplicar funcio de similitud en els casos del node
        # mes aplicar adaptacio
        pass

    def revise(self):
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
        #self.cases.to_csv('Cases.csv', encoding='utf-8', index=False)