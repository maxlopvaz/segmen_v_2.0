import instaloader
import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter

# Configuración de la aplicación en Streamlit
st.title("Instagram Account Statistics")

# Entrada del nombre de usuario
username = st.text_input("Enter the Instagram username:")

# Botón para extraer datos
if st.button("Get Statistics"):
    if username:
        # Cargar el perfil de Instagram
        L = instaloader.Instaloader()
        try:
            profile = instaloader.Profile.from_username(L.context, username)

            # Mostrar estadísticas básicas
            st.write(f"**Username:** {profile.username}")
            st.write(f"**Full Name:** {profile.full_name}")
            st.write(f"**Biography:** {profile.biography}")
            st.write(f"**Number of Posts:** {profile.mediacount}")
            st.write(f"**Followers:** {profile.followers}")
            st.write(f"**Following:** {profile.followees}")
            st.write(f"**External URL:** {profile.external_url}")

            # Extraer estadísticas adicionales
            st.write("### Additional Statistics")

            hashtags = []
            post_types = {'Image': 0, 'Video': 0, 'IGTV': 0}
            dates = []
            locations = []

            for post in profile.get_posts():
                hashtags.extend(post.caption_hashtags)
                dates.append(post.date)

                if post.typename == 'GraphImage':
                    post_types['Image'] += 1
                elif post.typename == 'GraphVideo':
                    post_types['Video'] += 1
                elif post.typename == 'GraphSidecar':
                    post_types['IGTV'] += 1

                # Extraer la ubicación si está disponible
                if post.location:
                    locations.append({
                        'name': post.location.name,
                        'lat': post.location.lat,
                        'lng': post.location.lng
                    })

            # Gráfico de barras de los hashtags más usados
            top_hashtags = Counter(hashtags).most_common(5)
            top_hashtags_df = pd.DataFrame(top_hashtags, columns=['Hashtag', 'Count'])
            st.write("**Top Hashtags Used**")
            fig = px.bar(top_hashtags_df, x='Hashtag', y='Count', title='Top 5 Hashtags')
            st.plotly_chart(fig)

            # Listar y graficar los tipos de publicaciones
            st.write("**Type of Posts**")
            post_types_df = pd.DataFrame(list(post_types.items()), columns=['Type', 'Count'])
            fig = px.pie(post_types_df, values='Count', names='Type', title='Distribution of Post Types')
            st.plotly_chart(fig)


            # Análisis de cuentas seguidas y tópicos
            st.write("### Followed Accounts and Topics")
            followed_accounts = []
            topics = []
            for followee in profile.get_followees():
                followed_accounts.append(followee.username)
                if followee.biography:
                    topics.extend(followee.biography.split())

            # Análisis de tópicos en las biografías de las cuentas seguidas
            if topics:
                top_topics = Counter(topics).most_common(10)
                top_topics_df = pd.DataFrame(top_topics, columns=['Topic', 'Count'])
                st.write("**Top Topics in Followed Accounts**")
                fig = px.bar(top_topics_df, x='Topic', y='Count', title='Top Topics in Followed Accounts')
                st.plotly_chart(fig)

            # Listar las cuentas más influyentes seguidas (mayor número de seguidores)
            if followed_accounts:
                followed_accounts_info = [(followee.username, followee.followers) for followee in profile.get_followees()]
                top_followed_accounts = sorted(followed_accounts_info, key=lambda x: x[1], reverse=True)[:10]
                top_followed_df = pd.DataFrame(top_followed_accounts, columns=['Username', 'Followers'])
                st.write("**Top Followed Accounts by Popularity**")
                st.dataframe(top_followed_df)

            # Crear mapa de calor de ubicaciones
            if locations:
                st.write("**Location Heatmap**")
                locations_df = pd.DataFrame(locations)
                fig = px.density_mapbox(locations_df, lat='lat', lon='lng', z=None, radius=10,
                                        mapbox_style="stamen-terrain", zoom=3,
                                        title="Location Heatmap of Posts")
                st.plotly_chart(fig)
            else:
                st.write("No locations available for this user.")

        except instaloader.exceptions.ProfileNotExistsException:
            st.error("The profile does not exist.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a username.")
