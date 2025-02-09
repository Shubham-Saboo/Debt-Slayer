import streamlit as st
import json
import time
from datetime import datetime, timedelta
from rag_pipeline import answer_query, retrieve_docs, llm_model
from dotenv import load_dotenv

load_dotenv()

# ======================
# 🎮 Game Theme Setup
# ======================
st.markdown("""
<style>
    :root {
        --dragon-red: #d90429;
        --treasure-gold: #ffd60a;
        --hero-blue: #118ab2;
        --dark-cave: #2b2d42;
    }

    .main {
        background: var(--dark-cave);
        color: white;
        font-family: 'Arial Black', fantasy;
    }
            
    .stButton {
    display: flex;
    justify-content: center;
    }
            
    .stButton>button {
        background: var(--hero-blue)!important;
        border: 2px solid var(--treasure-gold)!important;
        color: white!important;
    }

    .stProgress > div > div > div {
        background: var(--treasure-gold)!important;
    }
</style>
""", unsafe_allow_html=True)

# ======================
# 🧠 Enhanced Algorithm Core (Updated)
# ======================
def select_strategy(debts, motivation, stress_level):
    """Selects a debt repayment strategy based on user motivation and stress level."""
    if motivation == "Quick Strikes":
        return "Avalanche Assault"  # Pay off high-interest debts first
    elif motivation == "Long Campaign":
        return "Snowball Charge"  # Pay off smaller debts first
    else:
        # Stress level can influence the strategy
        if stress_level == "Calm":
            return "Avalanche Assault"
        elif stress_level == "Tense":
            return "Snowball Charge"
        else:  # Panic
            # Mix of strategy for quick wins and long-term control
            return "Hybrid Strategy"


def calculate_debt_payoff(debts, strategy, available_emi, stress_level):
    """Enhanced payoff calculator with precise tracking"""
    debts = [d.copy() for d in debts]
    for d in debts:
        d['balance'] = float(d['balance'])
        d['total_interest'] = 0.0

    total_min = sum(d['min_emi'] for d in debts)
    extra_budget = max(available_emi - total_min, 0)  # Ensure non-negative
    
    # Strategy sorting
    if strategy == "Avalanche Assault":
        ordered_debts = sorted(debts, key=lambda x: (-x['apr'], x['balance']))
    elif strategy == "Snowball Charge":
        ordered_debts = sorted(debts, key=lambda x: (x['balance'], -x['apr']))
    else:
        stress_factor = {"Calm": 0.2, "Tense": 0.5, "Panic": 0.8}[stress_level]
        threshold = sum(d['balance'] for d in debts) * stress_factor / len(debts)
        ordered_debts = sorted(debts, key=lambda x: (
            -x['apr'] if x['balance'] > threshold else x['balance'],
            x['balance']
        ))

    payoff_plan = []
    months = 0
    debt_tracker = {d['name']: {'paid_month': None, 'total_interest': 0.0} for d in debts}
    current_date = datetime.now()

    while any(d['balance'] > 0.01 for d in debts):  # Floating point tolerance
        months += 1
        monthly_interest = 0
        paid_this_month = []

        # Process minimum payments
        for d in debts:
            if d['balance'] <= 0:
                continue
                
            interest = d['balance'] * d['apr']/1200
            payment = min(d['min_emi'], d['balance'] + interest)
            
            # Ensure payment covers at least interest
            if payment < interest:
                payment = min(interest + 0.01, d['balance'] + interest)
                
            principal = payment - interest
            d['balance'] -= principal
            d['total_interest'] += interest
            debt_tracker[d['name']]['total_interest'] += interest
            monthly_interest += interest

        # Process extra payments
        remaining_extra = extra_budget
        for d in ordered_debts:
            if d['balance'] <= 0.01 or remaining_extra <= 0:
                continue
                
            possible_payment = min(remaining_extra, d['balance'])
            d['balance'] -= possible_payment
            remaining_extra -= possible_payment
            
            if d['balance'] <= 0.01 and not debt_tracker[d['name']]['paid_month']:
                paid_this_month.append(d['name'])
                debt_tracker[d['name']]['paid_month'] = months

        # Track payoff progress
        if paid_this_month:
            payoff_plan.append({
                'month': months,
                'paid_debts': paid_this_month,
                'remaining_debt': sum(d['balance'] for d in debts)
            })

    return {
        'total_interest': sum(d['total_interest'] for d in debts),
        'months': months,
        'payoff_plan': payoff_plan,
        'debt_tracker': debt_tracker
    }
# ======================
# 🛡️ User Input Section
# ======================
st.markdown(
    "<h1 style='text-align: center; font-size: 50px;'>⚔️ Debt Slayer ⚔️</h1>", 
    unsafe_allow_html=True
)

# user_data = {}

# def select_strategy(debts, motivation):
#     """Selects debt repayment strategy based on motivation and APR."""
#     if motivation == "Quick Strikes":
#         return "Avalanche Assault"  # Highest APR first
#     else:
#         return "Snowball Charge"  # Smallest debt first

# with st.form("warrior_form"):
#     # Core Financials
#     with st.expander("💰 Financial Profile", expanded=True):
#         user_data["income"] = st.number_input("Monthly Gold Income", min_value=0, step=100)
#         user_data["expenses"] = st.number_input("Monthly Expenses", min_value=0, step=100)
#         user_data["emi"] = st.slider("Available for Battles", min_value=100, max_value=10000, step=100)

#     # Debt Inputs
#     with st.expander("🧌 Debt Monsters", expanded=True):
#         debts = []
#         num_debts = st.number_input("How many debt monsters do you have?", min_value=1, step=1)
#         for i in range(num_debts):
#             cols = st.columns([3, 2, 2, 2])
#             debts.append({
#                 "name": cols[0].text_input(f"Monster {i+1} Name", f"Debt Monster {i+1}"),
#                 "balance": cols[1].number_input("Gold Owed", min_value=0, step=100, key=f"balance_{i}"),
#                 "apr": cols[2].number_input("Dragon Fire % (APR)", min_value=0.0, step=0.1, key=f"apr_{i}"),
#                 "min_emi": cols[3].number_input("Min EMI", min_value=0, step=50, key=f"min_emi_{i}")
#             })

#     # Behavioral Profile
#     with st.expander("🧠 Battle Strategy", expanded=True):
#         user_data["motivation"] = st.radio("⚔️ Motivation", ["Quick Strikes", "Long Campaign"], index=0)
#         user_data["stress"] = st.select_slider("😨 Stress Level", ["Calm", "Tense", "Panic"], value="Panic")

user_data = {}

with st.form("warrior_form"):
    with st.expander("💰 Financial Profile", expanded=True):
        user_data["income"] = st.number_input("Monthly Gold Income", min_value=0, step=100)
        user_data["expenses"] = st.number_input("Monthly Expenses", min_value=0, step=100)
        user_data["emi"] = st.slider("Available for Battles", min_value=100, max_value=10000, step=100)
    
    with st.expander("🧌 Debt Monsters", expanded=True):
        debts = []
        num_debts = st.number_input("How many debt monsters do you have?", min_value=1, step=1)
        for i in range(num_debts):
            cols = st.columns([3,2,2,2])
            debts.append({
                "name": cols[0].text_input(f"Monster {i+1} Name", f"Debt Monster {i+1}"),
                "balance": cols[1].number_input("Gold Owed", min_value=0, step=100, key=f"balance_{i}"),
                "apr": cols[2].number_input("Dragon Fire % (APR)", min_value=0.0, step=0.1, key=f"apr_{i}"),
                "min_emi": cols[3].number_input("Min EMI", min_value=0, step=50, key=f"min_emi_{i}")
            })
    
    with st.expander("🧠 Battle Strategy", expanded=True):
        user_data["motivation"] = st.radio("⚔️ Motivation", ["Quick Strikes", "Long Campaign"], index=0)
        user_data["stress"] = st.select_slider("😨 Stress Level", ["Calm", "Tense", "Panic"], value="Panic")
    # Submit Form
    # Center the submit button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.form_submit_button("⚔️ Prepare for Battle - Submit Data"):
            with open("user_data.json", "w") as f:
                json.dump({"user": user_data, "debts": debts}, f)
    # if st.form_submit_button("⚔️ Prepare for Battle - Submit Data"):
    #     with open("user_data.json", "w") as f:
    #         json.dump({"user": user_data, "debts": debts}, f)

# ======================
# 🧙 AI Battle Planner
# ======================
col1, col2 = st.columns([2, 1])  # Adjust the width ratio if needed
with col1:
    ask_question = st.button("⚔️ Generate Battle Plan - Analyze Data")
with col2:
    show_think = st.checkbox("Reveal Magic")
think_text = ""
if ask_question:
    # strategy = select_strategy(debts, user_data["motivation"])
    # battle_plan = {
    #     "strategy": strategy,
    #     "total_debt": sum(d["balance"] for d in debts),
    #     "interest_paid_yearly": sum(d["balance"] * (d["apr"] / 100) for d in debts),
    #     "free_date": (datetime.now() + timedelta(days=730)).strftime("%Y-%m-%d"),
    #     "steps": [
    #         {"target": d["name"], "payment": user_data["emi"] * (d["apr"] / sum(d["apr"] for d in debts)), "months": d["balance"] // (user_data["emi"] * (d["apr"] / sum(d["apr"] for d in debts)))}
    #         for d in sorted(debts, key=lambda x: -x["apr"] if strategy == "Avalanche Assault" else x["balance"])
    #     ]
    # }

    # # Save battle plan as JSON
    # with open("battle_plan.json", "w") as f:
    #     json.dump(battle_plan, f)

    # # Display Results
    
    # st.subheader("🏆 Battle Summary")
    # cols = st.columns(3)
    # cols[0].metric("Total Debt", f"${battle_plan['total_debt']:,}")
    # cols[1].metric("Interest Paid Yearly", f"${battle_plan['interest_paid_yearly']:.2f}")
    # cols[2].metric("Freedom Date", battle_plan["free_date"])
    
    # # st.progress(0.3, text="🔥 30% Path Cleared")

    # st.subheader("⚔️ Battle Plan")
    # for i, step in enumerate(battle_plan["steps"]):
    #     with st.expander(f"Step {i+1}: Attack {step['target']}"):
    #         st.write(f"⚔️ Pay ${step['payment']:.2f}/month → Vanquish in {int(step['months'])} months")

    with open("user_data.json", "r") as f:
            data = json.load(f)
            user_data = data['user']
            debts = data['debts']

    strategy = select_strategy(debts, user_data["motivation"], user_data["stress"])
    current_year = datetime.now().year
    
    # Calculate scenarios
    min_battle = calculate_debt_payoff(debts, strategy, sum(d['min_emi'] for d in debts), user_data["stress"])
    current_battle = calculate_debt_payoff(debts, strategy, user_data["emi"], user_data["stress"])

    # 1️⃣ Overall Summary (Big Picture View)
    st.markdown("## 1️⃣ Overall Summary (Big Picture View)")

    total_debt_remaining = sum(d['balance'] for d in debts)
    total_interest_paid = current_battle['total_interest']
    projected_debt_free_date = current_year + current_battle['months'] // 12

    st.write(f"✅ Total Debt Remaining: ${total_debt_remaining:,.0f}")
    st.write(f"✅ Current Interest Paid Yearly: ${total_interest_paid / current_battle['months'] * 12:,.0f}")
    st.write(f"✅ Projected Debt-Free Date: {projected_debt_free_date} (at min EMI)")
    st.write(f"✅ Strategy Chosen: {strategy}")

    # 2️⃣ Suggested EMI & Interest Savings
    st.markdown("## 2️⃣ Suggested EMI & Interest Savings")
    table_data = []
    for d in debts:
        min_tracker = min_battle['debt_tracker'][d['name']]
        current_tracker = current_battle['debt_tracker'][d['name']]
        
        min_date = (datetime.now() + timedelta(days=30*min_tracker['paid_month'])).year if min_tracker['paid_month'] else "-"
        current_date = (datetime.now() + timedelta(days=30*current_tracker['paid_month'])).year if current_tracker['paid_month'] else "-"
        
        interest_saved = min_tracker['total_interest'] - current_tracker['total_interest']
        
        table_data.append({
            "Debt": d['name'],
            "Old Date": min_date if min_date != datetime.now().year else "-",
            "New Date": current_date,
            "Saved": interest_saved
        })
    
    st.table(table_data)

    # 3️⃣ Action Plan Breakdown (Step-by-Step)
    st.markdown("## 3️⃣ Action Plan Breakdown (Step-by-Step)")
    for i, step in enumerate(current_battle['payoff_plan']):
        if step['paid_debts']:
            saved = sum(
                current_battle['debt_tracker'][d]['total_interest'] - 
                min_battle['debt_tracker'][d]['total_interest'] 
                for d in step['paid_debts']
            )
            st.markdown(f"""
            **Step {i+1}: Attack the {", ".join(step['paid_debts'])}!**  
            ⚔️ Pay {sum(d['min_emi'] for d in debts if d['name'] in step['paid_debts']):.0f}/month  
            🗓️ Clears in {step['month']} months  
            💰 Savings: {-1*saved:.0f} interest
            """)

    financial_context = f"""
    Monthly Income: ${user_data["income"]}
    Monthly Expenses: ${user_data["expenses"]}
    Available for Battles: ${user_data["emi"]}
    Motivation: {user_data["motivation"]}
    Stress Level: {user_data["stress"]}
    """

    # Add details for each debt
    if debts:
        financial_context += "\nDebts:\n"
        for i, debt in enumerate(debts):
            financial_context += (
                f"Debt {i + 1}:\n"
                f"  Name: {debt['name']}\n"
                f"  Balance: ${debt['balance']}\n"
                f"  APR: {debt['apr']}%\n"
                f"  Min EMI: ${debt['min_emi']}\n"
            )

    # Combine user query with financial context
    full_query = f"You are a professional debt management advisor. Generate a concise and clear three point debt repayment strategy based on the following financial context:\n{financial_context}"

    # RAG Pipeline
    
    retrieved_docs = retrieve_docs(full_query)
    response = answer_query(documents=retrieved_docs, model=llm_model, query=full_query)

    import re
    def extract_think_content(text):
        """Extract content inside <think> tags and remove it from the main content."""
        think_match = re.search(r"<think>(.*?)</think>", text, re.DOTALL)
        think_content = think_match.group(1).strip() if think_match else "No additional information."
        
        # Remove <think> content from main response
        main_content = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
        
        return main_content, think_content
    
    main_text, think_text = extract_think_content(response.content)

    # --- UI STARTS HERE ---
    st.write(main_text)

    if show_think:
        if think_text:
            st.write("### Debt Slayer: Reasoning")
            st.write(think_text)
        else:
            st.write("enter query to see the reasoning")
        # Display LLM Response
        st.success("Strategy Generated!")
        # st.write(response.content)

# ======================
# 💬 Chatbot for Additional Queries
# ======================
st.subheader("💬 Ask the Debt Slayer")
user_query = st.text_area("Enter your query:", placeholder="Ask anything about your finances!")

financial_context = f"""
    Monthly Income: ${user_data["income"]}
    Monthly Expenses: ${user_data["expenses"]}
    Available for Battles: ${user_data["emi"]}
    Motivation: {user_data["motivation"]}
    Stress Level: {user_data["stress"]}
    """

# Add details for each debt
if debts:
    financial_context += "\nDebts:\n"
    for i, debt in enumerate(debts):
        financial_context += (
            f"Debt {i + 1}:\n"
            f"  Name: {debt['name']}\n"
            f"  Balance: ${debt['balance']}\n"
            f"  APR: {debt['apr']}%\n"
            f"  Min EMI: ${debt['min_emi']}\n"
        )

# Combine user query with financial context
full_query = f"""You are a professional debt management advisor. Generate a concise and clear debt repayment strategy based on the following financial context:\n{financial_context}
                Do not use the $ symbol while generating the response."""


if st.button("Ask"):
    if user_query:
        # Pass the user query to the LLM
        with st.spinner("Thinking..."):
            retrieved_docs = retrieve_docs(full_query+user_query)
            response = answer_query(documents=retrieved_docs, model=llm_model, query=full_query+user_query)
        
        # Display the response
        st.chat_message("user").write(user_query)
        st.chat_message("AI Financial Assistant").write(response.content)
    else:
        st.warning("Please enter a query!")

# ======================
# 🎮 Game Theme Setup
# ======================
