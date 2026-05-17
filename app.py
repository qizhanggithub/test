import streamlit as st

st.title("Simple Addition Calculator")

a = st.number_input("Enter a", value=0.0)
b = st.number_input("Enter b", value=0.0)

result = a + b

st.success(f"Sum = {result}")