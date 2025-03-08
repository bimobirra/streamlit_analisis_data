import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
sns.set(style='dark')

def create_daily_sale_df(df):
    daily_sales_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        'order_id': 'nunique'
    })
    daily_sales_df.reset_index(inplace = True)
    daily_sales_df.rename(columns={
        'order_purchase_timestamp': 'month',
        'order_id': 'Sales_count',
    }, inplace=True)
    
    return daily_sales_df

def create_bycategory_df(df):
    bycategory_df = df.groupby('category_name').agg({
        'order_id': 'count'
    })
    
    return bycategory_df

def create_bycity_df(df):
    bycity_df = df.groupby('customer_city').agg({
        'custom_id': 'count'
    }).sort_values(by='custom_id', ascending=False)
    
    return bycity_df

def create_rfm_df(df):
    rfm_df = df.groupby('custom_id', as_index=False).agg({
        'order_purchase_timestamp' : 'max',
        'order_id' : 'count',
        'payment_value' : 'sum'
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    rfm_df['max_order_timestamp'] = pd.to_datetime(rfm_df['max_order_timestamp'])

    recent_date = pd.to_datetime(all_df['order_purchase_timestamp'].max())
    rfm_df['recency'] = rfm_df['max_order_timestamp'].apply(lambda x: (recent_date - x).days)
    rfm_df.drop('max_order_timestamp', axis=1, inplace=True)
    
    return rfm_df

all_df = pd.read_csv('/mount/src/streamlit_analisis_data/dashboard/all_df.csv')

datetime_columns = ['order_purchase_timestamp']
all_df.sort_values(by='order_purchase_timestamp', inplace=True)
all_df.reset_index()

all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'])

min_date = all_df['order_purchase_timestamp'].min()
max_date = all_df['order_purchase_timestamp'].max()

with st.sidebar:
    start_date, end_date = st.date_input(
        label='Time Range', min_value=min_date, max_value=max_date,value=[min_date, max_date]
    )
    
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]

daily_sale_df = create_daily_sale_df(main_df)
bycategory_df = create_bycategory_df(main_df)
bycity_df = create_bycity_df(main_df)
rfm_df = create_rfm_df(main_df)

st.header('E-Commerce Dashboard')

st.subheader('Daily sale')

total_sale = daily_sale_df.Sales_count.sum()
st.metric('Total sale', value=total_sale)

fig, ax = plt.subplots(figsize=(20,10))
ax.plot(daily_sale_df['month'], daily_sale_df['Sales_count'], marker='o', linewidth=4, color="#72BCD4")
ax.tick_params(axis='x', labelsize=20, labelrotation=30)
ax.tick_params(axis='y', labelsize=25)

st.pyplot(fig)

st.subheader('Best and Worst Performing Product Category')

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35,15))
sns.barplot(x='order_id', y='category_name', data= bycategory_df.sort_values(by='order_id', ascending=False).head(5), ax=ax[0], palette=colors)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Performing Product Category", loc="center", fontsize=50)
ax[0].tick_params(axis ='y', labelsize=35)
ax[0].tick_params(axis ='x', labelsize=35)

sns.barplot(x='order_id', y='category_name', data= bycategory_df.sort_values(by='order_id', ascending=True).head(5), ax=ax[1], palette=colors)
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product Category", loc="center", fontsize=50)
ax[1].tick_params(axis ='y', labelsize=35)
ax[1].tick_params(axis ='x', labelsize=35)

st.pyplot(fig)

st.subheader('Buyer Demographics')

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

fig, ax = plt.subplots(figsize=(10,5))
sns.barplot(x='custom_id', y='customer_city', data=bycity_df.sort_values(by='custom_id', ascending=False).head(10), palette=colors)
ax.set_title('Top 10 Buyer City', loc='center', fontsize=20)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=15)

st.pyplot(fig)

st.subheader('Best Customer Based on RFM Parameters')

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
    
with col3:
    avg_frequency = round(rfm_df.monetary.mean(), 2) 
    st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15), dpi=150)

colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis ='x', labelsize=30)
ax[0].tick_params(axis ='y', labelsize=30)

sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='x', labelsize=30)
ax[1].tick_params(axis='y', labelsize=30)

sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='x', labelsize=30)
ax[2].tick_params(axis='y', labelsize=30)

st.pyplot(fig)