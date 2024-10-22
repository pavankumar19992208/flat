# Install necessary packages
# !pip install streamlit pymongo

import streamlit as st
from pymongo import MongoClient
from urllib.parse import quote_plus
import pandas as pd

# Encode the username and password
username = quote_plus("pramodpulicherla350")
password = quote_plus("Amma@9502")

# MongoDB Atlas connection setup
uri = f"mongodb+srv://{username}:{password}@cluster0.qneod.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
db = client["investment_tracker"]
users_collection = db["users"]
expenses_collection = db["expenses"]
monthly_expected_collection = db["monthly_expected"]
cred_collection = db["cred"]

# Streamlit app setup
st.markdown(
    """
    <style>
    .title {
        font-size: 24px;
        text-align: center;
        margin-bottom: 10px;
    }
    .button-row {
        display: flex;
        justify-content: space-between;
        width: 300px;
        max-width: 300px;
        margin: 0 auto 20px auto; /* Center the button row */
    }
    
    .button-row > div {
        flex: 1;
        margin: 0 2px; /* Reduce the gap between buttons */
    }
    .button-row button {
        width: 40px; /* Set button width */
        height: 20px; /* Set button height */
        font-size: 8px; /* Reduce font size */
    }
    .form-container {
        margin-bottom: 10px;
    }
    .form-container input, .form-container select {
        width: 100%;
        padding: 10px;
        margin-bottom: 10px;
        font-size: 16px;
    }
    .form-container button {
        width: 100%;
        padding: 5px;
        font-size: 10px;
    }
    @media (max-width: 600px) {
        .button-row {
            flex-direction: column;
            align-items: center;
        }
        .button-row > div {
            margin: 5px 0; /* Adjust margin for small screens */
        }
    }
    .note {
        color: red;
        font-size: 12px;
        text-align: center;
        margin-top: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar menu
st.sidebar.title("Menu")
page = st.sidebar.radio("Go to", ["Portfolio", "Investment Tracker", "Grocery", "Expenditures"], index=0)

# PIN authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def authenticate(pin):
    cred = cred_collection.find_one({"pin": pin})
    if cred:
        st.session_state.authenticated = True
        st.success("Authenticated successfully!")
    else:
        st.error("Invalid PIN. Please try again.")

if not st.session_state.authenticated:
    pin = st.text_input("Enter PIN to update details", type="password")
    if st.button("Authenticate"):
        authenticate(pin)

if page == "Investment Tracker":
    st.markdown('<h1 class="title">INVESTMENT TRACKER</h1>', unsafe_allow_html=True)

    if st.session_state.authenticated:
        # Buttons in a single row within 300px width
        st.markdown('<div class="button-row">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            if st.button("Add Investor"):
                st.session_state.show_add_investor = not st.session_state.get('show_add_investor', False)
                st.session_state.show_deposit = False
                st.session_state.show_expense = False
                st.session_state.show_monthly_expected = False
        with col2:
            if st.button("Deposit"):
                st.session_state.show_deposit = not st.session_state.get('show_deposit', False)
                st.session_state.show_add_investor = False
                st.session_state.show_expense = False
                st.session_state.show_monthly_expected = False
        with col3:
            if st.button("Expense"):
                st.session_state.show_expense = not st.session_state.get('show_expense', False)
                st.session_state.show_add_investor = False
                st.session_state.show_deposit = False
                st.session_state.show_monthly_expected = False
        with col4:
            if st.button("Monthly Expected"):
                st.session_state.show_monthly_expected = not st.session_state.get('show_monthly_expected', False)
                st.session_state.show_add_investor = False
                st.session_state.show_deposit = False
                st.session_state.show_expense = False
        st.markdown('</div>', unsafe_allow_html=True)

        # Add Investor Form
        if st.session_state.get('show_add_investor', False):
            with st.form(key='add_investor_form', clear_on_submit=True):
                st.markdown('<div class="form-container">', unsafe_allow_html=True)
                investor_name = st.text_input("Enter Investor Name")
                submit_button = st.form_submit_button(label='Submit')
                if submit_button:
                    if investor_name:
                        users_collection.insert_one({"name": investor_name})
                        st.success(f"Investor '{investor_name}' added successfully!")
                    else:
                        st.error("Please enter a name.")
                st.markdown('</div>', unsafe_allow_html=True)

        # Deposit Form
        if st.session_state.get('show_deposit', False):
            with st.form(key='deposit_form', clear_on_submit=True):
                st.markdown('<div class="form-container">', unsafe_allow_html=True)
                user_list = [user["name"] for user in users_collection.find()]
                selected_user = st.selectbox("Select Investor", user_list)
                deposit_amount = st.number_input("Enter Amount", min_value=0.0, step=0.01, format="%.2f")
                submit_button = st.form_submit_button(label='Submit')
                if submit_button:
                    if selected_user and deposit_amount > 0:
                        user = users_collection.find_one({"name": selected_user})
                        if "deposit" in user:
                            new_amount = user["deposit"] + deposit_amount
                        else:
                            new_amount = deposit_amount
                        users_collection.update_one({"name": selected_user}, {"$set": {"deposit": new_amount}})
                        st.success(f"Deposited {deposit_amount:.2f} to {selected_user}. Total deposit: {new_amount:.2f}")
                    else:
                        st.error("Please select an investor and enter a valid amount.")
                st.markdown('</div>', unsafe_allow_html=True)

        # Expense Form
        if st.session_state.get('show_expense', False):
            with st.form(key='expense_form', clear_on_submit=True):
                st.markdown('<div class="form-container">', unsafe_allow_html=True)
                expense_name = st.text_input("Expense Name")
                expense_amount = st.number_input("Enter Amount", min_value=0.0, step=0.01, format="%.2f")
                submit_button = st.form_submit_button(label='Submit')
                if submit_button:
                    if expense_name and expense_amount > 0:
                        expenses_collection.insert_one({"name": expense_name, "amount": expense_amount})
                        total_expenses = sum(expense["amount"] for expense in expenses_collection.find())
                        st.success(f"Expense '{expense_name}' of {expense_amount:.2f} added. Total expenses: {total_expenses:.2f}")
                    else:
                        st.error("Please enter a valid expense name and amount.")
                st.markdown('</div>', unsafe_allow_html=True)

        # Monthly Expected Form
        if st.session_state.get('show_monthly_expected', False):
            with st.form(key='monthly_expected_form', clear_on_submit=True):
                st.markdown('<div class="form-container">', unsafe_allow_html=True)
                emi_name = st.text_input("EMI Name")
                emi_amount = st.number_input("Enter Amount", min_value=0.0, step=0.01, format="%.2f")
                total_emi_amount = sum(item["amount"] for item in monthly_expected_collection.find())
                st.write(f"Total EMI Amount: {total_emi_amount:.2f}")
                submit_button = st.form_submit_button(label='Submit')
                if submit_button:
                    if emi_name and emi_amount > 0:
                        monthly_expected_collection.insert_one({"name": emi_name, "amount": emi_amount})
                        st.success(f"Monthly expected EMI '{emi_name}' of {emi_amount:.2f} added.")
                    else:
                        st.error("Please enter a valid EMI name and amount.")
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("Please authenticate to update details.")

elif page == "Grocery":
    st.markdown('<h1 class="title">GROCERY</h1>', unsafe_allow_html=True)
    st.write("This is the Grocery page.")

elif page == "Expenditures":
    st.markdown('<h1 class="title">EXPENDITURES</h1>', unsafe_allow_html=True)

    # Monthly Installment Table
    st.markdown("### Monthly Installment Table")
    emi_data = list(monthly_expected_collection.find())
    emi_df = pd.DataFrame(emi_data).drop(columns=['_id'])
    st.table(emi_df)

    # Expenses Table
    st.markdown("### Expenses Table")
    expenses_data = list(expenses_collection.find())
    expenses_df = pd.DataFrame(expenses_data).drop(columns=['_id'])
    st.table(expenses_df)

elif page == "Portfolio":
    st.markdown('<h1 class="title">PORTFOLIO</h1>', unsafe_allow_html=True)

    # Fetch data from the database
    users = list(users_collection.find())
    total_expenses = sum(expense["amount"] for expense in expenses_collection.find())
    total_funded = sum(user.get("deposit", 0) for user in users)
    to_be_funded = total_expenses - total_funded

    # Prepare data for the table
    portfolio_data = []
    for user in users:
        user_name = user["name"]
        funded = user.get("deposit", 0)
        expenditure = (funded / total_funded) * total_expenses if total_funded > 0 else 0
        amount = funded - expenditure
        equity_percentage = (1/ 50000) * expenditure if 50000 > 0 else 0
        portfolio_data.append({
            "User": user_name,
            "Funded": f"{funded:.2f}",
            "Expenditure": f"{expenditure:.2f}",
            "Amount": f"{amount:.2f}",
            "Equity %": f"{equity_percentage:.2f}"
        })

    # Convert to DataFrame
    df = pd.DataFrame(portfolio_data)

    # Display the table
    st.table(df)

    # Display total expenses, total funded, and to be funded
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Total Expenses: {total_expenses:.2f}**")
    with col2:
        st.markdown(f"**Total Funded: {total_funded:.2f}**")
    with col3:
        st.markdown(f"**To Be Funded: {to_be_funded:.2f}**")

    # Button to show expense details
    if st.button("Show Expense Details"):
        expenses = list(expenses_collection.find())
        expense_details = pd.DataFrame(expenses).drop(columns=['_id'])
        st.table(expense_details)

    # Add note below the portfolio page
    st.markdown('<p class="note">*Note: The fields expenses, amount, and equity changes according to the ratio that you funded.</p>', unsafe_allow_html=True)

# To run the app, use the command: streamlit run your_script_name.py