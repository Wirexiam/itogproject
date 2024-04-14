# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Загрузка данных
@st.cache
def load_data():
    zp_data = pd.read_excel("zp.xlsx")
    inf_year_data = pd.read_excel("inf_year.xlsx")
    inf_month_data = pd.read_excel("inf_month.xlsx")

    # Преобразование данных о зарплате
    zp_long = zp_data.melt(id_vars=["Категория"], var_name="Год", value_name="Номинальная_ЗП")
    zp_long["Год"] = zp_long["Год"].astype(int)

    # Используем годовую инфляцию
    inf_year_simple = inf_year_data[["Год", "Всего"]].rename(columns={"Всего": "Годовой_коэф_инфляции"})
    inf_year_simple["Год"] = inf_year_simple["Год"].astype(int)

    # Объединение данных
    zp_inflation = pd.merge(zp_long, inf_year_simple, on="Год")
    zp_inflation["Реальная_ЗП"] = zp_inflation["Номинальная_ЗП"] / (1 + zp_inflation["Годовой_коэф_инфляции"] / 100)

    # Для месячной инфляции
    inf_month_summary = inf_month_data.melt(id_vars=["Год"], var_name="Месяц", value_name="Месячная_инфляция")
    inf_month_summary = inf_month_summary.groupby("Год").agg({'Месячная_инфляция': 'sum'}).reset_index()

    return zp_inflation, inf_month_summary


zp_inflation, inf_month_summary = load_data()
#В ыбор категории
category = st.selectbox("Выберите категорию для анализа месячной инфляции:", ["Образование", "Строительство"])

# Отображение соответствующего текста в зависимости от выбранной категории
if category == "Строительство":
    st.write("""
    **Для сектора "Строительство":**
    - Значительный рост реальной заработной платы можно наблюдать с 2000 по 2023 год, что указывает на увеличение покупательной способности заработной платы в этом секторе.
    - Красная линия показывает несколько пиков, особенно заметных примерно в 2010 и 2020 годах, что свидетельствует о более высоком инфляционном давлении в эти периоды. Несмотря на это, столбцы заработной платы продолжали расти, что говорит о том, что увеличение номинальной заработной платы компенсировало инфляцию.
    """)
elif category == "Образование":

    st.write("""
    **Для сектора "Образование":**
    - Подобно сектору "Строительство", реальная заработная плата в "Образовании" также показывает рост с течением времени, хотя и с меньшей амплитудой по сравнению со "Строительством".
    - Пики красной линии инфляции также заметны в те же периоды. Однако стоит отметить, что в некоторые годы столбцы реальной заработной платы увеличивались менее значительно или даже снижались (например, около 2010 года), что может указывать на то, что заработная плата в "Образовании" не всегда удерживала шаг с инфляцией.
    """)

# Графики
st.title("Реальная заработная плата по категориям")
filtered_data = zp_inflation[zp_inflation["Категория"] != "Всего"]
fig, ax = plt.subplots()
sns.barplot(data=filtered_data, x="Год", y="Реальная_ЗП", hue="Категория", palette="viridis", ax=ax)
ax.set_title('Реальная заработная плата по категориям с учетом годовой инфляции')
ax.set_ylabel('Реальная заработная плата')
ax.set_xlabel('Год')
plt.xticks(rotation=30) # Поворот меток на 30 градусов
plt.xticks(fontsize=5) # Уменьшение размера шрифта меток
st.pyplot(fig)

cat_data = zp_inflation[zp_inflation["Категория"] == category]
cat_inflation = pd.merge(cat_data, inf_month_summary, on="Год")

# Второй график
fig, ax1 = plt.subplots()
ax1.bar(cat_inflation["Год"], cat_inflation["Реальная_ЗП"], color='tab:blue')
ax1.set_ylabel('Реальная заработная плата', color='tab:blue')
ax1.set_title(f'Реальная заработная плата и месячная инфляция ({category})')
ax1.set_xlabel('Год')

ax2 = ax1.twinx()
ax2.plot(cat_inflation["Год"], cat_inflation["Месячная_инфляция"], color='tab:red', marker='o')
ax2.set_ylabel('Сумма месячной инфляции', color='tab:red')
st.pyplot(fig)
