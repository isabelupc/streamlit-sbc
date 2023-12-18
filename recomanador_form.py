import streamlit as st
import pandas as pd
from cbr import CBR
from Functions import *

#Carreguem l'arbre de casos

#Load

PATH_FILE = "Decision_Tree"
dt_instance = DecisionTree()
dt = dt_instance.load(PATH_FILE)

#graph = plot_tree(decision_tree_root)
#graph.render('decision_tree', view=True)

#To check that loading works:

#case = data.iloc[0,:].to_dict()  #Select one case to check the subset where it is addressed at.
#subset_cases_node = evaluate_case_through_tree(decision_tree_root,case)
#for c in subset_cases_node.subset:
#    print("Location: ",c,"\tCase id:",c.id_cas)


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
            any = st.number_input('Any de naixement 🗓️',1900,2030, dades['any_naixement'])
            dades['any_naixement'] = any

        with col3:
            dades['genere_persona']=st.radio('Gènere',model.get_sex_options(),horizontal=True, index=dades['genere_persona'])

        col4,col5 = st.columns([5,4],gap='small')
        with col4:
            st.write('') 
            llegits,no_edit,configuracio = model.read(lector)
            new_config = {}
            for key,value in configuracio.items():
                if len(value)==1:
                    new_config[key] =value[0]
                else:
                    new_config[key] = st.column_config.NumberColumn(value[0],min_value=value[1],max_value=value[2],step=1)
            nous_llegits = st.data_editor(llegits,disabled=no_edit,column_config=new_config,hide_index=True)
   
        with col5:
            default=[]
            for g in model.get_genre_options():
                if dades[g]== 1:
                    default.append(g)
            generes =st.multiselect("Quins són els teus gèneres literaris preferits? ⭐️",model.get_genre_options(),default)
            for g in generes:
                dades[g] = 1
            default_idi = []
            for i in dades['idioma']:
                default_idi.append(i)
            dades['idioma']=st.multiselect("En quins idiomes prefereixes llegir? 🌎",model.get_language_options(),default_idi)
            dades['idioma'] = set(dades['idioma'])
            dades['pref_adaptacio_peli']=st.radio('Prefereixes llibres adaptats al cinema? 🎥',model.get_film_options(),horizontal=True,index=dades['pref_adaptacio_peli'])
            dades['pref_best_seller']=st.radio('Prefereixes un Best Seller? 🎖️',model.get_bestseller_options(),horizontal=True,index=dades['pref_best_seller'])
            dades['pref_sagues']=st.radio("Prefereixes que el llibre formi part d'una saga? 🎭",model.get_saga_options(),horizontal=True,index=dades['pref_sagues'])
            dades['pref_tipus_lectura']=st.radio('Quin tipus de lectura prefereixes? 📖',model.get_reading_options(),horizontal=True,index=dades['pref_tipus_lectura'])
            dades['pagines_max']=st.number_input('Màxim número de pàgines 📄',0,100000000,dades['pagines_max'])
        
        submitted = st.form_submit_button("Desa Canvis i Recomana",type='primary')
        if submitted:
            model.change_user_name(lector,nom)
            model.actualitzar_puntuacions(nous_llegits)
            model.delete_last_if_empty()
            st.session_state['mostrar_recomanacions']=True  
            st.session_state['idx_recomanacio'] = 0 

    ### Recomanacions     
    
    if st.session_state['mostrar_recomanacions']:
        with st.form('formulari2'):
            st.session_state['recomanacions'] = model.recomanacions(lector,dades)
            #TRAÇA
            #trace_data = model.get_trace_data()
            if len(st.session_state['recomanacions'])==0 :
                st.subheader(':red[Amb les dades que em dones, no et puc recomenar cap llibre]')
            else:
                st.subheader(':red[Les teves recomanacions]')
                
                columnes = st.columns([2,2,2])
                noms_butons = ['Valora','Valora ','Valora  ']
                puntuacions=[0,0,0]
                comprar=[False,False,False]
                comprar_butons = ['Comprar','Comprar ','Comprar  ']
                for idx,col in enumerate(columnes):
                    with col:
                        book = st.session_state['recomanacions'][idx][0]
                        writer = st.session_state['recomanacions'][idx][1]
                        st.write(f':white[***#{idx+1} {book}***]')
                        st.write(f':white[*{writer}*]')
                        with st.expander('Raonament'):
                            st.write(st.session_state['recomanacions'][idx][2])
                            st.dataframe(st.session_state['recomanacions'][idx][7],use_container_width=True)
                            st.write(st.session_state['recomanacions'][idx][5])
                            st.write(st.session_state['recomanacions'][idx][6])
                            st.dataframe(st.session_state['recomanacions'][idx][8],use_container_width=True)
                        col1,col2 = st.columns(2)
                        with col1:
                            puntuacions[idx] = st.slider(noms_butons[idx],1,5,1)
                        with col2:
                            st.write('# ')
                            comprar[idx] = st.checkbox(comprar_butons[idx])
        
            submitted = st.form_submit_button("Desa Valoracions",type='primary')
            if submitted:
                for i in range(3):
                    case = model.adapted[i]
                    case.set_id_case(model.id_case_1+i)
                    case.set_puntuacio(puntuacions[i])
                    case.set_comprat("Si" if comprar[i] else "No")
                    model.retain(case)

                #COMENTAR SI ES VOL PROVAR EL SISTEMA SENSE GUARDAR ELS CASOS A LA BASE DE CASOS
                model.case_base.save(PATH_FILE)         
                st.session_state['mostrar_recomanacions']=False 
                st.rerun()


## el set page s'ha de cridar només un cop i abans de qualsevol instrucció
st.set_page_config( page_title='Llibres',
                    layout="wide",
                    initial_sidebar_state="expanded")

if 'model' not in st.session_state:
  st.session_state['model'] = CBR(case_base=dt)

view(st.session_state['model'])


