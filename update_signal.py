import json,pathlib,yfinance as yf

def rsi_wilder(s,n=14):
 d=s.diff();g=d.clip(lower=0);l=-d.clip(upper=0);ag=g.ewm(alpha=1/n,adjust=False,min_periods=n).mean();al=l.ewm(alpha=1/n,adjust=False,min_periods=n).mean();return 100-100/(1+ag/al)
q=yf.download("QQQ",period="2y",auto_adjust=True,progress=False);v=yf.download("^VIX",period="1mo",auto_adjust=True,progress=False)
qc=q["Close"].squeeze().dropna();vc=v["Close"].squeeze().dropna();ma=qc.rolling(175).mean();r=rsi_wilder(qc)
p=float(qc.iloc[-1]);m=float(ma.iloc[-1]);rv=float(r.iloc[-1]);vv=float(vc.iloc[-1])
if vv>=40:sig,reason,t,l="위험회피","VIX 40 이상 — 신규 레버리지 매수 제한",0,0
elif p<=m:sig,reason,t,l="매도·방어","QQQ가 SMA175 이하",0,30
elif rv>55:sig,reason,t,l="보유·완만매수","상승추세이나 RSI가 높은 구간",50,20
elif rv>=40:sig,reason,t,l="매수","QQQ 상승추세 + 정상 RSI",60,20
elif rv>=30:sig,reason,t,l="강력매수 후보","상승추세 내 조정 구간",70,20
else:sig,reason,t,l="매수축소","극단적 과매도 — 현금 소진 방지",40,20
d={"date":str(qc.index[-1].date()),"signal":sig,"reason":reason,"qqq":round(p,2),"sma":round(m,2),"rsi":round(rv,1),"vix":round(vv,1),"tqqq_pct":t,"qld_pct":l,"cash_pct":100-t-l}
pathlib.Path("data").mkdir(exist_ok=True);pathlib.Path("data/signal.json").write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8");print(d)
