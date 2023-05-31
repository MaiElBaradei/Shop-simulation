import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("Food Cart Simulation")

st.sidebar.header("Simulation Parameters")
t_arr_min = st.sidebar.number_input("Minimum inter-arrival time:", min_value=1, value=2, step=1)
t_arr_max = st.sidebar.number_input("Maximum inter-arrival time:", min_value=1, value=6, step=1)
t_ser_min = st.sidebar.number_input("Minimum service time:", min_value=1, value=3, step=1)
t_ser_max = st.sidebar.number_input("Maximum service time:", min_value=1, value=7, step=1)
customer_count = st.sidebar.number_input("Number of customers:", min_value=1, value=10, step=1)

def generate_random_digits(t_min,t_max,time_type):
    t = {'time':[],'probability':[]}
    for i in range(t_min, t_max+1):
        t['time'].append(i)
        t['probability'].append(float(st.number_input(f"Enter probability of {time_type} time {i}", value=0.1)))
    t_df = pd.DataFrame(t)
    fig,ax = plt.subplots()
    ax.pie(t_df['probability'], labels=t_df['time'], autopct='%1.1f%%', shadow=True, startangle=90)
    ax.axis('equal')
    st.pyplot(fig)

    
    max_prob = t_df['probability'].astype(str).str.len().max()
    k = max_prob-2
    t_df['cumulative'] = t_df['probability'].cumsum()
    t_df['random_min'] = (t_df['cumulative'] - t_df['probability'])*(10**k) +1
    t_df['random_max'] = t_df['cumulative']*(10**k)
    return t_df

col1, col2 = st.columns(2)
with col1: 
    st.subheader("Inter-arrival time probability distribution")
    arrival_df = generate_random_digits(t_arr_min, t_arr_max, "inter-arrival")
with col2: 
    st.subheader("Service time probability distribution")
    service_df = generate_random_digits(t_ser_min, t_ser_max, "service")

random_df = pd.DataFrame(columns=['customer_number','random_arrival_digit','random_service_digit'])

table_df = pd.DataFrame(columns=['customer_no','inter_arrival_time','arrival_time','service_time'
                                 ,'start_time','end_time','waiting_time','time_in_system','idle_time'])
table_df['customer_no'] = np.arange(1,customer_count+1)

t1_zero = True if st.checkbox("First customer arrival time is 0?") else False
if t1_zero:
    table_df.loc[0,"inter_arrival_time"] = 0
    table_df.loc[0,'start_time'] = 0
    random_df.loc[0,'random_arrival_digit']= None

st.header("Random digit assignment")
col1, col2 = st.columns(2)
for i in range(customer_count):
    with col1:
        st.subheader(f"Customer {i+1}")
        if t1_zero:
            if i!=0:
                random_df.loc[i,'random_arrival_digit'] = st.number_input(f"Enter random number for inter-arrival time of customer {i+1}"
                                                                          , value=1)
            else:
                "no random digit for first customer"
                ""
                ""
                ""
        else:
            random_df.loc[i,'random_arrival_digit']= st.number_input(f"Enter random number for inter-arrival time of customer {i+1}"
                                                                     , value=1)
    with col2:
        st.subheader(f"Customer {i+1}")
        random_df.loc[i,'random_service_digit'] = st.number_input(f"Enter random number for service time of customer {i+1}", value=1)
    random_df.loc[i,'customer_number']= i+1
st.table(random_df)

for j in range(customer_count):
    if t1_zero:
        if j!=customer_count-1:
            table_df.loc[j+1,'inter_arrival_time']=arrival_df.loc[(arrival_df['random_min'] <= random_df.loc[j+1,'random_arrival_digit']) 
                                                                  & (arrival_df['random_max'] >= random_df.loc[j+1,'random_arrival_digit'])
                                                                  ,'time'].to_numpy().item()
    else:
        table_df.loc[j,'inter_arrival_time']=arrival_df.loc[(arrival_df['random_min'] <= random_df.loc[j,'random_arrival_digit']) 
                                                            & (arrival_df['random_max'] >= random_df.loc[j,'random_arrival_digit'])
                                                            ,'time'].to_numpy().item()
    
    table_df.loc[j,'service_time'] = service_df.loc[(service_df['random_min'] <= random_df.loc[j,'random_service_digit']) 
                                                    & (service_df['random_max'] >= random_df.loc[j,'random_service_digit'])
                                                    ,'time'].to_numpy().item()
table_df['arrival_time']= table_df['inter_arrival_time'].cumsum()


for k in range(1,customer_count+1):
    if k==1:
        table_df.loc[k-1,'start_time'] = table_df.loc[k-1,'arrival_time']
        table_df.loc[k-1,'end_time'] = table_df.loc[k-1,'start_time'] + table_df.loc[k-1,'service_time']
        table_df.loc[k-1,'idle_time'] = table_df.loc[k-1,'arrival_time']
    if k != customer_count:
        table_df.loc[k,'start_time'] = max(table_df.loc[k,'arrival_time'],table_df.loc[k-1,'end_time'])
        if table_df.loc[k-1,"customer_no"]%5 ==0:
            table_df.loc[k,'start_time'] = max(table_df.loc[k,'arrival_time'],table_df.loc[k-1,'end_time']+10)
        table_df.loc[k,"idle_time"] = max(0,table_df.loc[k,"arrival_time"] - table_df.loc[k-1,"end_time"])
        table_df.loc[k,'end_time'] = table_df.loc[k,'start_time'] + table_df.loc[k,'service_time']
    table_df.loc[k-1,'waiting_time'] = table_df.loc[k-1,'start_time'] - table_df.loc[k-1,'arrival_time']
    table_df.loc[k-1,"time_in_system"] = table_df.loc[k-1,"service_time"] + table_df.loc[k-1,"waiting_time"]

st.header("Simulation Analysis Table")
st.table(table_df)

total_waiting_time = table_df['waiting_time'].sum()
total_service_time = table_df['service_time'].sum()
total_idle_time = table_df['idle_time'].sum()
total_time_in_system = table_df['time_in_system'].sum()
server_utilization = total_service_time/(total_service_time+total_idle_time)
avg_waiting_time = total_waiting_time/customer_count
avg_time_in_system = total_time_in_system/customer_count
probability_of_waiting = table_df[table_df['waiting_time']>0]['waiting_time'].count()/customer_count
avg_wait_for_those_who_wait = total_waiting_time/table_df[table_df['waiting_time']>0]['waiting_time'].count()
avg_service_time = total_service_time/customer_count


customers_in_system = []
customer_num = 0
for i in range(table_df.loc[customer_count-1,'end_time']+1):
    for j in range(customer_count):
        if i==table_df.loc[j,'arrival_time']:
            customer_num += 1
        elif i==table_df.loc[j,'end_time']:
            customer_num -= 1
    customers_in_system.append(customer_num)


st.header("Simulation Analysis Graphs")
st.subheader("Number of Customers in System each time instant")
fig ,ax = plt.subplots()
ax.plot([i for i in range(table_df.loc[customer_count-1,'end_time']+1)],customers_in_system
        ,label='Number of Customers in System each time instant',drawstyle="steps-post")
ax.set_xlabel('Time (mins)')
ax.set_ylabel('Number of Customers')
ax.set_title('Number of Customers in System each time instant')
ax.set_xticks([i for i in range(0,table_df.loc[customer_count-1,'end_time']+1,2)])
ax.legend()
st.pyplot(fig)

st.subheader("Arrival Time vs Start Time vs End Time")
fig, ax = plt.subplots()
ax.scatter(table_df['customer_no'],table_df['arrival_time'],label='Arrival Time')
ax.scatter(table_df['customer_no'],table_df['start_time'],label='Start Time')
ax.scatter(table_df['customer_no'],table_df['end_time'],label='End Time')
ax.set_xlabel('Customer Number')
ax.set_ylabel('Time (mins)')
ax.set_xticks(table_df['customer_no'])
ax.set_title('Arrival Time vs Start Time vs End Time')
ax.legend()
st.pyplot(fig)

st.subheader(f"Total service time: {total_service_time} mins")
st.subheader(f"Average service time: {avg_service_time} mins")
col1, col2 = st.columns(2)
with col1:
    fig, ax = plt.subplots()
    ax.bar(table_df['customer_no'],table_df['service_time'],label='Service Time')
    ax.set_xlabel('Customer Number')
    ax.set_ylabel('Time (mins)')
    ax.set_xticks(table_df['customer_no'])
    ax.set_title('Service Time')
    ax.legend()
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots()
    ax.bar(table_df['customer_no'],table_df['service_time'],label='Service Time',alpha=0.7, color='r')
    ax.bar(table_df['customer_no'],table_df['time_in_system'],label='Time in System',alpha=0.5)
    ax.set_xlabel('Customer Number')
    ax.set_ylabel('Time (mins)')
    ax.set_xticks(table_df['customer_no'])
    ax.set_title('Service Time')
    ax.legend()
    st.pyplot(fig)

st.subheader(f"Total waiting time: {total_waiting_time} mins")
st.subheader(f"Average waiting time: {avg_waiting_time} mins")
col1,col2 = st.columns(2)
with col1:
    fig, ax = plt.subplots()
    ax.bar(table_df['customer_no'],table_df['waiting_time'],label='Waiting Time')
    ax.set_xlabel('Customer Number')
    ax.set_ylabel('Time (mins)')
    ax.set_xticks(table_df['customer_no'])
    ax.set_title('Waiting Time')
    ax.legend()
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots()
    ax.bar(table_df['customer_no'],table_df['waiting_time'],label='Waiting Time',alpha=0.7, color='r')
    ax.bar(table_df['customer_no'],table_df['time_in_system'],label='Time in System',alpha=0.5)
    ax.set_xlabel('Customer Number')
    ax.set_ylabel('Time (mins)')
    ax.set_xticks(table_df['customer_no'])
    ax.set_title('Waiting Time vs Time in System')
    ax.legend()
    st.pyplot(fig)

col1, col2 = st.columns(2)
with col1:
    fig, ax = plt.subplots()
    ax.pie([probability_of_waiting,1-probability_of_waiting]
           ,labels=['Probability of Waiting','Probability of Not Waiting'],autopct='%1.1f%%',shadow=True)
    ax.set_title('Probability of Waiting')
    st.pyplot(fig)

st.subheader(f"Total time in system: {total_time_in_system} mins")
st.subheader(f"Average time in system: {avg_time_in_system} mins")

fig, ax = plt.subplots()
ax.bar(table_df['customer_no'],table_df['waiting_time'],label='Waiting Time',alpha=0.7, color='r')
ax.bar(table_df['customer_no'],table_df['service_time'],label='Service Time',alpha=0.7, color='g')
ax.bar(table_df['customer_no'],table_df['time_in_system'],label='Time in System',alpha=0.5)
ax.set_xlabel('Customer Number')
ax.set_ylabel('Time (mins)')
ax.set_xticks(table_df['customer_no'])
ax.set_title('Waiting Time vs Time in System')
ax.legend()
st.pyplot(fig)

st.subheader(f"Server utilization: {server_utilization*100}%")
fig, ax = plt.subplots()
ax.pie([server_utilization,1-server_utilization],labels=['Server Utilization','Idle Time'],autopct='%1.1f%%')
ax.set_title('Server Utilization')
st.pyplot(fig)

st.subheader(f"Total idle time: {total_idle_time} mins")
fig, ax = plt.subplots()
ax.scatter(table_df['customer_no'],table_df['idle_time'],label='Idle Time')
ax.set_xlabel('Customer Number')
ax.set_ylabel('Time (mins)')
ax.set_xticks(table_df['customer_no'])
ax.set_title('Idle Time')
ax.legend()
st.pyplot(fig)

