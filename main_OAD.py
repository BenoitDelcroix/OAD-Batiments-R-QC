# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 11:48:16 2021

Prototype d'app (Streamlit) pour aider à la prise de décision dans le cadre de
la mise en place de mesures d'efficacité énergétique dans le bâtiment 
résidentiel.  

@author: DK6034
"""
###############################################################################
# IMPORT DES LIBRAIRIES D'INTÉRÊT
###############################################################################
import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from joblib import load
import sys
import plotly.graph_objects as go

###############################################################################
# Utiliser toute la largeur de la page sur Streamlit
###############################################################################
st.set_page_config(layout="wide")

###############################################################################
# DÉFINIR LE RÉPERTOIRE DE L'APP
###############################################################################
full_path = os.path.realpath(__file__)
path, filename = os.path.split(full_path)
os.chdir(path)

###############################################################################
# DÉFINITION DES FONCTIONS D'INTÉRÊT
###############################################################################
@st.cache_data
def LoadJsonFiles():
    """
    Fonction pour charger tous les fichiers json permettant de faire la
    correspondance entre les entrées des modèles et leurs significations.

    Returns
    -------
    data : DICT
        Dictionnaire contenant la correspondance entre les propriétés d'intérêt
        des bâtiments résidentiels et les nombres entiers utilisés dans les
        modèles.

    """
    path='json/'
    ListFiles = os.listdir(path)
    data = dict()
    for i in ListFiles:
        with open(path+i,'rb') as f:
            data[i[:-5]] = json.load(f)
        f.close()
    
    return data

@st.cache_data
def LoadWeather():
    """
    Fonction pour charger tous les fichiers csv météo de chaque région 
    considérée.

    Returns
    -------
    meteo : DICT
        Dictionnaire contenant la météo de toutes les régions considérées.

    """
    path='weather/'
    weather = load(path+'weather.joblib')
    
    return weather

@st.cache_resource
def LoadPRISMmodel():
    """
    Fonction pour charger le modèle PRISM permettant d'estimer la consommation
    électrique journalière totale (compteur) d'un bâtiment résidentiel en 
    fonction des conditions météo, des éphémérides et des propriétés du 
    bâtiment et d'occupation de ce bâtiment.

    Returns
    -------
    model : SCIKIT-LEARN MODEL (JOBLIB)
        Modèle PRISM en format joblib.

    """
    path = 'models/'
    model = load(path+'PRISMmodel.joblib')
    
    return model

@st.cache_resource
def LoadDesagModel():
    """
    Fonction pour charger le modèle de désagrégation permettant d'estimer la 
    part de la consommation de chaque usage (CVCA, ECS, équipements, éclairage,
    spa et piscine) en fonction des conditions météo, des éphémérides, de la
    consommation électrique totale, et des propriétés du bâtiment et 
    d'occupation de ce bâtiment.

    Returns
    -------
    model : SCIKIT-LEARN MODEL (JOBLIB)
        Modèle de désagrégation en format joblib.

    """
    path = 'models/'
    model = load(path+'DesagModel.joblib')
    
    return model

###############################################################################
# PROGRAMME PRINCIPAL
###############################################################################
if __name__ == '__main__':
    ### Importer les fichiers json
    correspondance = LoadJsonFiles()
    
    ### Importer les fichiers météo
    weather = LoadWeather()
    
    ### Importer le modèle PRISM
    PRISMmod = LoadPRISMmodel()
    
    ### Importer le modèle de désagrégation
    DesagMod = LoadDesagModel()
    
    ### Titre de l'app
    st.title('Outil d\'aide à la décision pour le secteur du bâtiment'+\
             ' résidentiel')
                
    ### Descriptif de l'app
    st.markdown("""
                Cet outil permet de comparer différents scénarios de 
                consommation électrique de bâtiments résidentiels en faisant 
                varier de nombreux paramètres tels que:  
                    - la localisation;  
                    - le type de bâtiment;  
                    - la configuration de l'enveloppe du bâtiment;  
                    - le nombre d'occupants;  
                    - les équipements dans le bâtiment et leurs propriétés.  
                """)
    st.markdown("""
                ---
                """)
    
    ### Sous-titre 1
    st.header('1. Définition des scénarios')
    st.subheader('1.1. Définition du nombre de scénarios')
    nbScenario = st.selectbox('Nombre de scénarios:',
                              list(np.arange(1,6,1)))
    st.markdown("""
                ---
                """)
                
    ### Définition de chacun des scénarios
    Scenarios = dict()
    st.subheader('1.2. Définition de chacun des scénarios')
    st.markdown("""
                #### 1.2.1. Localisation et propriétés principales du bâtiment  
                
                """)
    cols = st.columns(int(nbScenario))
    j = 0
    for i in cols:
        j+=1
        i.write('**SCÉNARIO '+str(j)+'**')
        with i:
            ### Région du Québec
            region = st.selectbox('Choisir la ville pour Scénario '+\
                                  str(j)+':',
                                  list(correspondance['region'].keys()))
            region = correspondance['region'][region]
            ### Type de bâtiment
            buildingtype = st.selectbox('Choisir le type de bâtiment'+\
                                        ' pour Scénario '+str(j)+':',
                                        correspondance['buildingtype'].keys())
            buildingtype = correspondance['buildingtype'][buildingtype]
            ### Surface chauffée
            area = st.slider('Surface chauffée du bâtiment'+\
                             ' (m²) pour Scénario '+str(j)+':',50,280)
            ### Nombre d'occupants
            nbOccupants = st.selectbox('Nombre d\'occupants pour'+\
                                       ' Scénario '+str(j)+':',
                                       list(np.arange(1,6,1)))
            ### Ajouter le scénario au dictionnaire Scenarios
            Scenarios[j] = {'Region':int(region),
                            'Building type':float(buildingtype),
                            '# occupants':float(nbOccupants),
                            'Exact heated area':float(area)}
    
    st.markdown("""
                #### 1.2.2. Propriétés d'isolation du bâtiment  
                
                """)
    cols = st.columns(int(nbScenario))
    j = 0
    for i in cols:
        j+=1
        i.write('**SCÉNARIO '+str(j)+'**')
        with i:
            ### Résistance thermique des murs
            Rwall = st.selectbox('Résistance thermique des murs (m²K/W)'+\
                                 ' pour Scénario '+str(j)+':',
                                 [1,2,3,5])
            ### Résistance thermique des toits
            Rroof = st.selectbox('Résistance thermique des toits (m²K/W)'+\
                                 ' pour Scénario '+str(j)+':',
                                 [1,2,3,4,5,8])
            ### Résistance thermique des fondations
            Rfloor = st.selectbox('Résistance thermique des fondations'+\
                                  ' (m²K/W) pour Scénario '+str(j)+':',
                                  [1,2,3,4])
            ### Ajouter le scénario au dictionnaire Scenarios
            Scenarios[j]['Wall thermal resistance'] = float(Rwall)
            Scenarios[j]['Roof thermal resistance'] = float(Rroof)
            Scenarios[j]['Foundation thermal resistance'] = float(Rfloor)
    
    st.markdown("""
                #### 1.2.3. Propriétés d'infiltration du bâtiment  
                
                """)
    cols = st.columns(int(nbScenario))
    j = 0
    for i in cols:
        j+=1
        i.write('**SCÉNARIO '+str(j)+'**')
        with i:
            ### Surface d'infiltration
            averageleakagearea = st.selectbox('Choisir le niveau'+\
                                              ' d\'infiltration pour'+\
                                              ' Scénario '+str(j)+':',
                                              correspondance['averageleakagearea'].keys())
            averageleakagearea = correspondance['averageleakagearea'][averageleakagearea]
            ### Ajouter le scénario au dictionnaire Scenarios
            Scenarios[j]['Average leakage area'] = float(averageleakagearea)
    
    st.markdown("""
                #### 1.2.4. Propriétés de fenestration du bâtiment  
                
                """)
    cols = st.columns(int(nbScenario))
    j = 0
    for i in cols:
        j+=1
        i.write('**SCÉNARIO '+str(j)+'**')
        with i:
            ### Ratio entre les surfaces vitrée et totale
            windowtowallratio = st.selectbox('Choisir le ratio entre les'+\
                                             ' surfaces vitrée et totale'+\
                                             ' pour Scénario '+str(j)+':',
                                             correspondance['windowtowallratio'].keys())
            windowtowallratio = correspondance['windowtowallratio'][windowtowallratio]
            ### Type de fenêtres
            glazing = st.selectbox('Nombre de vitrages dans les fenêtres pour'+\
                                   ' Scénario '+str(j)+':',
                                   list(np.arange(1,4,1)))
            ### Ajouter le scénario au dictionnaire Scenarios
            Scenarios[j]['Window-to-wall ratio'] = float(windowtowallratio)
            Scenarios[j]['# window glazings'] = float(glazing)
    
    st.markdown("""
                #### 1.2.5. Équipements CVCA du bâtiment  
                
                """)
    cols = st.columns(int(nbScenario))
    j = 0
    for i in cols:
        j+=1
        i.write('**SCÉNARIO '+str(j)+'**')
        with i:
            ### Présence d'une pompe à chaleur pour le chauffage
            heatpump = st.selectbox('Présence d\'une pompe à chaleur pour le'+\
                                    ' chauffage pour Scénario '+str(j)+':',
                                    correspondance['heatpump'].keys())
            heatpump = correspondance['heatpump'][heatpump]
            ### Type pour le chauffage auxiliaire
            auxiliaryheatingtype = st.selectbox('Choisir le type de chauffage'+\
                                                ' (auxiliaire si la pompe à'+\
                                                ' chaleur a été sélectionnée)'+\
                                                ' pour Scénario '+str(j)+':',
                                                correspondance['auxiliaryheatingtype'].keys())
            auxiliaryheatingtype = correspondance['auxiliaryheatingtype'][auxiliaryheatingtype]
            ### Conditionnement d'air
            airconditioning = st.selectbox('Choisir le système de'+\
                                           ' climatisation pour'+\
                                           ' Scénario '+str(j)+':',
                                           correspondance['airconditioning'].keys())
            airconditioning = correspondance['airconditioning'][airconditioning]
            ### Ajouter le scénario au dictionnaire Scenarios
            Scenarios[j]['Air conditioning'] = float(airconditioning)
            Scenarios[j]['Heat pump'] = float(heatpump)
            Scenarios[j]['Auxiliary heating type'] = float(auxiliaryheatingtype)
    
    st.markdown("""
                #### 1.2.6. Approvisionnement de l'ECS du bâtiment  
                
                """)
    cols = st.columns(int(nbScenario))
    j = 0
    for i in cols:
        j+=1
        i.write('**SCÉNARIO '+str(j)+'**')
        with i:
            ### Eau chaude sanitaire
            DHWenergysource = st.selectbox('Choisir la source d\'énergie pour'+\
                                           ' l\'eau chaude sanitaire pour'+\
                                           ' Scénario '+str(j)+':',
                                           correspondance['DHWenergysource'].keys())
            DHWenergysource = correspondance['DHWenergysource'][DHWenergysource]
            ### Ajouter le scénario au dictionnaire Scenarios
            Scenarios[j]['DHW energy source'] = float(DHWenergysource)
    
    st.markdown("""
                #### 1.2.7. Présence de spa/piscine dans le bâtiment  
                
                """)
    cols = st.columns(int(nbScenario))
    j = 0
    for i in cols:
        j+=1
        i.write('**SCÉNARIO '+str(j)+'**')
        with i:
            ### Présence d'une piscine
            pool = st.selectbox('Présence d\'une piscine pour'+\
                                ' Scénario '+str(j)+':',
                                correspondance['pool'].keys())
            pool = correspondance['pool'][pool]
            ### Présence d'un spa
            spa = st.selectbox('Présence d\'un spa pour'+\
                               ' Scénario '+str(j)+':',
                               correspondance['spa'].keys())
            spa = correspondance['spa'][spa]
            ### Ajouter le scénario au dictionnaire Scenarios
            Scenarios[j]['Pool'] = float(pool)
            Scenarios[j]['Spa'] = float(spa)

    ### Séparation entre les différents scénarios
    st.markdown("""
                ---
                """)
                
    ### Préparer les dataframes d'intrant pour chacun des scénarios
    DFdict = dict()
    for i in Scenarios:
        df = pd.DataFrame()
        df[['dayofweek', 'Temp (°C)', 'Rel Hum (%)']] = weather[
            str(Scenarios[i]['Region'])][['dayofweek','Temp (°C)','Rel Hum (%)']]
        df['Building type'] = np.full(len(df),Scenarios[i]['Building type'])
        df['Window-to-wall ratio'] = np.full(len(df),Scenarios[i]['Building type'])
        df['# occupants'] = np.full(len(df),Scenarios[i]['# occupants'])
        df['Wall thermal resistance'] = np.full(len(df),Scenarios[i]['Wall thermal resistance'])
        df['Roof thermal resistance'] = np.full(len(df),Scenarios[i]['Roof thermal resistance'])
        df['Foundation thermal resistance'] = np.full(len(df),Scenarios[i]['Foundation thermal resistance'])
        df['Average leakage area'] = np.full(len(df),Scenarios[i]['Average leakage area'])
        df['Air conditioning'] = np.full(len(df),Scenarios[i]['Air conditioning']) 
        df['Heat pump'] = np.full(len(df),Scenarios[i]['Heat pump'])
        df['Auxiliary heating type'] = np.full(len(df),Scenarios[i]['Auxiliary heating type'])
        df['DHW energy source'] = np.full(len(df),Scenarios[i]['DHW energy source'])
        df['Pool'] = np.full(len(df),Scenarios[i]['Pool'])
        df['Spa'] = np.full(len(df),Scenarios[i]['Spa'])
        df['Exact heated area'] = np.full(len(df),Scenarios[i]['Exact heated area'])
        df['# window glazings'] = np.full(len(df),Scenarios[i]['# window glazings'])
        DFdict[i] = df
    
    ### Simulation des différents scénarios
    st.header('2. Résultats')
    BoolSim = st.button('Simuler tous les scénarios')
    if BoolSim: #st.checkbox('Cocher pour simuler tous les scénarios',value=True):
        ### Calculer les consommations électriques journalières pour chacun des scénarios
        st.subheader('2.0. Barre de progression des simulations')
        my_bar = st.progress(0.0)
        DFdict_PRISM = dict()
        DFdict_Desag = dict()
        for i in DFdict:
            temp = DFdict[i].copy()
            df_PRISM = PRISMmod.predict(temp)
            df_PRISM = pd.DataFrame(data=df_PRISM,index=temp.index,
                                    columns=['Meter_kWh'])
            DFdict_PRISM[i] = df_PRISM
            temp['Meter_kWh'] = df_PRISM['Meter_kWh']
            df_Desag = DesagMod.predict(temp)
            i2c = np.where(df_Desag < 0)
            df_Desag[i2c] = 0
            if Scenarios[i]['Pool'] > 1:
                df_Desag[:,5] = 0
            if Scenarios[i]['Spa'] > 1:
                df_Desag[:,4] = 0
            df_Desag = df_Desag/df_Desag.sum(axis=1,keepdims=True)
            df_Desag = df_Desag*df_PRISM.values
            df_Desag = pd.DataFrame(data=df_Desag,index=temp.index,
                                    columns=['HVAC_kWh','DHW_kWh',
                                             'Appliances_kWh','Lighting_kWh',
                                             'Spa_kWh','Pool_kWh'])
            DFdict_Desag[i] = df_Desag
            my_bar.progress(i/len(DFdict))
        st.markdown(""" 
                    ---
                    """)
        st.subheader('2.1. Comparaison des profils de consommation')
        fig1 = go.Figure()
        for i in DFdict_PRISM:
            fig1.add_trace(go.Scatter(x=DFdict_PRISM[i].index, 
                                      y=DFdict_PRISM[i]['Meter_kWh'],
                                      mode='lines',
                                      name='Scénario '+str(i)))
        fig1.update_layout(title='Évolution de la consommation électrique'+\
                           ' journalière durant une année pour chaque scénario')
        fig1.update_xaxes(title_text='Date')
        fig1.update_yaxes(title_text='Consommation électrique journalière <br> [kWh/jour]')
        st.plotly_chart(fig1,use_container_width=True)
        st.markdown(""" 
                    ---
                    """)
        
        st.subheader('2.2. Bilan annuel de la consommation')
        fig2 = go.Figure()
        for i in DFdict_PRISM:
            fig2.add_trace(go.Bar(x=[''], 
                                  y=[DFdict_PRISM[i]['Meter_kWh'].sum()],
                                  name='Scénario '+str(i)))
        fig2.update_layout(title='Bilan annuel de la consommation électrique'+\
                           ' pour chaque scénario')
        fig2.update_yaxes(title_text='Consommation électrique annuelle <br> [kWh/an]')
        st.plotly_chart(fig2,use_container_width=True)
        st.markdown("""
                    ---
                    """)
        
        st.subheader('2.3. Bilan annuel des différents usages')
        fig3 = go.Figure()
        for i in DFdict_Desag:
            fig3.add_trace(go.Bar(x=['CVCA','ECS','Appareils','Éclairage',
                                     'Spa','Piscine'], 
                                  y=DFdict_Desag[i].sum().values,
                                  name='Scénario '+str(i)))
        fig3.update_layout(title='Bilan annuel de la consommation électrique'+\
                           ' des différents usages pour chaque scénario')
        fig3.update_xaxes(title_text='Poste de consommation')
        fig3.update_yaxes(title_text='Consommation électrique annuelle <br> [kWh/an]')
        st.plotly_chart(fig3,use_container_width=True)
        st.markdown(""" 
                    ---
                    """)
        