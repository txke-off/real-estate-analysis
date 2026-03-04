import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import mapclassify

df = pd.read_csv("flats.csv", sep=";")
df['price'] = df['price'].str.replace(" ", "").str.replace("₽", "").astype(int)
df['area'] = df['area'].str.replace(",", ".").astype(float)
df['price_per_m2'] = df['price'].astype(int) / df['area'].astype(int)
df['floor'] = df['floor'].astype(int)
df['max_floor'] = df['max_floor'].astype(int)
df = df[df['rooms'].isin(["Студия", "1", "2", "3", "4", "5", "6"])]

plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x='rooms', y='price', order=['Студия', '1', '2', '3', '4', '5', '6'])
plt.title('Распределение цен квартир по количеству комнат')
plt.xlabel('Количество комнат')
plt.ylabel('Цена')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()

Q1 = df['price'].quantile(0.25)
Q3 = df['price'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
df = df[(df['price'] >= lower_bound) & (df['price'] <= upper_bound)]

df['price'].plot.hist(bins=100, title='Распределение цен')
plt.xlabel('Значение')
plt.ylabel('Частота')
plt.show()

plt.scatter(df['price'], df['area'])
plt.title("Зависимость цены от площади")
plt.xlabel("Цена")
plt.ylabel("Площадь")
plt.show()

plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x='floor', y='price_per_m2')
plt.title("Зависимость цены от этажа")
plt.xlabel("Этаж")
plt.ylabel("Цена/м²")
plt.show()

mapping = {
    'р-н Адмиралтейский': 'Адмиралтейский район',
    'р-н Василеостровский': 'Василеостровский район',
    'р-н Выборгский': 'Выборгский район',
    'р-н Калининский': 'Калининский район',
    'р-н Кировский': 'Кировский район',
    'р-н Колпинский': 'Колпинский район',
    'р-н Красногвардейский': 'Красногвардейский район',
    'р-н Красносельский': 'Красносельский район',
    'р-н Кронштадтский': 'Кронштадт',
    'р-н Курортный': 'Курортный район',
    'р-н Московский': 'Московский район',
    'р-н Невский': 'Невский район',
    'р-н Петроградский': 'Петроградский район',
    'р-н Петродворцовый': 'Петродворцовый район',
    'р-н Приморский': 'Приморский район',
    'р-н Пушкинский': 'Пушкинский район',
    'р-н Фрунзенский': 'Фрунзенский район',
    'р-н Центральный': 'Центральный район'
}

df['name'] = df['region'].map(mapping)
df_agg = df.groupby('name')['price_per_m2'].mean().reset_index()
regions_gdf = gpd.read_file('export.geojson')
merged_gdf = regions_gdf.merge(df_agg, on='name')

fig, ax = plt.subplots(1, 1, figsize=(12, 12))

merged_gdf.plot(
    column='price_per_m2',
    cmap='RdYlGn_r',
    legend=True,
    legend_kwds={'label': 'Цена за м² (руб.)', 'orientation': 'horizontal'},
    edgecolor='black',
    linewidth=0.5,
    ax=ax
)

ax.set_aspect('equal')
ax.set_title('Стоимость жилья по районам Санкт-Петербурга', fontsize=16)
plt.tight_layout()
plt.savefig('choropleth.png', dpi=300)
plt.show()
