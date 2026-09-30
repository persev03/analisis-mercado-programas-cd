"""Shared calculations used by Streamlit, tests and downloadable report."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).parent
SCOPES=['Colombia','G8 + referentes nacionales','G8 Medellín','Referentes nacionales']
COLORS={'Directo':'#087F8C','Cercano':'#6262B5'}

def load_data():
    d=pd.read_csv(ROOT/'data/anual.csv',dtype={'id':str,'snies':str,'municipio_id':str,'ies_id':str})
    meta=json.loads((ROOT/'data/metadata.json').read_text())
    return d,meta

def select_scope(d,scope):
    if scope==SCOPES[1]: return d[d.ambito!='Resto del país'].copy()
    if scope==SCOPES[2]: return d[d.ambito=='G8 Medellín'].copy()
    if scope==SCOPES[3]: return d[d.ambito=='Benchmark nacional'].copy()
    return d.copy()

def series(d,metric='ingreso'):
    return d.groupby('anio')[metric].sum(min_count=1).sort_index()

def predict_model(years,values,future,model='Ridge'):
    x=np.asarray(years,dtype=float); y=np.asarray(values,dtype=float); z=np.asarray(future,dtype=float)
    if model=='Último valor': return np.repeat(max(0,y[-1]),len(z))
    xc=x-x.mean()
    # Ridge on a centered annual time feature, unpenalized intercept; fixed alpha = 1.
    alpha=1.0 if model=='Ridge' else 0.0
    slope=float(xc@(y-y.mean())/(xc@xc+alpha))
    return np.maximum(0,y.mean()+slope*(z-x.mean()))

def forecast(s,model='Ridge',horizon=5):
    s=s.dropna(); x=s.index.to_numpy(dtype=int); y=s.to_numpy(dtype=float)
    if len(s)<3: return None
    rows=[]
    for candidate in ['Ridge','Lineal','Último valor']:
        for i in range(2,len(s)):
            p=float(predict_model(x[:i],y[:i],[x[i]],candidate)[0])
            rows.append(dict(modelo=candidate,anio=int(x[i]),observado=float(y[i]),prediccion=p,error_absoluto=abs(float(y[i])-p)))
    back=pd.DataFrame(rows)
    scores=back.groupby('modelo').agg(MAE=('error_absoluto','mean'),error_total=('error_absoluto','sum'),observado_total=('observado','sum')).reset_index()
    scores['WAPE']=scores.error_total/scores.observado_total.replace(0,np.nan)
    scores=scores[['modelo','MAE','WAPE']].sort_values('MAE')
    years=np.arange(x[-1]+1,x[-1]+horizon+1)
    pred=predict_model(x,y,years,model)
    mae=float(scores.set_index('modelo').loc[model,'MAE'])
    spread=mae*np.sqrt(np.arange(1,horizon+1))
    future=pd.DataFrame(dict(anio=years,base=pred,inferior=np.maximum(0,pred-spread),superior=pred+spread))
    fit=predict_model(x,y,x,model); denom=((y-y.mean())**2).sum()
    return dict(future=future,scores=scores,backtest=back,r2=None if denom==0 else 1-float(((y-fit)**2).sum()/denom),model=model,n=len(s))

def cagr_table(d,metric='ingreso'):
    records=[]
    for pid,g in d.groupby('id'):
        g=g.sort_values('anio').dropna(subset=[metric]); last=g.iloc[-1] if len(g) else None
        if last is None: continue
        first=g.iloc[0]; span=int(last.anio-first.anio)
        # Do not manufacture a growth rate with one observation or a zero base.
        rate=(float(last[metric])/float(first[metric]))**(1/span)-1 if span>0 and first[metric]>0 else np.nan
        prev=g[g.anio==last.anio-1]
        yoy=float(last[metric]/prev.iloc[0][metric]-1) if len(prev) and prev.iloc[0][metric]>0 else np.nan
        records.append(dict(id=pid,Universidad=last.alias,Programa=last.programa,SNIES=last.snies,Segmento=last.segmento,Inicio=int(first.anio),Fin=int(last.anio),CAGR=rate,YoY=yoy,Último=float(last[metric]),Observaciones=len(g)))
    return pd.DataFrame(records)

def fmt(n,dec=0):
    if n is None or pd.isna(n): return '—'
    return f'{n:,.{dec}f}'.replace(',','X').replace('.',',').replace('X','.')

def metric_value(d,metric):
    return d[metric].sum(min_count=1)

