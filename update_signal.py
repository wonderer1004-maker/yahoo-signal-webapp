import json,pathlib,yfinance as yf
def close(df):
 return df["Close"].squeeze().dropna()
def atr(df,n=14):
 h=df["High"].squeeze();l=df["Low"].squeeze();c=close(df);pc=c.shift(1)
 tr=(h-l).to_frame("a").join((h-pc).abs().rename("b")).join((l-pc).abs().rename("c")).max(axis=1)
 return float(tr.ewm(alpha=1/n,adjust=False,min_periods=n).mean().iloc[-1])
def rsi(s,n=14):
 d=s.diff();up=d.clip(lower=0);down=-d.clip(upper=0);a=up.ewm(alpha=1/n,adjust=False,min_periods=n).mean();b=down.ewm(alpha=1/n,adjust=False,min_periods=n).mean()
 return float((100-100/(1+a/b)).iloc[-1])
def get(ticker,period):
 df=yf.download(ticker,period=period,auto_adjust=True,progress=False)
 if df.empty:raise RuntimeError("No Yahoo data for "+ticker)
 return df
q=get("QQQ","2y");v=get("^VIX","1mo");qc=close(q);p=float(qc.iloc[-1]);m=float(qc.rolling(175).mean().iloc[-1]);rv=rsi(qc);vv=float(close(v).iloc[-1])
if vv>=40:sig,reason,t,l="위험회피","VIX 40 이상: 신규 레버리지 매수 제한",0,0
elif p<=m:sig,reason,t,l="매도·방어","QQQ 종가가 SMA175 이하",0,30
elif rv>55:sig,reason,t,l="보유·완만매수","상승추세, RSI 높은 구간",50,20
elif rv>=40:sig,reason,t,l="매수","상승추세, 정상 RSI",60,20
elif rv>=30:sig,reason,t,l="강력매수 후보","상승추세 내 조정",70,20
else:sig,reason,t,l="매수축소","과매도, 현금 소진 방지",40,20
targets={}
for ticker in ["TQQQ","QLD","QQQ"]:
 df=q if ticker=="QQQ" else get(ticker,"3mo")
 price=float(close(df).iloc[-1]);a=atr(df)
 stop=max(0.01,price-2*a);one=price+2*a;two=price+4*a
 targets[ticker]={"price":round(price,2),"entry":round(price,2),"stop":round(stop,2),"target1":round(one,2),"target2":round(two,2),"atr":round(a,2),"target1_pct":round((one/price-1)*100,2),"stop_pct":round((1-stop/price)*100,2)}
d={"date":str(qc.index[-1].date()),"signal":sig,"reason":reason,"qqq":round(p,2),"sma":round(m,2),"rsi":round(rv,1),"vix":round(vv,1),"sma_gap_pct":round((p/m-1)*100,2),"tqqq_pct":t,"qld_pct":l,"cash_pct":100-t-l,"targets":targets}
pathlib.Path("data").mkdir(exist_ok=True);pathlib.Path("data/signal.json").write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8");print(d)
