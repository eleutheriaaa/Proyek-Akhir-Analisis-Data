import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import folium
from streamlit_folium import folium_static

sns.set(style='dark')

all_df = pd.read_csv("Dashboard/all_data.csv")

all_df["datetime"] = pd.to_datetime(all_df[["year", "month", "day", "hour"]])

station_coords = {
    "Dongsi": [39.929, 116.417],
    "Gucheng": [39.928, 116.342],
    "Huairou": [40.316, 116.637]
}

# Sidebar untuk filter
st.sidebar.header("Filter Data")
lokasi = st.sidebar.multiselect("Pilih Lokasi", all_df["station"].unique(), all_df["station"].unique())
tahun = st.sidebar.multiselect("Pilih Tahun", all_df["year"].astype(str).unique(), all_df["year"].astype(str).unique())

filtered_df = all_df[(all_df["station"].isin(lokasi)) & (all_df["year"].astype(str).isin(tahun))]


st.title("Dashboard Kualitas Udara")
st.markdown("Melihat tren kualitas udara berdasarkan lokasi dan waktu.")
st.markdown("Nathanael Dennis Gunawan")
st.markdown("MC325D5Y2201")


if not filtered_df.empty:
    # Visualisasi Tren PM2.5
    st.subheader("Tren PM2.5 di Tiga Lokasi")
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=filtered_df, x="year", y="PM2.5", hue="station", marker="o")
    plt.xlabel("Tahun")
    plt.ylabel("Konsentrasi PM2.5")
    plt.title("Tren PM2.5 dari 2013-2017")
    st.pyplot(plt)

    # Korelasi antara PM2.5 dan Faktor Meteorologi
    st.subheader("Korelasi antara PM2.5 dan Faktor Meteorologi")
    plt.figure(figsize=(10, 6))
    correlation_matrix = filtered_df[["PM2.5", "TEMP", "PRES", "DEWP"]].corr()
    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f")
    st.pyplot(plt)

    # Tren PM10 di tiga lokasi
    st.subheader("Tren PM10 di Tiga Lokasi")
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=filtered_df, x="year", y="PM10", hue="station", marker="o")
    plt.xlabel("Tahun")
    plt.ylabel("Konsentrasi PM10")
    plt.title("Tren PM10 dari 2013-2017")
    st.pyplot(plt)

    # Menampilkan tren SO2, NO2, CO, dan O3
    st.subheader("Tren Polutan di Tiga Lokasi")
    pollutants = ["SO2", "NO2", "CO", "O3"]
    titles = ["Tren SO2", "Tren NO2", "Tren CO", "Tren O3"]
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    for i, ax in enumerate(axes.flat):
        sns.lineplot(data=filtered_df, x="year", y=pollutants[i], hue="station", marker="o", ax=ax)
        ax.set_title(f"{titles[i]} di Tiga Lokasi (2013-2017)")
        ax.set_xlabel("Tahun")
        ax.set_ylabel(f"Konsentrasi {pollutants[i]}")
    
    plt.tight_layout()
    st.pyplot(fig)

    # Box plot untuk PM2.5 terhadap Suhu, Tekanan Udara, dan Kelembapan
    st.subheader("Distribusi PM2.5 berdasarkan Suhu, Tekanan Udara, dan Kelembapan")
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Box plot PM2.5 vs Suhu (TEMP)
    sns.boxplot(data=filtered_df, x=pd.cut(filtered_df["TEMP"], bins=10), y="PM2.5", ax=axes[0])
    axes[0].set_xticklabels(axes[0].get_xticklabels(), rotation=45)
    axes[0].set_title("Distribusi PM2.5 berdasarkan Suhu")
    axes[0].set_xlabel("Suhu")
    axes[0].set_ylabel("PM2.5")

    # Box plot PM2.5 vs Tekanan Udara (PRES)
    sns.boxplot(data=filtered_df, x=pd.cut(filtered_df["PRES"], bins=10), y="PM2.5", ax=axes[1])
    axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=45)
    axes[1].set_title("Distribusi PM2.5 berdasarkan Tekanan Udara")
    axes[1].set_xlabel("Tekanan Udara")
    axes[1].set_ylabel("PM2.5")

    # Box plot PM2.5 vs Kelembapan (DEWP)
    sns.boxplot(data=filtered_df, x=pd.cut(filtered_df["DEWP"], bins=10), y="PM2.5", ax=axes[2])
    axes[2].set_xticklabels(axes[2].get_xticklabels(), rotation=45)
    axes[2].set_title("Distribusi PM2.5 berdasarkan Kelembapan")
    axes[2].set_xlabel("Kelembapan")
    axes[2].set_ylabel("PM2.5")

    st.pyplot(fig)

    # Peta pengamatan
    st.subheader("Peta Stasiun Pengamatan")
    peta = folium.Map(location=[39.9, 116.4], zoom_start=10)

    filtered_df["latitude"] = filtered_df["station"].map(lambda x: station_coords.get(x, [None, None])[0])
    filtered_df["longitude"] = filtered_df["station"].map(lambda x: station_coords.get(x, [None, None])[1])

    avg_pm25 = filtered_df.groupby("station").agg({"PM2.5": "mean", "latitude": "first", "longitude": "first"}).reset_index()

    def get_color(pm25):
        if pm25 < 50:
            return "green"
        elif pm25 < 100:
            return "yellow"
        elif pm25 < 150:
            return "orange"
        elif pm25 < 200:
            return "red"
        else:
            return "darkred"

    for _, row in avg_pm25.iterrows():
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=row["PM2.5"] / 10, 
            color=get_color(row["PM2.5"]),
            fill=True,
            fill_color=get_color(row["PM2.5"]),
            fill_opacity=0.7,
            popup=f"{row['station']}: {row['PM2.5']:.2f} µg/m³"
        ).add_to(peta)

    folium_static(peta)

else:
    st.warning("Tidak ada data yang tersedia untuk filter yang dipilih.")
