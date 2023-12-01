import streamlit as st
import pandas as pd



################ View  ################
def view(model):

    # Inicialització de les variables de sessio
    if 'iniciat' not in st.session_state:
        st.session_state['iniciat']=True
        st.session_state['max_id']=model.darrer_lector()
        st.session_state['primer']=1
        st.session_state['idx_recomanacio']=0
        st.session_state['mostrar_recomanacions']=False
        st.session_state['ha_comprat']=False

    # Funcions auxiliars i callbacks   
    def treure_recomanacions():
            st.session_state['mostrar_recomanacions']=False
            st.session_state['idx_recomanacio']=0

    def nou_call():  
        model.afegir_lector()
        st.session_state['primer'] = model.darrer_lector()
        st.session_state['max_id'] = st.session_state['primer']
        treure_recomanacions()

    def comprar_call(idx):
        model.afegir_rating(st.session_state['recomanacions'][idx][3],st.session_state['recomanacions'][idx][4])
        st.session_state['ha_comprat']=True

    def calcula_index_recomanacions():
        maxim = len(st.session_state['recomanacions'])
        if st.session_state['ha_comprat']:
            idx1 = st.session_state['idx_recomanacio']-3
            if idx1<0:
                idx1 += maxim
        else: 
            idx1 = st.session_state['idx_recomanacio']
        idx2 = idx1+1
        if idx2 >= maxim:
            idx2 = idx2%maxim
        idx3 = idx2+1
        if idx3 >= maxim:
            idx3 = idx3%maxim
        nou = idx3+1
        if nou >= maxim:
            nou = nou%maxim
        st.session_state['idx_recomanacio']=nou
        st.session_state['ha_comprat']=False
        return idx1,idx2,idx3

    ### Titol
    titol=f":blue[{model.title}]"
    st.title(titol)

    ### Usuari
    col1,col2,col3 = st.columns([2,1,8],gap='small')

    with col1:
        lector = st.number_input('Entra codi de Lector (o clica NOU)',1,st.session_state['max_id'],st.session_state['primer'],on_change=treure_recomanacions)
        nom,edat = model.usuari(lector)
  
    with col2:
        st.write(' ')
        st.write(' ')
        st.button('Nou',on_click=nou_call)

    with st.form('formulari1'): 
        col1,col2,col3 = st.columns([4,1,2],gap='medium')

        with col1:
            nom = st.text_input(label='nom',value=nom)

        with col2:
            edat = st.number_input('edat',0,110,edat)

        with col3:
            st.radio('Gènere',model.genere_opcions(),horizontal=True)

        col4,col5 = st.columns([5,4],gap='small')
        with col4:
            st.write('') 
            llegits,no_edit,configuracio = model.llegits(lector)
            new_config = {}
            for key,value in configuracio.items():
                if len(value)==1:
                    new_config[key] =value[0]
                else:
                    new_config[key] = st.column_config.NumberColumn(value[0],min_value=value[1],max_value=value[2],step=1)
            nous_llegits = st.data_editor(llegits,disabled=no_edit,column_config=new_config,hide_index=True)
   
        with col5:
            st.multiselect("Gèneres Literaris",model.genre_opcions())
            st.radio('Vols llibres adaptats al cinema?',model.adaptats_opcions(),horizontal=True)
            st.radio('Vols un Best Seller?',model.bestseller_opcions(),horizontal=True)
            st.radio('Quin tipus de lectura?',model.lectura_opcions(),horizontal=True)
        
        submitted = st.form_submit_button("Desa Canvis i Recomana",type='primary')
        if submitted:
            model.canvia_nom(lector,nom)
            model.canvia_edat(lector,edat)
            model.actualitzar_puntuacions(nous_llegits) 
            st.session_state['mostrar_recomanacions']=True  
            st.session_state['idx_recomanacio'] = 0 

    ### Recomanacions        
    if st.session_state['mostrar_recomanacions']:
        st.session_state['recomanacions'] = model.recomanacions(lector)
        if len(st.session_state['recomanacions'])==0 :
            st.subheader(':blue[Amb les dades que em dones, no et puc recomenar cap llibre]')
        else:
            st.subheader(':blue[Les teves recomanacions]')
            index = calcula_index_recomanacions()
            columnes = st.columns([2,2,2])
            noms_butons = ['Comprar','Comprar ','Comprar  ']
            for idx,col,buto in zip(index,columnes,noms_butons):
                with col:
                    book = st.session_state['recomanacions'][idx][0]
                    writer = st.session_state['recomanacions'][idx][1]
                    st.write(f':red[***#{idx+1} {book}***]')
                    st.write(f':red[*{writer}*]')
                    with st.expander('Raonament'):
                        st.write(st.session_state['recomanacions'][idx][2])
                    st.button(buto,on_click=comprar_call,args=[idx])

        st.button('Mes Recomanacions',type='primary')


################ Model ################

class Model:
   
    def __init__(self):
        self.books=pd.read_csv('Books.csv',low_memory=False)
        self.users=pd.read_csv('Users.csv')
        self.ratings=pd.read_csv('Ratings.csv')
        
        self.genre_options = [
            "Comèdia", "Ficció", "Ciència ficció", "Històrica", "Romàntica",
            "Fantasia", "Ciència", "Creixement personal", "Autoajuda",
            "Policiaca", "Juvenil"
        ]
        self.genere_options=['Dona','Home','Altres']
        self.adaptats_options=['Si','No','Indiferent']
        self.bestseller_options=['Si','No','Indiferent']
        self.lectura_options=['Densa','Lleugera','Indiferent']
        self.title = 'Recomanador de Llibres'

    def darrer_lector(self):
        return len(self.users)
   
    def afegir_lector(self):
        new_row = pd.DataFrame({'User-ID':[len(self.users)+1],'Nom':[''],'Age':[0]})
        self.users= pd.concat([self.users,new_row], ignore_index=True)
     
    def genre_opcions(self):
        return self.genre_options
   
    def genere_opcions(self):
        return self.genere_options

    def adaptats_opcions(self):
        return self.adaptats_options

    def bestseller_opcions(self):
        return self.bestseller_options

    def lectura_opcions(self):
        return self.lectura_options

    def usuari(self,id):
        usuari = self.users.loc[self.users['User-ID'] == id].iloc[0]
        nom=usuari[2]
        edat=usuari[1]
        return nom,edat
   
    def llegits(self,id):
        df = self.users.loc[self.users['User-ID'] == id]
        llegits = pd.merge(pd.merge(df, self.ratings, on="User-ID"),self.books[['ISBN','Book-Title','Book-Author']],on='ISBN')
        llegits.drop(['Nom','Age'], inplace=True, axis=1)
        llegits = llegits[['Book-Title','Book-Author','Book-Rating','ISBN','User-ID']]   # Per ordenar les columnes
        #llegits = llegits.sort_values('Book-Rating')
        camps_no_editables =('Book-Title','Book-Author')

        # diccionaria amb confirguracio de les columnes: None=no surt, Nom=surt amb aquest nom, [nom,min,max] : columna numerica editable amb nom min i max
        configuracio ={'ISBN':[None], 'User-ID':[None],'Book-Title':['Titol'],'Book-Author':['Autor'],'Book-Rating':['Puntuacio',0,10]}
        return llegits,camps_no_editables,configuracio
   
    def canvia_nom(self,id,nom):
        self.users.loc[self.users["User-ID"]==id,'Nom'] = nom
        #self.users.to_csv('Users.csv', encoding='utf-8', index=False)

    def canvia_edat(self,id,edat):
        self.users.loc[self.users["User-ID"]==id,'Age'] = edat
        #self.users.to_csv('Users.csv', encoding='utf-8', index=False)
      
    def actualitzar_puntuacions(self,modificats):
        for idx,fila in modificats.iterrows():
            self.ratings.loc[(self.ratings['User-ID']==fila['User-ID']) & (self.ratings['ISBN']==fila['ISBN']),'Book-Rating']=fila['Book-Rating']
    
    def recomanacions(self,lector):
        llista=[]
        df = self.books.sort_values('Classificacio',ascending=False).head(lector*20).tail(14)
        for idx,fila in df.iterrows():
            lectors = fila['Read']
            punts = fila['Rating']
            llista.append((fila['Book-Title'],fila['Book-Author'],f'la recomanació es per que aquest llibre te {lectors:d} lectors amb una puntuacio mitjana de {punts:.2f}',
                          fila['ISBN'],lector))
        return llista

    def afegir_rating(self,isbn,lector):
        self.ratings.loc[len(self.ratings)] = [lector,isbn,0]


################ Start  ################

## el set page s'ha nomes un cop i abans de qualsevol instrucció
st.set_page_config( page_title='Llibres',
                    layout="wide",
                    initial_sidebar_state="expanded")

if 'model' not in st.session_state:
  st.session_state['model'] = Model()

view(st.session_state['model'])


