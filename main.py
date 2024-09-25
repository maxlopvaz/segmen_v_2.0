import requests
import streamlit as st
import pandas as pd
import plotly.express as px

# App credentials
app_id = "500840846254356"
app_secret = "0aaffe2acd5e594f3452a8e8fef6706b"
redirect_uri = "https://segmenv20-cdhhkxnhdciwcefkpjjn5u.streamlit.app/"
auth_url = f"https://api.instagram.com/oauth/authorize?client_id={app_id}&redirect_uri={redirect_uri}&scope=user_profile,user_media&response_type=code"

# Configuración de la aplicación en Streamlit
st.title("Instagram Account Statistics")

# Paso 1: Instrucciones para autenticación
st.write(f"1. Haz clic en [este enlace]({auth_url}) para autenticarte y obtener un código.")
st.write("2. Después de la autenticación, ingresa el código que recibiste.")

# Entrada del código de autenticación después de redirigir al usuario
auth_code = st.text_input("Introduce el código de autenticación:")

# Botón para intercambiar el código por un token de acceso
if st.button("Obtener Token de Acceso"):
    if auth_code:
        # Paso 2: Intercambiar el código por el token de acceso
        token_url = "https://api.instagram.com/oauth/access_token"
        payload = {
            'client_id': app_id,
            'client_secret': app_secret,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
            'code': auth_code
        }

        # Solicitar el token de acceso
        try:
            response = requests.post(token_url, data=payload)
            token_data = response.json()

            if 'access_token' in token_data:
                access_token = token_data['access_token']
                st.success("Token de acceso obtenido exitosamente.")
                st.write(f"Token de acceso: {access_token}")

                # Paso 3: Extraer datos del perfil usando el token de acceso
                profile_url = f"https://graph.instagram.com/me?fields=id,username,media_count,account_type&access_token={access_token}"
                profile_response = requests.get(profile_url)
                profile_data = profile_response.json()

                if profile_response.status_code == 200:
                    # Mostrar estadísticas básicas del perfil
                    st.write(f"**Username:** {profile_data['username']}")
                    st.write(f"**Media Count:** {profile_data['media_count']}")
                    st.write(f"**Account Type:** {profile_data['account_type']}")

                    # Obtener medios (publicaciones) del usuario
                    media_url = f"https://graph.instagram.com/me/media?fields=id,caption,media_type,media_url,thumbnail_url,timestamp&access_token={access_token}"
                    media_response = requests.get(media_url)
                    media_data = media_response.json()

                    if 'data' in media_data:
                        media_list = media_data['data']

                        # Verificar si hay publicaciones
                        if len(media_list) == 0:
                            st.warning("No se encontraron publicaciones.")
                        else:
                            # Analizar y mostrar estadísticas de los medios (publicaciones)
                            captions = []
                            media_types = {'IMAGE': 0, 'VIDEO': 0, 'CAROUSEL_ALBUM': 0}
                            timestamps = []

                            for media in media_list:
                                captions.extend(media.get('caption', '').split())
                                media_type = media.get('media_type', 'UNKNOWN')
                                if media_type in media_types:
                                    media_types[media_type] += 1
                                timestamps.append(media['timestamp'])

                            # Mostrar gráfico de tipos de publicaciones
                            post_types_df = pd.DataFrame(list(media_types.items()), columns=['Type', 'Count'])
                            st.write("**Distribución de Tipos de Publicaciones**")
                            fig = px.pie(post_types_df, values='Count', names='Type',
                                         title='Distribución de Tipos de Publicaciones')
                            st.plotly_chart(fig)

                            # Mostrar las palabras más comunes en las descripciones (captions)
                            if captions:
                                caption_counts = pd.DataFrame(captions, columns=["Word"])
                                top_words = caption_counts['Word'].value_counts().head(10).reset_index()
                                top_words.columns = ['Word', 'Count']

                                st.write("**Top 10 Palabras en las Descripciones**")
                                fig = px.bar(top_words, x='Word', y='Count', title='Top 10 Palabras en Descripciones')
                                st.plotly_chart(fig)

                            # Mostrar las fechas de las publicaciones
                            if timestamps:
                                timestamps_df = pd.DataFrame(timestamps, columns=["Timestamp"])
                                timestamps_df['Date'] = pd.to_datetime(timestamps_df['Timestamp']).dt.date
                                date_counts = timestamps_df['Date'].value_counts().reset_index()
                                date_counts.columns = ['Date', 'Count']

                                st.write("**Frecuencia de Publicaciones por Fecha**")
                                fig = px.line(date_counts, x='Date', y='Count',
                                              title='Frecuencia de Publicaciones por Fecha')
                                st.plotly_chart(fig)

                    else:
                        st.warning("No se pudieron obtener las publicaciones del perfil.")

                else:
                    st.error(f"Error al obtener el perfil: {profile_data.get('error', {}).get('message', 'Unknown Error')}")

            else:
                st.error(f"Error al obtener el token: {token_data.get('error_message', 'Unknown Error')}")

        except Exception as e:
            st.error(f"Error durante el intercambio del código por token: {e}")
    else:
        st.warning("Por favor, ingresa el código de autenticación.")
