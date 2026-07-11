import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from scipy.stats import t as stud_t
t_intervals = 90    # 90 days into the future
iterations = 10000  # 10,000 separate scenarios

data = yf.download("AAPL", start="2026-01-01", end="2026-07-10")

data["Returns"] = np.log(data['Close']/data['Close'].shift(1))

data = data.dropna()

df_param, mean_param, vol_param = stud_t.fit(data["Returns"])

print(f"Estimated Degrees of Freedom (Tail Heaviness): {df_param:.2f}")

random_shocks = stud_t.rvs(df=df_param, loc=mean_param, scale=vol_param, size=(t_intervals, iterations))
d_growth_f = np.exp(random_shocks)
S0 = float(data['Close'].values[-1, 0])
price_list = np.zeros_like(d_growth_f)
price_list[0] = S0
for t in range(1,t_intervals):
    price_list[t] = price_list[t-1] * d_growth_f[t]
print (price_list)

average_price = np.zeros(t_intervals)
for i in range(t_intervals):
    average_price[i] = price_list[i].mean()

#Probability of profit in t_intervals days
end_price  = price_list[-1]
prob_of_profit = 0
for i in range(iterations):
    if end_price[i] > S0:
        prob_of_profit += 1/iterations
print("Probability of profit:", prob_of_profit)


#VaR
conf_prob = float(input("Confidence probability: "))
sorted_prices = np.sort(end_price)
var_index = int((1-conf_prob)*iterations)
var_price = sorted_prices[var_index]

var_dollars = S0 - var_price
var_percentage = (var_dollars / S0) * 100

print(conf_prob*100, f"% 90-Day VaR: ${var_dollars:.2f} ({-var_percentage:.2f}%)")

#CVaR
tail_prices = sorted_prices[:var_index]
es_price = np.mean(tail_prices)
es_var_dollars = S0 - es_price
es_var_percentage = (es_var_dollars / S0) * 100
print(conf_prob*100, f"% 90-Day Expected Shortfall (Average Tail Loss): ${es_var_dollars:.2f} ({-es_var_percentage:.2f}%)")


#Plot
plt.figure(figsize=(10, 6))

plt.plot(price_list, lw=0.5, color='blue' )
plt.plot(average_price, lw=3.5, color='red', label='Average Price')

plt.title("Monte Carlo Simulation: AAPL Stock Price Prediction")
plt.xlabel("Days into the Future")
plt.ylabel("Stock Price ($)")
#plt.grid(True)

plt.show()