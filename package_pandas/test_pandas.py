import io, pandas
data = """col1,col2
1,3
2,4
3,6
4,7"""
df = pandas.read_csv(io.StringIO(data))
print(df)
import matplotlib.pyplot as plt 
plt.plot(df.col1, df.col2)
plt.show()