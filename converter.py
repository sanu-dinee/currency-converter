from dotenv import load_dotenv #load environment variables
import streamlit as st
import os
import requests #make HTTP requests to external APIs
import json # JSON data
from datetime import datetime

#----------------------------Load API key-------------------------
def load_api_key():
   load_dotenv()
   return os.getenv("EXCHANGE_RATE_API_KEY")

#---------------------------------Fetch  Rates---------------------
def fetch_exchange_rates(base_currency,api_key):

         url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"
         try:
          response = requests.get(url)
          data=response.json()
          if data.get("result")=="success":
               with open("backup_rates.json", "w") as backup:
                     json.dump(data["conversion_rates"],backup)
               return data.get("conversion_rates",{})
          else:
              return load_backupRates()
         except Exception:
          return load_backupRates()

def load_backupRates():
     if os.path.exists("backup_rates.json"):
          with open("backup_rates.json","r") as backup:
             return json.load(backup)
     else:
          st.error("No offline data available")
          return

#------------------------------App layout------------------------------
def currency_selector(currencyCodes):
   
#custom css
     
     st.markdown(

    """
   <iframe class='homeImage' src="https://lottie.host/embed/3ff898ee-a6db-4b99-9f5d-1c1731a0777f/RXX4NUUABZ.lottie"></iframe>
    <link href="https://fonts.googleapis.com/css2?family=Poppins&display=swap" rel="stylesheet">
    <style>
    body{
      background-color:black !important; color: white;
      }
    .stApp {
      background-color:#090040
      }
    .css-ffhzg2 {
        background-color: green !important; 
      }
    .stTitle > div{
        color: green !important;
        font-family: 'Poppins', sans-serif;
        text-align: center !important;
      }
    .stSelectbox > div, .stNumberInput > div { 
      color: black !important;
      } 
       
    .homeImage{
        border:none;
        height:25rem;
        width:22rem;
        margin-bottom:-2.5rem;
        margin-left:-2.5rem;
        margin-top:-3rem;
      }
    </style>
    """,unsafe_allow_html=True) #Streamlit to render raw HTML

     st.title("Currency Converter")

#Currency Selectors

     col1, col2 ,col3 = st.columns([3,1,3])

#first selectBox for the base currency
     with col1:
        baseCurrency =st.selectbox('From ',currencyCodes)
     with col2:
        st.markdown("""
    <iframe class='image' src="https://lottie.host/embed/e5f259d9-3cbd-486e-9f2f-0e4a23cb9218/Zhfo49xl5V.lottie" width="100%" height="150"  frameborder="0" allowfullscreen></iframe>
                <style>
                .image{
                   margin-top:-1.5rem;
                   
                  }
                </style>
                """, unsafe_allow_html=True)

#second selectBox for the base currency
     with col3:
      targetCurrency=st.selectbox('To ',currencyCodes)
      return baseCurrency,targetCurrency
     
         
def display_exchange_rates(base,target,rates):
    
#Exchange rates both ways

    rateForward=rates.get(target)
    rateBackward=1/rateForward if rateForward else None

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"1 {base} ")
        st.success(f"{rateForward:.3f}" if rateForward else "N/A")
    with col2:
        st.write(f"1 {target} ")
        st.success(f"{rateBackward:.3f}" if rateBackward else "N/A")

    return rateForward
         
#User Amount conversion and result
def convertAmount(baseCurrency, targetCurrency, rateForward):
    row3_col1, row3_col2 = st.columns(2)

    with row3_col1:
        st.markdown("""
        <style>
                  
         .custom-label {
            font-size: 16px;
            margin-top: 5px;
            margin-bottom:-10px;
        }       
         .custom-label2{
                   margin-top:18px ;
                   margin-bottom:30px;
                    
                    }                
        
        </style>
        """, unsafe_allow_html=True)
        st.markdown(f"<div class='custom-label'>Enter amount in {baseCurrency}</div>", unsafe_allow_html=True)
        
        userAmount = st.number_input("", key="amount_input", min_value=0.0, step=0.01) 
         #key=A unique key is required for Streamlit widgets when there are multiple instances or when the widget's state needs to be managed across reruns 

    with row3_col2:
        st.markdown(f"<div class='custom-label2'>Enter amount in {baseCurrency}</div>", unsafe_allow_html=True)
        if userAmount > 0 and rateForward:
            convertedAmount = userAmount * rateForward
            st.success(f"{convertedAmount:.3f} {targetCurrency}")
            save_conversion(baseCurrency, targetCurrency, userAmount, convertedAmount)
        else:
          st.success("             ")
           


st.markdown('<style>body{text-align:center;} #MainMenu,footer{visibility:hidden}.css-ffhzg2{background-color:#0E185F;}</style>',unsafe_allow_html=True)    

def save_conversion(base, target, amount, result):
    if amount<=0 and result<=0:
          return 
     
     #Creates a dictionary to store the details of the conversion
    record = {
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "from": base,
        "to": target,
        "amount": amount,
        "converted": round(result, 3),
        
    }
    history = load_history()
    history.append(record)

    #write records in json file
    with open("conversion_history.json", "w") as file:
        json.dump(history, file, indent=4 )#pretty-printing the JSON

def load_history():
     #read records from json file
    if os.path.exists("conversion_history.json"):
        with open("conversion_history.json", "r") as file:
            return json.load(file)
    return []        

def removeButton(index):
     history=load_history()
     if 0<=index <len(history):
          history.pop(index)
          #overwrites with the modified history list 
          with open("conversion_history.json","w") as file:
               json.dump(history,file,indent=4)
               
               
def clear_history():
    if os.path.exists("conversion_history.json"):
        os.remove("conversion_history.json")
        st.success("Conversion history cleared.")
    else:
        st.info("No history to clear.")
    
          
def show_HistoryPage():
     st.title("Past Currency Conversions")
     
     history=load_history()
     if history:
          #Header row
          h_col1,h_col2,h_col3,h_col4,h_col5,h_col6=st.columns([2,2,2,2,2,1])
          h_col1.markdown("**Date & Time**") #Displays bold text as column headers for the history table
          h_col2.markdown("**From**")
          h_col3.markdown("**To**")
          h_col4.markdown("**Amount**")
          h_col5.markdown("**Converted**")
          h_col6.markdown("**Delete**")
          for i, record in enumerate(history[::-1]):
            col1,col2,col3,col4,col5,col6=st.columns([2,2,2,2,2,1])  
            col1.write(record["datetime"])
            col2.write(record["from"])
            col3.write(record["to"])
            col4.write(f'{record["amount"]}')
            col5.write(f'{record["converted"]}')
            if col6.button("Delete", key=f"del_{i}"): #dynamically generated in a loop
                #Calculates the correct original index of the record to be removed because the loop iterates in reverse
                index_to_remove = len(history) - 1 - i  
                removeButton(index_to_remove)

          st.markdown("---")
          if st.button("Clear All History"):
            clear_history()
     else:
        st.info("No past conversions available.")




def runConversionPage():
     api_key = load_api_key()
     defaultCurrency = "LKR"

     initialRates = fetch_exchange_rates(defaultCurrency, api_key)
     if not initialRates:
        return

     currencyCodes = list(initialRates.keys())
     baseCurrency, targetCurrency = currency_selector(currencyCodes)

     latestRates = fetch_exchange_rates(baseCurrency, api_key)
     if not latestRates:
        return

     rateForward = display_exchange_rates(baseCurrency, targetCurrency, latestRates)
     convertAmount(baseCurrency, targetCurrency, rateForward)

    
def main():
       
       st.set_page_config(page_title="Currency Converter", layout="wide")

          #Creates a select box in the Streamlit sidebar
       page = st.sidebar.selectbox("Choose a page", ["Convert", "History"])

       if page == "Convert":
        runConversionPage()
       elif page == "History":
        show_HistoryPage()
 
       #entry point for running
if __name__=="__main__":
       main() # only when the script is executed directly
              
