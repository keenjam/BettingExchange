import statsmodels.api as sm
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.graphics.gofplots import qqplot_2samples

fig, ax = plt.subplots()

x = np.array([0.2938*5000, 0.205*5000, 0.1532*5000, 0.1092*5000, 0.077*5000, 0.0598*5000, 0.0522*5000, 0.0498*5000])
y = np.array([0.354*5000, 0.216*5000, 0.144*5000, 0.109*5000, 0.0706*5000, 0.058*5000, 0.028*5000, 0.016*5000])


# pp_x = sm.ProbPlot(x)
# pp_y = ProbPlot(y)
qqplot_2samples(x, y, ax=ax)

x = np.linspace(*ax.get_xlim())
ax.plot(x, x)

plt.xlabel("Quantiles of wins in BBE")
plt.ylabel("Quantiles of wins in real horse race-events")
plt.show()
