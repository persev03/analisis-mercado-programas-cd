from pathlib import Path
import json, html, unicodedata
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from analytics import ROOT, SCOPES, COLORS, load_data, select_scope, series, forecast, cagr_table, fmt

st.set_page_config(page_title='Análisis de Mercado Programas CD · EIA',page_icon='◈',layout='wide',initial_sidebar_state='expanded')
st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"],.stApp{font-family:'DM Sans',sans-serif}h1,h2,h3,h4{font-family:'Manrope',sans-serif!important;letter-spacing:-.04em}
.block-container{padding:1.6rem 2.6rem 3rem;max-width:1600px}header[data-testid="stHeader"]{background:transparent;height:2rem}
[data-testid="stSidebar"]{background:#14283F;color:#E7EDF3;min-width:255px;max-width:275px}
[data-testid="stSidebar"] *{color:#E7EDF3}[data-testid="stSidebar"] [data-baseweb="select"] *{color:#182B44}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p{font-size:12px;letter-spacing:.035em;color:#C0CDD9}
[data-testid="stSidebar"] hr{border-color:#32445A}[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p{color:#A8BAC9;font-size:11px}
.brand{font-family:Manrope,sans-serif;font-size:46px;font-weight:800;letter-spacing:-5px;color:white;line-height:1}.brand span{font-size:10px;letter-spacing:2px;display:block;margin-top:14px;color:#80CDD3}
.brand-sub{font-size:11px;line-height:1.7;color:#A8BAC9;margin-top:15px;margin-bottom:20px}
.eyebrow{font-size:10px;letter-spacing:2px;font-weight:700;color:#648197;text-transform:uppercase;margin:0 0 7px}
.heading{font-family:Manrope,sans-serif;font-size:32px;font-weight:800;line-height:1.2;letter-spacing:-1.3px;color:#182B44;margin-bottom:7px}
.subheading{font-size:13px;color:#6D7C8D;margin:0 0 20px}.pill{display:inline-block;border:1px solid #D6E4E8;padding:5px 10px;border-radius:20px;font-size:10px;color:#376574;background:#F2F8F8;margin-right:5px}
.kpi{background:white;border:1px solid #E3E8EF;border-radius:12px;padding:18px 21px;margin-bottom:12px;box-shadow:0 3px 10px #192D4503}.kpi-label{font-size:11px;color:#687B8E;font-weight:500}.kpi-value{font-family:Manrope;font-size:34px;color:#182B44;font-weight:800;letter-spacing:-1.6px;line-height:1.4}.kpi-note{font-size:11px;color:#65788A}.kpi-accent{border-left:3px solid #087F8C}
.insight{background:#E8F3F3;border-radius:10px;padding:17px 20px;font-size:13px;line-height:1.65;color:#284D59;margin:9px 0 16px}.note{font-size:11px;line-height:1.65;color:#758598}
.section{font-family:Manrope;font-size:19px;font-weight:800;color:#20354E;margin:15px 0 4px;letter-spacing:-.5px}
.rule{height:1px;background:#E2E8F0;margin:18px 0}.mini-card{border:1px solid #E1E6ED;background:#FFFFFF;padding:20px;border-radius:12px;min-height:148px}
.mini-card h4{font-size:15px;margin:0 0 9px}.mini-card p{font-size:12px;line-height:1.7;color:#687B8C;margin:0}
[data-testid="stPlotlyChart"]{border-radius:12px;overflow:hidden;border:1px solid #E5EAF0;background:white}
[data-testid="stMetric"]{background:white;border:1px solid #E3E8EF;border-radius:10px;padding:16px}
.stButton>button,.stDownloadButton>button{border-radius:8px;font-size:12px}.stTabs [data-baseweb="tab-list"]{gap:18px}
[data-testid="stDataFrame"]{border-radius:10px}.footer{margin-top:34px;padding-top:15px;border-top:1px solid #DEE6ED;font-size:10px;color:#8291A1;letter-spacing:.4px}
@media(max-width:800px){.block-container{padding:1rem}.heading{font-size:25px}.kpi-value{font-size:28px}}
</style>''',unsafe_allow_html=True)

@st.cache_data
def data(): return load_data()
@st.cache_data
def geography(): return json.loads((ROOT/'assets/colombia.geojson').read_text())
d,meta=data()

def title(name,description):
    st.markdown(f'<div class="eyebrow">Universidad EIA / Dirección de Ciencia de Datos</div><div class="heading">{name}</div><div class="subheading">{description}</div>',unsafe_allow_html=True)

def section(name,desc=None):
    st.markdown(f'<div class="section">{name}</div>',unsafe_allow_html=True)
    if desc: st.caption(desc)

def card(label,value,note='',accent=False):
    st.markdown(f'<div class="kpi {"kpi-accent" if accent else ""}"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-note">{note}</div></div>',unsafe_allow_html=True)

def layout(fig,height=350):
    fig.update_layout(height=height,margin=dict(l=24,r=24,t=30,b=32),paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF',font=dict(family='DM Sans, Arial',size=12,color='#566D82'),legend=dict(orientation='h',y=1.12,x=0,title=None),hoverlabel=dict(bgcolor='#14283F',font_color='white'),colorway=list(COLORS.values()),separators=',.')
    fig.update_xaxes(showgrid=False,zeroline=False)
    fig.update_yaxes(gridcolor='#EDF1F5',zeroline=False)
    return fig

def chart(fig,key=None): st.plotly_chart(fig,use_container_width=True,config={'displaylogo':False,'modeBarButtonsToRemove':['lasso2d','select2d'],'toImageButtonOptions':{'format':'png','scale':2}},key=key)

with st.sidebar:
    st.markdown('<div class="brand">EIA</div><div class="brand-sub" style="font-size:16px;color:white;font-weight:600">Análisis de Mercado<br>Programas CD</div>',unsafe_allow_html=True)
    page=st.radio('Explorar',['Colombia 2025','Competidores','Evolución histórica','Proyecciones 2030','Datos y metodología'],label_visibility='collapsed')
    st.divider()
    universe=st.selectbox('Universo de programas',['Mercado ampliado','Benchmark v3 original'],help='Ampliado añade Ingeniería de Datos e Inteligencia Artificial. Se excluyen licenciaturas, Sistemas, Software, Informática y posgrados.')
    scope=st.selectbox('Ámbito de análisis',SCOPES)
    year=st.select_slider('Año observado',options=list(range(2021,2026)),value=2025)
    segments=st.multiselect('Segmentos',['Directo','Cercano'],default=['Directo','Cercano'])
    metric_label=st.selectbox('Indicador',['Matrícula equivalente anual','Nuevo ingreso observado','Matrícula media observada'])
    st.divider()
    st.caption('SNIES · 2021–2025\n\nActualización del análisis: 30 sep 2026\n\nEIA 2026: referencia interna separada de las cifras oficiales.')
metric={'Matrícula equivalente anual':'matricula_equivalente_anual','Nuevo ingreso observado':'ingreso','Matrícula media observada':'matricula'}[metric_label]
base=d.copy() if universe=='Mercado ampliado' else d[d.universo_v3].copy()
hist=select_scope(base,scope); hist=hist[hist.segmento.isin(segments)]
current=hist[hist.anio==year].copy()
if not segments:
    st.info('Selecciona al menos un segmento para explorar el mercado.'); st.stop()
definitions={
    'matricula_equivalente_anual':'Tamaño del programa en un semestre promedio del año: sumamos la matrícula reportada y dividimos siempre entre 2. Ejemplo: 100 estudiantes en el primer semestre y 120 en el segundo dan 110. Si solo hay un reporte de 100, el resultado es 50; esto no significa que el otro semestre tuviera cero estudiantes. Esta medida reproduce el Excel original.',
    'ingreso':'Estudiantes que entraron a primer curso durante el año, según los reportes disponibles. Ejemplo: 20 nuevos en el primer semestre y 30 en el segundo dan 50 ingresos. No incluye a quienes ya venían cursando el programa. Si falta un semestre, el total puede estar incompleto.',
    'matricula':'Tamaño promedio del programa usando únicamente los semestres que sí tienen reporte. Con 100 y 120 estudiantes da 110. Si solo se reportó un semestre con 100, da 100, porque se divide entre 1. Coincide con la matrícula equivalente cuando hay datos de ambos semestres.'
}
with st.sidebar:
    st.info(definitions[metric])

COORDS={'Bogotá, D.C.':(4.711,-74.072),'Medellín':(6.244,-75.581),'Manizales':(5.070,-75.514),'Montería':(8.748,-75.881),'Santiago de Cali':(3.452,-76.532),'Bucaramanga':(7.119,-73.122),'Ibagué':(4.438,-75.232),'Chía':(4.863,-74.032),'Barranquilla':(10.989,-74.781),'Tunja':(5.535,-73.367),'Cartagena de Indias':(10.391,-75.480),'Soledad':(10.918,-74.765),'La Paz':(10.386,-73.171),'Envigado':(6.168,-75.586)}
CITY_COLORS={'Bogotá, D.C.':'#2563EB','Medellín':'#008579','Santiago de Cali':'#9B4AC5','Barranquilla':'#D97706','Bucaramanga':'#CC4269','Montería':'#6B7130'}
CITY_NAMES={'Bogotá, D.C.':'Bogotá','Santiago de Cali':'Cali'}

def selected_city(event):
    points=event.get('selection',{}).get('points',[])
    for point in reversed(points):
        custom=point.get('customdata')
        if isinstance(custom,(list,tuple)) and custom and custom[0] in COORDS:
            return custom[0]
    return None

def remember_city():
    st.session_state['city_to_open']=selected_city(st.session_state.get('mapa',{}))

@st.dialog('Detalle de la ciudad',width='large')
def city_detail(city,rows):
    detail=rows[rows.municipio==city]
    st.subheader(f'{CITY_NAMES.get(city,city)} · {year}')
    st.caption(f'{universe} · {", ".join(segments)} · {detail.ies_id.nunique()} universidades · {detail.snies.nunique()} programas (códigos SNIES)')
    a,b,c=st.columns(3)
    with a: st.metric('Matrícula equivalente anual',fmt(detail.matricula_equivalente_anual.sum(min_count=1),1))
    with b: st.metric('Nuevos ingresos',fmt(detail.ingreso.sum(min_count=1)))
    with c: st.metric('Matrícula media observada',fmt(detail.matricula.sum(min_count=1),1))
    st.caption('Matrícula: tamaño promedio por semestre. Nuevos ingresos: entradas a primer curso durante el año. Los promedios se calculan por programa y municipio y luego se suman.')
    st.dataframe(detail[['alias','programa','segmento','matricula_equivalente_anual','ingreso']].rename(columns={'alias':'Universidad','programa':'Programa','segmento':'Segmento','matricula_equivalente_anual':'Matrícula equivalente','ingreso':'Nuevos ingresos'}),hide_index=True,use_container_width=True)
    with st.expander('Cómo leer estos números'):
        for label,m in [('Matrícula equivalente anual','matricula_equivalente_anual'),('Nuevo ingreso observado','ingreso'),('Matrícula media observada','matricula')]:
            st.markdown(f'**{label}.** {definitions[m]}')
    st.caption('La ciudad corresponde a la sede reportada por SNIES, incluso en programas virtuales; no a la residencia del estudiante.')

def colombia_map(rows):
    fig=go.Figure()
    for f in geography()['features']:
        geom=f['geometry']; polys=geom['coordinates'] if geom['type']=='MultiPolygon' else [geom['coordinates']]
        for poly in polys:
            ring=poly[0]
            # Mainland and coastal islands. San Andrés is outside this view and has no matched offer.
            if min(p[0] for p in ring)<-80: continue
            fig.add_trace(go.Scatter(x=[p[0] for p in ring],y=[p[1] for p in ring],mode='lines',fill='toself',fillcolor='#E8EEF3',line=dict(color='white',width=.9),hoverinfo='skip',showlegend=False))
    g=rows.groupby('municipio').agg(valor=(metric,'sum'),ofertas=('id','nunique'),ies=('ies_id','nunique')).reset_index()
    g=g[g.municipio.isin(COORDS)]
    if len(g):
        sizes=14+50*np.sqrt(g.valor/max(g.valor.max(),1))
        fig.add_trace(go.Scatter(x=[COORDS[x][1] for x in g.municipio],y=[COORDS[x][0] for x in g.municipio],mode='markers+text',text=[CITY_NAMES.get(x,x) if x in CITY_COLORS else '' for x in g.municipio],textposition=['top left' if x in ['Medellín','Montería','Santiago de Cali'] else 'top right' for x in g.municipio],textfont=dict(size=14,color='#284760'),customdata=g[['municipio','valor','ofertas','ies']].to_numpy(),marker=dict(size=sizes,color=[CITY_COLORS.get(x,'#778A9B') for x in g.municipio],opacity=.9,line=dict(color='white',width=2)),selected=dict(marker=dict(opacity=1)),unselected=dict(marker=dict(opacity=.65)),hovertemplate='<b>%{customdata[0]}</b><br>'+metric_label+': %{customdata[1]:,.1f}<br>%{customdata[2]} ofertas · %{customdata[3]} universidades<br><b>Haz clic para ver programas y cifras</b><extra></extra>',showlegend=False))
    fig.update_layout(height=800,margin=dict(l=12,r=12,t=12,b=12),paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF',xaxis=dict(visible=False,range=[-79.2,-66.7],fixedrange=False),yaxis=dict(visible=False,range=[-4.5,12.8],scaleanchor='x',scaleratio=1.01),dragmode='pan',clickmode='event+select',hoverlabel=dict(bgcolor='#14283F',font_color='white'))
    fig.add_annotation(x=.96,y=.96,xref='paper',yref='paper',text='N<br>↑',showarrow=False,font=dict(size=15,color='#8195A9'))
    fig.add_annotation(x=.03,y=.04,xref='paper',yref='paper',text='COLOMBIA<br><span style="font-size:10px">Ubicación de oferta reportada</span>',showarrow=False,align='left',font=dict(size=11,color='#73899D'))
    return fig

if page=='Colombia 2025':
    title('Análisis de Mercado Programas CD','Distribución, escala y evolución de la formación universitaria en datos en Colombia.')
    st.markdown(f'<span class="pill">{html.escape(scope)}</span><span class="pill">SNIES {year}</span><span class="pill">{universe}</span>',unsafe_allow_html=True)
    st.caption('Haz clic en una ciudad o en su círculo para ver universidades, programas y cifras. El tamaño del círculo representa el indicador seleccionado; el color identifica la ciudad.')
    st.plotly_chart(colombia_map(current),use_container_width=True,key='mapa',on_select=remember_city,selection_mode='points',config={'displaylogo':False,'scrollZoom':False,'modeBarButtonsToRemove':['lasso2d','select2d']})
    clicked=st.session_state.pop('city_to_open',None)
    if clicked and clicked in current.municipio.values:
        city_detail(clicked,current)
    st.markdown(' '.join(f'<span class="pill" style="border-color:{color};color:{color}">{CITY_NAMES.get(city,city)}</span>' for city,color in CITY_COLORS.items() if city in current.municipio.values),unsafe_allow_html=True)
    st.caption('Burbujas proporcionales al indicador. Ubicación municipal aproximada, no ubicación de residencia del estudiante. La oferta virtual se asigna al municipio reportado por SNIES. Cartografía: geoBoundaries / OpenStreetMap (ODbL).')
    total=current[metric].sum(min_count=1)
    selected=current[current.ambito!='Resto del país'][metric].sum(min_count=1)
    if pd.isna(selected): selected=0
    share=selected/total if total else 0
    k1,k2,k3,k4=st.columns(4)
    with k1:
        card(f'{metric_label} · {year}',fmt(total,1 if metric!='ingreso' else 0),f'{fmt(current.snies.nunique())} códigos SNIES · {len(current)} ofertas municipales',True)
    with k2:
        card('G8 + referentes en esta selección',fmt(selected,1 if metric!='ingreso' else 0),f'{fmt(share*100,1)} % del indicador seleccionado')
    with k3:
        card('Nuevo ingreso observado',fmt(current.ingreso.sum(min_count=1)),f'Primer curso SNIES · {year}')
    with k4:
        card('EIA · Ciencia de Datos · 2026*','59','Dato interno del Director. Separado de SNIES 2025 y del modelo.',True)
    with st.expander('¿Qué significa cada indicador?',expanded=True):
        for label,m in [('Matrícula equivalente anual','matricula_equivalente_anual'),('Nuevo ingreso observado','ingreso'),('Matrícula media observada','matricula')]:
            st.markdown(f'**{label}.** {definitions[m]}')
        st.info('Para comparar el tamaño de los programas, usa matrícula. Para analizar la captación, usa nuevos ingresos. Las dos matrículas difieren cuando faltan reportes semestrales. Calculamos los promedios por programa y municipio y después los sumamos; no son personas únicas en todo el año.')
    if universe=='Mercado ampliado':
        st.info('El universo ampliado incorpora Ingeniería de Datos e Inteligencia Artificial. Para reproducir los 6.821 del Excel, selecciona “Benchmark v3 original”, Colombia, 2025 y matrícula equivalente anual.')
    section('Una categoría, dos espacios competitivos')
    c1,c2,c3=st.columns(3)
    with c1: st.markdown('<div class="mini-card"><h4 style="color:#087F8C">Directos</h4><p>Ciencia de Datos y sus ingenierías. En el universo ampliado también Ingeniería de Datos e Inteligencia Artificial.</p></div>',unsafe_allow_html=True)
    with c2: st.markdown('<div class="mini-card"><h4 style="color:#6262B5">Cercanos</h4><p>Estadística y actuariales, Ciencias de la Computación, Computación Científica, Ingeniería Matemática y MACC.</p></div>',unsafe_allow_html=True)
    with c3: st.markdown('<div class="mini-card"><h4>Alcance del estudio</h4><p>Pregrados universitarios. Se excluyen Sistemas, Software, Informática, licenciaturas, posgrados y educación continua.</p></div>',unsafe_allow_html=True)
    a,b=st.columns([1.1,1])
    with a:
        section('Composición del mercado',f'{metric_label} · {year}')
        g=current.groupby('segmento',as_index=False)[metric].sum()
        fig=px.bar(g,x='segmento',y=metric,color='segmento',color_discrete_map=COLORS,text_auto=',.0f',labels={'segmento':'',metric:metric_label});fig.update_layout(showlegend=False);chart(layout(fig,320))
    with b:
        section('Dónde se concentra',f'Departamento de oferta · {year}')
        g=current.groupby('departamento',as_index=False)[metric].sum().nlargest(7,metric).sort_values(metric)
        fig=px.bar(g,x=metric,y='departamento',orientation='h',text_auto=',.0f',color_discrete_sequence=['#315577'],labels={metric:metric_label,'departamento':''});chart(layout(fig,320))
    section('Explorar una ciudad')
    city=st.selectbox('Municipio',['Todos']+sorted(current.municipio.unique()),label_visibility='collapsed')
    detail=current if city=='Todos' else current[current.municipio==city]
    st.dataframe(detail[['alias','programa','snies','municipio','segmento',metric]].rename(columns={'alias':'Universidad','programa':'Programa','snies':'SNIES','municipio':'Municipio','segmento':'Segmento',metric:metric_label}),hide_index=True,use_container_width=True)

elif page=='Competidores':
    title('La posición competitiva','Comparaciones por institución, programa y entorno para orientar las decisiones de EIA.')
    st.caption(f'{scope} · {universe} · {year} · {metric_label}')
    section('Universidades de referencia','UNAL Medellín y UNAL Bogotá se muestran por separado. Sin registro comparable no implica ausencia de oferta universitaria.')
    selected=current[current.ambito!='Resto del país']
    aliases=[u['alias'] for u in meta['universidades'] if (scope!=SCOPES[2] or u['ambito']=='G8 Medellín') and (scope!=SCOPES[3] or u['ambito']=='Benchmark nacional')]
    ranking=selected.groupby(['alias','segmento'],as_index=False)[metric].sum()
    skeleton=pd.MultiIndex.from_product([aliases,segments],names=['alias','segmento']).to_frame(index=False)
    ranking=skeleton.merge(ranking,how='left',on=['alias','segmento']);ranking[metric]=ranking[metric].fillna(0)
    order=ranking.groupby('alias')[metric].sum().sort_values().index.tolist()
    fig=px.bar(ranking,x=metric,y='alias',color='segmento',orientation='h',color_discrete_map=COLORS,category_orders={'alias':order[::-1]},labels={'alias':'',metric:metric_label,'segmento':'Segmento'});chart(layout(fig,510))
    absent=[x for x in aliases if x not in selected.alias.unique()]
    if absent: st.caption('Sin registros directos/cercanos en la selección: '+', '.join(absent)+'.')
    section('Programas: captación frente a tamaño','Cada punto es un programa en un municipio. Pasa el cursor para identificarlo; no se unen observaciones independientes.')
    s=current.dropna(subset=['ingreso','matricula_equivalente_anual'])
    fig=px.scatter(s,x='ingreso',y='matricula_equivalente_anual',color='segmento',size='matricula_equivalente_anual',size_max=36,hover_name='alias',hover_data=['programa','snies','municipio','modalidad'],color_discrete_map=COLORS,labels={'ingreso':'Nuevo ingreso anual observado','matricula_equivalente_anual':'Matrícula equivalente anual','segmento':'Segmento'})
    chart(layout(fig,430))
    section('EIA en contexto: referencia entre años','EIA 2026* no es temporalmente comparable con SNIES 2025. Las barras no constituyen un ranking homogéneo.')
    comp=d[(d.anio==2025)&(d.ambito!='Resto del país')&(d.segmento=='Directo')][['alias','matricula_equivalente_anual']].copy()
    comp['Periodo']='SNIES 2025';comp.loc[len(comp)]=['EIA 2026*',59,'Interno 2026']
    fig=px.bar(comp,x='alias',y='matricula_equivalente_anual',color='Periodo',color_discrete_map={'SNIES 2025':'#A6B7C9','Interno 2026':'#087F8C'},text_auto='.1f',labels={'alias':'','matricula_equivalente_anual':'Estudiantes / equivalente anual'});chart(layout(fig,310))
    st.caption('*59 estudiantes reportados por el Director de Ciencia de Datos. Es un conteo interno de 2026; las otras cifras son promedios semestrales oficiales de 2025.')
    section('Cronología de los programas directos seleccionados','Fecha de registro no equivale al inicio de clases. La cronología es una referencia del benchmark v3, no un inventario nacional exhaustivo.')
    chrono=pd.read_json(ROOT/'data/cronologia.json')
    st.dataframe(chrono[['Universidad','Programa directo','Fecha registro calificado','Inicio / primera observación','Fuente']],column_config={'Fuente':st.column_config.LinkColumn('Fuente institucional')},hide_index=True,use_container_width=True)
    st.caption('Uniandes: inicio enero de 2027 verificado en su página institucional. UdeM y UPB: registros 2026 verificados. La condición de programa nuevo frente a transformación de oferta debe confirmarse antes de sumar capacidad incremental.')

elif page=='Evolución histórica':
    title('Cómo ha cambiado el mercado','Historia 2021–2025. Distingue expansión de oferta, nuevo ingreso y tamaño de los programas.')
    st.caption(f'{scope} · {universe}. Esta vista utiliza toda la serie 2021–2025, independientemente del año del panorama.')
    g=hist.groupby(['anio','segmento'],as_index=False)[metric].sum(min_count=1)
    fig=px.line(g,x='anio',y=metric,color='segmento',markers=True,color_discrete_map=COLORS,labels={'anio':'Año',metric:metric_label,'segmento':'Segmento'});fig.update_xaxes(dtick=1);chart(layout(fig,390))
    st.caption(definitions[metric]+' El universo anual es variable: el crecimiento puede reflejar nuevas ofertas, no solo crecimiento de programas existentes.')
    left,right=st.columns(2)
    with left:
        section('Crecimiento por programa','CAGR del indicador seleccionado, con período explícito. No se calcula con una sola observación ni base cero.')
        rates=cagr_table(hist,metric)
        valid=rates.dropna(subset=['CAGR']).sort_values('CAGR').tail(16)
        valid['Etiqueta']=valid.Universidad+' · '+valid.SNIES+' ('+valid.Inicio.astype(str)+'–'+valid.Fin.astype(str)+')'
        fig=px.bar(valid,x='CAGR',y='Etiqueta',color='Segmento',orientation='h',color_discrete_map=COLORS,hover_data=['Programa']);fig.update_xaxes(tickformat='.0%');chart(layout(fig,500))
    with right:
        section('Oferta observada','Número de códigos SNIES distintos por año. Las sedes municipales no duplican el conteo.')
        counts=hist.groupby(['anio','segmento']).snies.nunique().reset_index(name='Programas')
        fig=px.bar(counts,x='anio',y='Programas',color='segmento',color_discrete_map=COLORS,labels={'anio':'Año','segmento':'Segmento'});fig.update_xaxes(dtick=1);chart(layout(fig,300))
        st.markdown('<div class="insight"><b>Lectura para planeación</b><br>Una categoría puede crecer mientras algunos programas pierden captación. Contrasta las tendencias agregadas con el nuevo ingreso por programa antes de definir metas.</div>',unsafe_allow_html=True)
    section('Seguir un programa')
    options=hist[['id','alias','programa','municipio']].drop_duplicates('id'); options['label']=options.alias+' — '+options.programa+' · '+options.municipio
    pid=st.selectbox('Programa',options.id.tolist(),format_func=lambda x:options.set_index('id').loc[x,'label'])
    one=hist[hist.id==pid].set_index('anio').reindex(range(2021,2026)).reset_index()
    fig=go.Figure(go.Scatter(x=one.anio,y=one[metric],mode='lines+markers',connectgaps=False,line=dict(color='#087F8C',width=3),name=metric_label));fig.update_xaxes(dtick=1);chart(layout(fig,290))
    st.caption('Los años anteriores a la primera observación permanecen vacíos. Primera observación SNIES no acredita la fecha real de apertura.')
    st.dataframe(rates,column_config={'CAGR':st.column_config.NumberColumn(format='percent'),'YoY':st.column_config.NumberColumn(format='percent')},hide_index=True,use_container_width=True)

elif page=='Proyecciones 2030':
    title('Cinco años para explorar','Proyecciones 2026–2030 desde el último año observado: 2025.')
    st.caption(f'{scope} · {universe} · segmentos: {", ".join(segments)}. El modelo usa toda la serie histórica del indicador seleccionado.')
    c1,c2=st.columns([1,1.7])
    with c1: model=st.selectbox('Modelo',['Ridge','Lineal','Último valor'],help='Ridge: regresión lineal regularizada con α=1. Lineal: mínimos cuadrados. Último valor: baseline sin crecimiento.')
    with c2: adjustment=st.slider('Escenario adicional: cambio anual sobre la proyección (%)',-15,15,0,help='Supuesto de planeación manual, acumulativo desde 2026. No es un efecto estimado por el modelo.')
    ts=series(hist,metric); result=forecast(ts,model)
    if result is None: st.info('Se requieren al menos tres años observados para ajustar y validar.');st.stop()
    future=result['future'].copy();future['escenario']=future.base*(1+adjustment/100)**np.arange(1,6)
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=future.anio,y=future.superior,mode='lines',line=dict(width=0),showlegend=False,hoverinfo='skip'))
    fig.add_trace(go.Scatter(x=future.anio,y=future.inferior,fill='tonexty',fillcolor='rgba(8,127,140,.12)',mode='lines',line=dict(width=0),name='Banda orientativa ± MAE × √h',hoverinfo='skip'))
    fig.add_trace(go.Scatter(x=ts.index,y=ts.values,mode='lines+markers',name='Observado',line=dict(color='#213F5C',width=3)))
    fig.add_trace(go.Scatter(x=[2025]+future.anio.tolist(),y=[ts.iloc[-1]]+future.base.tolist(),mode='lines+markers',name=model,line=dict(color='#087F8C',width=3,dash='dash')))
    if adjustment:fig.add_trace(go.Scatter(x=future.anio,y=future.escenario,name=f'Escenario {adjustment:+d}% anual',mode='lines',line=dict(color='#B78247',dash='dot')))
    fig.add_vline(x=2025.5,line_dash='dot',line_color='#BAC7D4');fig.update_xaxes(dtick=1);fig.update_yaxes(title=metric_label);chart(layout(fig,435))
    a,b,c=st.columns(3)
    score=result['scores'].set_index('modelo').loc[model]
    with a: st.metric('Proyección base 2030',fmt(future.base.iloc[-1]))
    with b: st.metric('Error absoluto medio retrospectivo',fmt(score.MAE,1))
    with c: st.metric('WAPE retrospectivo',fmt(score.WAPE*100,1)+' %')
    st.warning('Escenario exploratorio: solo cinco observaciones anuales. La banda representa ± MAE retrospectivo × √h; no es un intervalo de confianza ni garantiza cobertura. No se incorporan automáticamente nuevas aperturas, cierres, demografía, precios o cambios de captación.')
    section('El modelo frente a una alternativa simple','Validación temporal expansiva: entrenar 2021–2022 y evaluar 2023; ampliar hasta 2023 y evaluar 2024; ampliar hasta 2024 y evaluar 2025. No hay mezcla aleatoria de años.')
    st.dataframe(result['scores'],hide_index=True,use_container_width=True,column_config={'MAE':st.column_config.NumberColumn(format='%.1f'),'WAPE':st.column_config.NumberColumn(format='percent')})
    best=result['scores'].iloc[0].modelo
    st.caption(f'Menor MAE retrospectivo: {best}. Estos tres errores sirven para comparar modelos, no son una evaluación independiente de un modelo seleccionado después de verlos. Se reentrena con 2021–2025 para proyectar. El ajuste interno R² de {model} es {fmt(result["r2"],3)} y no mide precisión futura.')
    section('Proyecciones por ámbito','Todos los ámbitos usan los mismos segmentos, taxonomía, indicador y modelo. Los ajustes son independientes; no deben sumarse entre sí.')
    group_rows=[]
    for sc in SCOPES:
        q=forecast(series(select_scope(base[base.segmento.isin(segments)],sc),metric),model)
        if q:
            group_rows.append({'Ámbito':sc,**{str(int(row.anio)):round(row.base,1) for row in q['future'].itertuples()}})
    st.dataframe(pd.DataFrame(group_rows),hide_index=True,use_container_width=True)
    with st.expander('Detalle de validación y ecuación'):
        st.markdown('**Modelo Ridge:** y = intercepto + pendiente × año centrado. Se minimiza el error cuadrático más α × pendiente², con α = 1 fijado antes de evaluar. El intercepto no se penaliza y las predicciones negativas se truncan en cero. No se añaden estudiantes de EIA 2026 a los datos de entrenamiento.')
        st.dataframe(result['backtest'],hide_index=True,use_container_width=True)
    future['modelo']=model;future['ambito']=scope;future['indicador']=metric_label;future['universo']=universe;future['ajuste_anual_pct']=adjustment
    st.download_button('Descargar proyección y escenario · CSV',future.to_csv(index=False).encode('utf-8-sig'),'proyeccion_2026_2030.csv','text/csv')

else:
    title('Datos, método y trazabilidad','Los resultados pueden reconstruirse desde los archivos originales, con reglas explícitas y hallazgos de auditoría.')
    a,b,c=st.columns(3)
    with a:st.metric('Archivos SNIES procesados','10')
    with b:st.metric('Registros históricos v3 conciliados',fmt(meta['filas_crudas_verificadas']))
    with c:st.metric('Diferencias en esos registros',str(len(meta['diferencias_crudos'])))
    section('Qué cambió al reconstruir el análisis')
    st.markdown('''1. **Histórico de las universidades objetivo:** los 450 registros coinciden con los originales. La serie de nuevo ingreso es 617, 657, 718, 807 y 794.
2. **Universo nacional:** el v3 incluye 47 ofertas municipales y 46 códigos SNIES. El ampliado añade 4 ofertas de Ingeniería de Datos e Inteligencia Artificial (3 códigos SNIES): Santo Tomás en Bogotá y Tunja, Autónoma de Occidente y ESEIT.
3. **Semestres ausentes:** siete celdas del v3 usan cero sin una fila correspondiente en la fuente. Aquí se conserva la ausencia en el detalle. UNAB tiene matrícula solo en 2025-2: 7 reportados; equivalente anual 3,5.
4. **Dos lecturas de matrícula:** el equivalente anual divide entre dos y reproduce los 6.821 del v3. La media de semestres observados suma 6.824,5. En el universo ampliado, son 7.322 y 7.363 respectivamente.
5. **Gráficas:** se recalculan desde los datos auditados. Los vacíos históricos no se conectan como ceros, el CAGR muestra su período y EIA 2026 permanece separado.''')
    with st.expander('Definiciones y límites',expanded=True):
        for label,m in [('Matrícula equivalente anual','matricula_equivalente_anual'),('Nuevo ingreso observado','ingreso'),('Matrícula media observada','matricula')]:st.markdown(f'**{label}.** {definitions[m]}')
        st.markdown('**Unidad:** institución + código SNIES + municipio + año + semestre. Se agregan los sexos antes de calcular indicadores. Un código con dos municipios es un programa y dos ofertas municipales. **Geografía:** municipio de oferta, no residencia; virtual no equivale a demanda local. **Ausencia:** sin fila no prueba cero ni cierre. **Universidades objetivo:** se conservan los filtros por municipio de la conversación y del v3; otras sedes de la misma institución quedan en el resto del país.')
    section('Conciliación del universo original')
    audit=pd.read_csv(ROOT/'data/conciliacion.csv')
    only=st.toggle('Mostrar solo observaciones de auditoría',value=True)
    st.dataframe(audit[audit.estado!='Coincide'] if only else audit,hide_index=True,use_container_width=True)
    st.caption('Las 275 celdas con dato fuente comparable coinciden; siete celdas están marcadas como “Sin registro fuente”. El cero usado para reproducir el equivalente no se presenta como cero reportado.')
    section('Datos del indicador seleccionado')
    st.dataframe(current.drop(columns=['ies_id','municipio_id']),hide_index=True,use_container_width=True)
    st.download_button('Descargar selección · CSV',current.to_csv(index=False).encode('utf-8-sig'),f'snies_seleccion_{year}.csv','text/csv')
    with st.expander('Inventario de fuentes y huellas SHA-256'):
        st.dataframe(pd.DataFrame(meta['fuentes']),hide_index=True,use_container_width=True)
        st.markdown('[SNIES · Bases consolidadas](https://snies.mineducacion.gov.co/portal/ESTADISTICAS/Bases-consolidadas/) · [geoBoundaries · Colombia](https://www.geoboundaries.org/api/current/gbOpen/COL/ADM1/)')
        st.caption('Los archivos SNIES suministrados son la fuente cuantitativa; no se sustituyen por cifras web. El benchmark v3 se conserva intacto como referencia descargable.')

st.markdown('<div class="rule"></div>',unsafe_allow_html=True)
section('Llevar el análisis a la reunión','Descargas completas del estudio. El informe y los Excel no cambian con los filtros de pantalla; los CSV sí reflejan la selección indicada.')
cols=st.columns(3)
with cols[0]:
    pdf=ROOT/'downloads/informe_ejecutivo_eia.pdf'
    if pdf.exists():st.download_button('Informe ejecutivo · PDF',pdf.read_bytes(),pdf.name,'application/pdf',use_container_width=True)
with cols[1]:
    f=ROOT/'data/benchmark_ciencia_datos_v3_completo.xlsx';st.download_button('Benchmark original v3 · Excel',f.read_bytes(),f.name,'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)
with cols[2]:
    f=ROOT/'downloads/analisis_auditado_eia.xlsx'
    if f.exists():st.download_button('Datos auditados y proyección · Excel',f.read_bytes(),f.name,'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)
st.markdown('<div class="footer">UNIVERSIDAD EIA &nbsp; / &nbsp; DIRECCIÓN DE CIENCIA DE DATOS &nbsp; / &nbsp; SNIES 2021–2025 · EIA 2026* · PROYECCIÓN 2026–2030</div>',unsafe_allow_html=True)
