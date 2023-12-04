import streamlit as st
import pandas as pd
from cbr import CBR



################ View  ################
def view(model):

    # Inicialització de les variables de sessio
    if 'iniciat' not in st.session_state:
        st.session_state['iniciat']=True
        st.session_state['max_id']=model.last_user()
        st.session_state['primer']=1
        st.session_state['idx_recomanacio']=0
        st.session_state['mostrar_recomanacions']=False
        st.session_state['ha_comprat']=False

    # Funcions auxiliars i callbacks   
    def treure_recomanacions():
            st.session_state['mostrar_recomanacions']=False
            st.session_state['idx_recomanacio']=0

    def nou_call():  
        model.add_user()
        st.session_state['primer'] = model.last_user()
        st.session_state['max_id'] = st.session_state['primer']
        treure_recomanacions()

    ### Titol
    titol=f":red[{model.title}]"
    st.title(titol)

    ### Usuari
    col1,col2,col3 = st.columns([2,1,8],gap='small')

    with col1:
        lector = st.number_input('Entra codi de Lector (o clica NOU) 👤',1,st.session_state['max_id'],st.session_state['primer'],on_change=treure_recomanacions)
        nom, dades = model.user_data(lector)
  
    with col2:
        st.write(' ')
        st.write(' ')
        st.button('Nou',on_click=nou_call)

    with st.form('formulari1'): 
        col1,col2,col3 = st.columns([4,1,2],gap='medium')

        with col1:
            nom = st.text_input(label='Nom ✍🏼',value=nom)

        with col2:
            dades['year'] = st.number_input('Any de naixement 🗓️',1900,2030,dades['year'])

        with col3:
            dades['sex']=st.radio('Gènere',model.get_sex_options(),horizontal=True, index=dades['sex'])

        col4,col5 = st.columns([5,4],gap='small')
        with col4:
            st.write('') 
            llegits,configuracio = model.read(lector)
            new_config = {}
            for key,value in configuracio.items():
                if len(value)==1:
                    new_config[key] =value[0]
                else:
                    new_config[key] = st.column_config.NumberColumn(value[0],min_value=value[1],max_value=value[2],step=1)
            st.dataframe(llegits,column_config=new_config,hide_index=True)
   
        with col5:
            dades['genre']=st.multiselect("Quins són els teus gèneres literaris preferits? ⭐️",model.get_genre_options(),default=dades['genre'])
            dades['film']=st.radio('Prefereixes llibres adaptats al cinema? 🎥',model.get_film_options(),horizontal=True,index=dades['film'])
            dades['bestseller']=st.radio('Prefereixes un Best Seller? 🎖️',model.get_bestseller_options(),horizontal=True,index=dades['bestseller'])
            dades['saga']=st.radio("Prefereixes que el llibre formi part d'una saga? 🎭",model.get_saga_options(),horizontal=True,index=dades['saga'])
            dades['reading']=st.radio('Quin tipus de lectura prefereixes? 📖',model.get_reading_options(),horizontal=True,index=dades['reading'])
            dades['pages']=st.number_input('Màxim número de pàgines 📄',0,100000000,dades['pages'])
        
        submitted = st.form_submit_button("Desa Canvis i Recomana",type='primary')
        if submitted:
            model.change_user_name(lector,nom)
            st.session_state['mostrar_recomanacions']=True  
            st.session_state['idx_recomanacio'] = 0 

    ### Recomanacions     
    
    if st.session_state['mostrar_recomanacions']:
        with st.form('formulari2'):
            st.session_state['recomanacions'] = model.recomanacions(lector,dades)
            if len(st.session_state['recomanacions'])==0 :
                st.subheader(':red[Amb les dades que em dones, no et puc recomenar cap llibre]')
            else:
                st.subheader(':red[Les teves recomanacions]')
                
                columnes = st.columns([2,2,2])
                noms_butons = ['Valora','Valora ','Valora  ']
                puntuacions=[0,0,0]
                for idx,col in enumerate(columnes):
                    with col:
                        book = st.session_state['recomanacions'][idx][0]
                        writer = st.session_state['recomanacions'][idx][1]
                        st.write(f':white[***#{idx+1} {book}***]')
                        st.write(f':white[*{writer}*]')
                        with st.expander('Raonament'):
                            st.write(st.session_state['recomanacions'][idx][2])
                        puntuacions[idx] = st.slider(noms_butons[idx],1,5,1)
        
            submitted = st.form_submit_button("Desa Valoracions",type='primary')
            if submitted:
                for i in range(3):
                    model.retain(lector,dades,st.session_state['recomanacions'][i][3],puntuacions[i])          
                st.session_state['mostrar_recomanacions']=False 
                st.rerun()


## el set page s'ha de cridar només un cop i abans de qualsevol instrucció
st.set_page_config( page_title='Llibres',
                    layout="wide",
                    initial_sidebar_state="expanded")

if 'model' not in st.session_state:
  st.session_state['model'] = CBR()

view(st.session_state['model'])


