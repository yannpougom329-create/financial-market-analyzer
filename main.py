import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
def backtest(ticker):
    action = yf.Ticker(ticker)
    data = action.history(period="1y")
    meilleure_performance = float("-inf")
    meilleure_ma_courte = None
    meilleure_ma_longue = None
    resultats = []
    for ma_courte in [10, 20, 30]:
        for ma_longue in [50, 100, 200]:
            print(ma_courte,ma_longue)
            data["MA_courte"] = data["Close"].rolling(window=ma_courte).mean() 
            data["MA_longue"] = data["Close"].rolling(window=ma_longue).mean() 
    data["signal"]= 0
    data.loc[data["MA_courte"] > data["MA_longue"], "signal"] = 1
    data["position"] = data["signal"].diff()
    frais = 0.001
    data["frais"] = 0.0
    data.loc[data["position"] != 0, "frais"]= frais
    data["Retour"] = data["Close"].pct_change()
    data["Retour_strategie"] = data["Retour"] * data["signal"].shift(1)
    data["Retour_strategie_net"] = data["Retour_strategie"] - data["frais"]
    data["performance_buyhold"] = (1 + data["Retour"]).cumprod()
    performance_buyhold = data["performance_buyhold"].iloc[-1]
    performance_strategie = (1 + data["Retour_strategie"]).cumprod().iloc[-1]
    performance_strategie_net= (1 + data["Retour_strategie_net"]).cumprod().iloc[-1]
    resultats.append({
          "MA_courte" : ma_courte,
          "MA_longue" : ma_longue,
          "Performance" : performance_strategie_net
    })
    resultats = pd.DataFrame(resultats)
    resultats = resultats.sort_values("Performance", ascending=False)
    print(resultats.head(10))
    if performance_strategie_net > meilleure_performance:
               meilleure_performance = performance_strategie_net
               meilleure_ma_courte = ma_courte
               meilleure_ma_longue = ma_longue
    print("meilleur moyenne courte:", meilleure_ma_courte)
    print("meilleur moyenne longue:", meilleure_ma_longue)
    print("meilleur performance", meilleure_performance)
    print(f"performance buy & hold : {performance_buyhold:.2f}")
    print(f"performance strategie : {performance_strategie:.2f}")
    print("performance de la statégie :",
      (1 + data["Retour_strategie"]).cumprod().iloc[-1]) 
    capital_initial = 10000
    data["capital_buyhold"] = capital_initial * (1 + data["Retour"]).cumprod()
    data["capital_strategie"] = capital_initial *(1 + data["Retour_strategie"]).cumprod()
    print(data[["capital_buyhold", "capital_strategie"]].tail(10))
    nbre_jours = len(data)
    performance_annuelle = ((1 + data["Retour_strategie"].cumprod().iloc[-1])** (252 / nbre_jours) -1)
    print(f"performance annuelle : {performance_annuelle*100:.2f}%")
    volatilité = data["Retour_strategie"].std() * (252 ** 0.5)
    print(f"Volatilité : {volatilité*100:.2f}%")
    sharpe = performance_annuelle / volatilité
    print(f"sharpe ratio : {sharpe:.2f}")
    capital = (1 + data["Retour_strategie"]).cumprod()
    plus_haut =capital.cummax()
    drawdown = (capital - plus_haut) / plus_haut
    drawdown_max = drawdown.min()
    print(f"drawdown maximal: {drawdown_max*100:.2f}%")
    print(data.tail(20))
    plt.figure(figsize=(12,6))
    plt.plot(data.index, data["Close"], label="prix")
    plt.plot(data.index, data["MA_courte"], label=["MA_courte"])
    plt.plot(data.index, data["MA_longue"], label=["MA_longue"])
    plt.title("Prix de l'action")
    plt.xlabel("date")
    plt.ylabel("prix ($)")
    plt.scatter(data.index[data["position"] == 1],
       data["Close"][data["position"] == 1],
       marker="^",
       color="green",
       s=100,
       label="achat")
    plt.scatter(data.index[data["position"] == -1],
       data["Close"][data["position"] == -1],
       marker="v",
       color="red",
       s=100,
       label="vente")
    plt.figure(figsize=(12,6))
    plt.plot(data.index, data["capital_buyhold"], label="buy & hold")
    plt.plot(data.index, data["capital_strategie"], label="strategie")
    plt.title("comparaison des performances")
    plt.xlabel("date")
    plt.ylabel("capital (£)")
    plt.legend()
    plt.show()
backtest("AAPL")