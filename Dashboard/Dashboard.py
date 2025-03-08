import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import folium
from streamlit_folium import folium_static

sns.set(style='dark')

# Load data
all_df = pd.read_csv("all_data.csv")

# Konversi datetime
all_df["datetime"] = pd.to_datetime(all_df[["year", "month", "day", "hour"]])

# Koordinat lokasi stasiun (ditambahkan untuk menghindari error KeyError: 'latitude')
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

if not filtered_df.empty:
    # Visualisasi Tren PM2.5
    st.subheader("Tren PM2.5 di Tiga Lokasi")
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=filtered_df, x="year", y="PM2.5", hue="station", marker="o")
    plt.xlabel("Tahun")
    plt.ylabel("Konsentrasi PM2.5 (µg/m³)")
    plt.title("Tren PM2.5 dari 2013-2017")
    st.pyplot(plt)

    # Korelasi antara PM2.5 dan Faktor Meteorologi
    st.subheader("Korelasi antara PM2.5 dan Faktor Meteorologi")
    plt.figure(figsize=(10, 6))
    correlation_matrix = filtered_df[["PM2.5", "TEMP", "PRES", "DEWP"]].corr()
    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f")
    st.pyplot(plt)

    # Box plot untuk PM2.5 terhadap Suhu, Tekanan Udara, dan Kelembapan
    st.subheader("Distribusi PM2.5 berdasarkan Suhu, Tekanan Udara, dan Kelembapan")

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Box plot PM2.5 vs Suhu (TEMP)
    sns.boxplot(data=filtered_df, x=pd.cut(filtered_df["TEMP"], bins=10), y="PM2.5", ax=axes[0])
    axes[0].set_xticklabels(axes[0].get_xticklabels(), rotation=45)
    axes[0].set_title("Distribusi PM2.5 berdasarkan Suhu")
    axes[0].set_xlabel("Suhu (°C)")
    axes[0].set_ylabel("PM2.5 (µg/m³)")

    # Box plot PM2.5 vs Tekanan Udara (PRES)
    sns.boxplot(data=filtered_df, x=pd.cut(filtered_df["PRES"], bins=10), y="PM2.5", ax=axes[1])
    axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=45)
    axes[1].set_title("Distribusi PM2.5 berdasarkan Tekanan Udara")
    axes[1].set_xlabel("Tekanan Udara (hPa)")
    axes[1].set_ylabel("PM2.5 (µg/m³)")

    # Box plot PM2.5 vs Kelembapan (DEWP)
    sns.boxplot(data=filtered_df, x=pd.cut(filtered_df["DEWP"], bins=10), y="PM2.5", ax=axes[2])
    axes[2].set_xticklabels(axes[2].get_xticklabels(), rotation=45)
    axes[2].set_title("Distribusi PM2.5 berdasarkan Kelembapan")
    axes[2].set_xlabel("Kelembapan (°C)")
    axes[2].set_ylabel("PM2.5 (µg/m³)")

    st.pyplot(fig)

    # Peta lokasi pengamatan (gunakan koordinat dari dictionary)
    st.subheader("Peta Stasiun Pengamatan")
    peta = folium.Map(location=[39.9, 116.4], zoom_start=10)

    filtered_df["latitude"] = filtered_df["station"].map(lambda x: station_coords.get(x, [None, None])[0])
    filtered_df["longitude"] = filtered_df["station"].map(lambda x: station_coords.get(x, [None, None])[1])

    grouped_df = filtered_df.groupby("station").mean(numeric_only=True).reset_index()

    for _, row in grouped_df.iterrows():
        if not pd.isna(row["latitude"]) and not pd.isna(row["longitude"]):
            folium.Marker(
                [row["latitude"], row["longitude"]], popup=row["station"]
            ).add_to(peta)

    folium_static(peta)

else:
    st.warning("Tidak ada data yang tersedia untuk filter yang dipilih.")
