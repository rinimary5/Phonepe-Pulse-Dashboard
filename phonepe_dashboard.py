import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu
import json
import pandas as pd
from pymongo import MongoClient
from camelcase import CamelCase
import plotly.express as px
import plotly.io as pio
from pandas import json_normalize
import numpy as np
c = CamelCase()
phn=Image.open("phn.png")
st.set_page_config(page_title="PhonePe Pulse", page_icon=phn, layout="wide", )
#Dashboard Design
SELECT = option_menu(
    menu_title = None,
    options = ["About","Search","Home","Map"],
    icons =["bar-chart","search","house","map"],
    default_index=2,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "white","size":"cover"},
        "icon": {"color": "black", "font-size": "20px"},
        "nav-link": {"font-size": "20px", "text-align": "center", "margin": "-2px", "--hover-color": "#6F36AD"},
        "nav-link-selected": {"background-color": "#6F36AD"},}
    )
#For Home Tab
if SELECT == "Home":
    col1,col2, = st.columns(2)
    col1.image(Image.open("pulse.png"),width = 500)
    with col1:
        st.subheader("PhonePe  is an Indian digital payments and financial technology company headquartered in Bengaluru, Karnataka, India. PhonePe was founded in December 2015, by Sameer Nigam, Rahul Chari and Burzin Engineer. The PhonePe app, based on the Unified Payments Interface (UPI), went live in August 2016. It is owned by Flipkart, a subsidiary of Walmart.")

    with col2:
        st.video("https://website.phonepe.com/assets/page/home-fast-secure-v3.mp4")
#For About Tab
if SELECT == "About":
    col1,col2 = st.columns(2)
    with col1:
        st.video("https://youtu.be/c_1H6vivsiA")
    with col2:
        st.image(Image.open("pulse2.jpg"),width = 500)
        st.write("---")
        st.subheader("The Indian digital payments story has truly captured the world's imagination."
                 " From the largest towns to the remotest villages, there is a payments revolution being driven by the penetration of mobile phones, mobile internet and state-of-the-art payments infrastructure built as Public Goods championed by the central bank and the government."
                 " Founded in December 2015, PhonePe has been a strong beneficiary of the API driven digitisation of payments in India. When we started, we were constantly looking for granular and definitive data sources on digital payments in India. "
                 "PhonePe Pulse is our way of giving back to the digital payments ecosystem.")
    st.write("---")
    col1,col2 = st.columns(2)
    with col1:
        st.title("THE BEAT OF PHONEPE")
        st.write("---")
        st.subheader("Phonepe became a leading digital payments company")
        st.image(Image.open("beat.jpg"),width = 400,use_column_width='auto')
        with open("Pulse_Report_2021_L_Cr.pdf","rb") as f:
            data = f.read()
        st.download_button("DOWNLOAD REPORT",data,file_name="annual report.pdf")
    with col2:
        st.image(Image.open("report.png"),width = 800)
#For Map Tab
if SELECT == "Map":
    st.title("MAP")
    st.write("----")
    # For loading geojson file
    india_states = json.load(open('C:/Users/Faith/PycharmProjects/phonepe/states_india.geojson', 'r'))

# For creating a dictionary of state & id pairs
    def state_id_dict(india_state):
        state_id_map = {}
        for feature in india_state['features']:
            feature['id'] = feature['properties']['state_code']
            state_id_map[feature['properties']['st_nm']] = feature['id']
        # Manipulating the dictionary state names according to state name in df
        state_id_map['Arunachal Pradesh'] = state_id_map['Arunanchal Pradesh']
        del state_id_map['Arunanchal Pradesh']
        state_id_map['Dadra & Nagar Haveli & Daman & Diu'] = state_id_map['Daman & Diu']
        del state_id_map['Daman & Diu']
        del state_id_map['Dadara & Nagar Havelli']
        state_id_map['Delhi'] = state_id_map['NCT of Delhi']
        del state_id_map['NCT of Delhi']
        return state_id_map


    options = ["--select--", "Transaction Map",
               "User Map"]
    select = st.selectbox("Select the option", options)

    #For Displaying Map with respet to transaction details
    if select == "Transaction Map":
        # For loading datas from Database
        def load_data():
            client = MongoClient('mongodb://localhost:27017')
            mydb = client.db_phonepe_pulse
            mycol = mydb.map_transaction
            cursor = mycol.find()
            list_cur = list(cursor)
            df = pd.DataFrame(list_cur)
            df['State'] = df['State'].apply(lambda x: x.replace('-', ' '))
            df['State'] = df['State'].apply(lambda x: x.replace('islands', 'island'))
            df['State'] = df['State'].apply(lambda x: c.hump(x))

        # To make more clear representation in plotly map
            df["Transaction_CountScale"] = np.log10(df["Transaction_Count"])
            return df

        state_id_map = {}
        df_map_trans=load_data()
        state_id_map = state_id_dict(india_states)
        df_map_trans.drop(df_map_trans.loc[df_map_trans['State']=='Ladakh'].index,axis=0,inplace=True)

        #Adding a column id to dataframe inorder to connect with map dictionary for each state(For location)
        df_map_trans['id'] = df_map_trans['State'].apply(lambda x:state_id_map[x])

        #Plotting map using plotly for Aggregated Transaction Data
        fig = px.choropleth(df_map_trans,
                            locations='id',
                            geojson=india_states,
                            color='Transaction_CountScale',
                            hover_name='State',
                            hover_data=['Transaction_Amount', 'Transaction_Count'],
                            scope='asia',
                            color_continuous_scale='Viridis',
                            title='Total Transaction Count and Transaction Amount across the states',height=1000)

        fig.update_geos(fitbounds='locations', visible=False)
        st.plotly_chart(fig,use_container_width=True)
    # For Displaying Map with respect to registered users details
    if select == "User Map":

        # For loading datas from Database
        def load_data():
            client = MongoClient('mongodb://localhost:27017')
            mydb = client.db_phonepe_pulse
            mycol = mydb.map_user
            cursor = mycol.find()
            list_cur = list(cursor)
            df = pd.DataFrame(list_cur)
            df['State'] = df['State'].apply(lambda x: x.replace('-', ' '))
            df['State'] = df['State'].apply(lambda x: x.replace('islands', 'island'))
            df['State'] = df['State'].apply(lambda x: c.hump(x))

        # To make more clear representation in plotly map
            df["RegisteredUsers_Scale"] = np.log10(df["RegisteredUsers"])
            return df

        state_id_map = {}
        df_map_user = load_data()
        state_id_map = state_id_dict(india_states)
        df_map_user.drop(df_map_user.loc[df_map_user['State'] == 'Ladakh'].index, axis=0, inplace=True)

        #Adding a column id to connect with map dictionary for each state
        df_map_user['id'] = df_map_user['State'].apply(lambda x: state_id_map[x])

        # Plotting map using plotly for Aggregated Registered User Data
        fig = px.choropleth(df_map_user,
                            locations='id',
                            geojson=india_states,
                            color='RegisteredUsers_Scale',
                            hover_name='State',
                            hover_data=['RegisteredUsers'],
                            scope='asia',
                            color_continuous_scale='Viridis',
                            title='Total no of Registered Users across the states',height=1000)

        fig.update_geos(fitbounds='locations', visible=False)
        st.plotly_chart(fig,use_container_width=True)

#For Search Tab
if SELECT =="Search":
    Topic = ["","Transaction-Type","Transaction-District","Brand","Top-Transactions","Registered-users-District"]
    choice_topic = st.selectbox("Search by",Topic)

    #To get aggregated transaction dataframe
    def load_data_agg_trans():
        client = MongoClient('mongodb://localhost:27017')
        mydb = client.db_phonepe_pulse
        mycol = mydb.aggregated_transaction
        cursor = mycol.find()
        list_cur = list(cursor)
        df = pd.DataFrame(list_cur)
        return df


    # To get aggregated user dataframe
    def load_data_agg_user():
        client = MongoClient('mongodb://localhost:27017')
        mydb = client.db_phonepe_pulse
        mycol = mydb.aggregated_user
        cursor = mycol.find()
        list_cur = list(cursor)
        df = pd.DataFrame(list_cur)
        return df


    # To get map_transaction dataframe
    def load_data_map_trans():
        client = MongoClient('mongodb://localhost:27017')
        mydb = client.db_phonepe_pulse
        mycol = mydb.map_transaction
        cursor = mycol.find()
        list_cur = list(cursor)
        df = pd.DataFrame(list_cur)
        return df


    # To get map_user dataframe
    def load_data_map_user():
        client = MongoClient('mongodb://localhost:27017')
        mydb = client.db_phonepe_pulse
        mycol = mydb.map_user
        cursor = mycol.find()
        list_cur = list(cursor)
        df = pd.DataFrame(list_cur)
        return df
    #To get top transaction dataframe
    def load_data_top_trans():
        client = MongoClient('mongodb://localhost:27017')
        mydb = client.db_phonepe_pulse
        mycol = mydb.top_transaction_district
        cursor = mycol.find()
        list_cur = list(cursor)
        df = pd.DataFrame(list_cur)
        return df


    # To get top user dataframe
    def load_data_top_user():
        client = MongoClient('mongodb://localhost:27017')
        mydb = client.db_phonepe_pulse
        mycol = mydb.top_user_district
        cursor = mycol.find()
        list_cur = list(cursor)
        df = pd.DataFrame(list_cur)
        return df

    df_agg_trans = load_data_agg_trans()
    df_agg_user = load_data_agg_user()
    df_map_trans = load_data_map_trans()
    df_map_user = load_data_map_user()
    df_top_trans = load_data_top_trans()
    df_top_user = load_data_top_user()

#For Searching according to Transaction type
    if choice_topic == "Transaction-Type":
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("-- 5 TYPES OF TRANSACTION --")
            transaction_type = st.selectbox("search by", ["Choose an option", "Peer-to-peer payments",
                                                          "Merchant payments", "Financial Services",
                                                          "Recharge & bill payments", "Others"], 0)
        with col2:
            st.subheader("-- YEARS --")
            choice_year = st.selectbox("Year", ["", "2018", "2019", "2020", "2021", "2022"], 0)
        with col3:
            st.subheader("-- STATES --")
            menu_state = ["", 'uttar-pradesh', 'jharkhand', 'puducherry', 'rajasthan', 'odisha', 'nagaland',
                          'chandigarh', 'dadra-&-nagar-haveli-&-daman-&-diu', 'assam', 'haryana', 'jammu-&-kashmir',
                          'tamil-nadu', 'himachal-pradesh', 'ladakh', 'bihar', 'maharashtra', 'uttarakhand',
                          'karnataka', 'lakshadweep', 'andhra-pradesh', 'sikkim', 'madhya-pradesh', 'mizoram',
                          'kerala', 'manipur', 'arunachal-pradesh', 'andaman-&-nicobar-islands', 'delhi', 'tripura',
                          'chhattisgarh', 'meghalaya', 'goa', 'west-bengal', 'telangana', 'gujarat', 'punjab']
            choice_state = st.selectbox("State", menu_state, 0)
        if transaction_type:
            col1, col2, col3, = st.columns(3)
            with col1:
                st.subheader(transaction_type)
                df=df_agg_trans.loc[df_agg_trans['Transaction_type']==transaction_type]
                st.write(df)
        if transaction_type and choice_year:
            with col2:
                st.subheader(f' in {choice_year}')
                df = df_agg_trans.loc[(df_agg_trans['Transaction_type'] == transaction_type) & (df_agg_trans['Year'] == choice_year)]
                st.write(df)
        if transaction_type and choice_state and choice_year:
            with col3:
                st.subheader(f' in {choice_state}')
                df = df_agg_trans.loc[(df_agg_trans['Transaction_type'] == transaction_type) & (df_agg_trans['Year'] == choice_year)& (df_agg_trans['State']==choice_state)]
                st.write(df)
# For Searching Transaction details with respect to District
    if choice_topic == "Transaction-District":
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("-- STATES --")
            menu_state = ["", 'uttar-pradesh', 'jharkhand', 'puducherry', 'rajasthan', 'odisha', 'nagaland',
                          'chandigarh', 'dadra-&-nagar-haveli-&-daman-&-diu', 'assam', 'haryana', 'jammu-&-kashmir',
                          'tamil-nadu', 'himachal-pradesh', 'ladakh', 'bihar', 'maharashtra', 'uttarakhand',
                          'karnataka', 'lakshadweep', 'andhra-pradesh', 'sikkim', 'madhya-pradesh', 'mizoram',
                          'kerala', 'manipur', 'arunachal-pradesh', 'andaman-&-nicobar-islands', 'delhi', 'tripura',
                          'chhattisgarh', 'meghalaya', 'goa', 'west-bengal', 'telangana', 'gujarat', 'punjab']
            choice_state = st.selectbox("State", menu_state, 0)
        with col2:
            st.subheader("-- 5 YEARS --")
            choice_year = st.selectbox("Year", ["", "2018", "2019", "2020", "2021", "2022"], 0)
        with col3:
            st.subheader("-- SELECT DISTRICTS --")
            df = df_map_trans.loc[df_map_trans["State"]== choice_state]
            district = st.selectbox("search by", df["District"].unique().tolist())
        if choice_state:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.subheader(f'{choice_state}')
                df = df_map_trans.loc[df_map_trans["State"] == choice_state]
                st.write(df)
        if choice_year and choice_state:
            with col2:
                st.subheader(f'in {choice_year} ')
                df = df_map_trans.loc[(df_map_trans["State"] == choice_state) & (df_map_trans["Year"] == choice_year)]
                st.write(df)
        if district and choice_state and choice_year:
            with col3:
                st.subheader(f'in {district} ')
                df = df_map_trans.loc[(df_map_trans["State"] == choice_state) & (df_map_trans["Year"] == choice_year) & (df_map_trans["District"] == district)]
                st.write(df)
#For Searching with respect to Mobilephone Brands
    if choice_topic == "Brand":
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("-- TYPES OF BRANDS --")
            mobiles = ["", 'Xiaomi', 'Vivo', 'Samsung', 'Oppo', 'Realme', 'Apple', 'Huawei', 'Motorola', 'Tecno',
                       'Infinix','Lenovo', 'Lava', 'OnePlus', 'Micromax', 'Asus', 'Gionee', 'HMD Global', 'COOLPAD',
                       'Lyf','Others']
            brand_type = st.selectbox("search by", mobiles, 0)
        with col2:
            st.subheader("-- YEARS --")
            choice_year = st.selectbox("Year", ["", "2018", "2019", "2020", "2021", "2022"], 0)
        with col3:
            st.subheader("--STATES --")
            menu_state = ["", 'uttar-pradesh', 'jharkhand', 'puducherry', 'rajasthan', 'odisha', 'nagaland',
                          'chandigarh', 'dadra-&-nagar-haveli-&-daman-&-diu', 'assam', 'haryana', 'jammu-&-kashmir',
                          'tamil-nadu', 'himachal-pradesh', 'ladakh', 'bihar', 'maharashtra', 'uttarakhand',
                          'karnataka', 'lakshadweep', 'andhra-pradesh', 'sikkim', 'madhya-pradesh', 'mizoram',
                          'kerala', 'manipur', 'arunachal-pradesh', 'andaman-&-nicobar-islands', 'delhi', 'tripura',
                          'chhattisgarh', 'meghalaya', 'goa', 'west-bengal', 'telangana', 'gujarat', 'punjab']
            choice_state = st.selectbox("State", menu_state, 0)
        if brand_type:
            col1, col2, col3, = st.columns(3)
            with col1:
                st.subheader(f'{brand_type}')
                df=df_agg_user.loc[df_agg_user['Brands']==brand_type]
                st.write(df)

        if brand_type and choice_year:
            with col2:
                st.subheader(f' in {choice_year}')
                df = df_agg_user.loc[(df_agg_user['Brands'] == brand_type) & ( df_agg_user['Year']==choice_year)]
                st.write(df)

        if brand_type and choice_state and choice_year:
            with col3:
                st.subheader(f' in {choice_state}')
                df = df_agg_user.loc[(df_agg_user['Brands'] == brand_type) & (df_agg_user['Year']==choice_year) & (df_agg_user['State']==choice_state)]
                st.write(df)
#For Searching top transaction of states:
    if choice_topic == "Top-Transactions":
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("-- 36 STATES --")
            menu_state = ["", 'uttar-pradesh', 'jharkhand', 'puducherry', 'rajasthan', 'odisha', 'nagaland',
                          'chandigarh', 'dadra-&-nagar-haveli-&-daman-&-diu', 'assam', 'haryana', 'jammu-&-kashmir',
                          'tamil-nadu', 'himachal-pradesh', 'ladakh', 'bihar', 'maharashtra', 'uttarakhand',
                          'karnataka', 'lakshadweep', 'andhra-pradesh', 'sikkim', 'madhya-pradesh', 'mizoram',
                          'kerala', 'manipur', 'arunachal-pradesh', 'andaman-&-nicobar-islands', 'delhi', 'tripura',
                          'chhattisgarh', 'meghalaya', 'goa', 'west-bengal', 'telangana', 'gujarat', 'punjab']
            choice_state = st.selectbox("State", menu_state, 0)
        with col2:
            st.subheader("-- 5 YEARS --")
            choice_year = st.selectbox("Year", ["", "2018", "2019", "2020", "2021", "2022"], 0)
        with col3:
            st.subheader("--4 Quaters --")
            menu_quater = ["", 1, 2, 3, 4]
            choice_quater = st.selectbox("Quater", menu_quater, 0)

        if choice_state:
            with col1:
                st.subheader(f'{choice_state}')
                df = df_top_trans.loc[df_top_trans['State'] == choice_state]
                st.write(df)
        if choice_state and choice_year:
            with col2:
                st.subheader(f'{choice_year}')
                df = df_top_trans.loc[(df_top_trans['State'] == choice_state) & (df_top_trans['Year'] == choice_year)]
                st.write(df)
        if choice_state and choice_quater and choice_year:
            with col3:
                st.subheader(f'{choice_quater}')
                df = df_top_trans.loc[(df_top_trans['Quater'] == choice_quater) & (df_top_trans['Year'] == choice_year) & (df_top_trans['State'] == choice_state)]
                st.write(df)
#For Searching Registered Users with respect to District
    if choice_topic == "Registered-users-District":
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("-- STATES --")
            menu_state = ["", 'uttar-pradesh', 'jharkhand', 'puducherry', 'rajasthan', 'odisha', 'nagaland',
                          'chandigarh', 'dadra-&-nagar-haveli-&-daman-&-diu', 'assam', 'haryana', 'jammu-&-kashmir',
                          'tamil-nadu', 'himachal-pradesh', 'ladakh', 'bihar', 'maharashtra', 'uttarakhand',
                          'karnataka', 'lakshadweep', 'andhra-pradesh', 'sikkim', 'madhya-pradesh', 'mizoram',
                          'kerala', 'manipur', 'arunachal-pradesh', 'andaman-&-nicobar-islands', 'delhi', 'tripura',
                          'chhattisgarh', 'meghalaya', 'goa', 'west-bengal', 'telangana', 'gujarat', 'punjab']
            choice_state = st.selectbox("State", menu_state, 0)
        with col2:
            st.subheader("-- YEARS --")
            choice_year = st.selectbox("Year", ["", "2018", "2019", "2020", "2021", "2022"], 0)
        with col3:
            st.subheader("-- SELECT DISTRICTS --")
            df = df_map_user.loc[df_map_user['State']== choice_state]
            district = st.selectbox("search by", df["District"].unique().tolist())

        if choice_state:
            with col1:
                st.subheader(f'{choice_state}')
                df = df_map_user.loc[df_map_user['State'] == choice_state]
                st.write(df)
        if choice_state and choice_year:
            with col2:
                st.subheader(f'{choice_year}')
                df = df_map_user.loc[(df_map_user['State'] == choice_state) & (df_map_user['Year'] == choice_year)]
                st.write(df)
        if choice_state and choice_year and district:
            with col3:
                st.subheader(f'{district}')
                df = df_map_user.loc[(df_map_user['State'] == choice_state) & (df_map_user['Year'] == choice_year) & (df_map_user['District'] == district)]
                st.write(df)