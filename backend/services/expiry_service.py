def detect_expiry(df, forecast_results):

    expiry_results = {}

    # Shelf life (days)
    shelf_life_catalog = {
        "Rice": 365,
        "Oil": 365,
        "Sugar": 365,
        "Milk": 7,
        "Soap": 730
    }

    products = forecast_results.keys()

    for product in products:

        product_df = df[df["product_name"] == product]

        if product_df.empty:
            continue  # safety

        predicted_daily_demand = forecast_results[product]["Predicted Daily Demand"]

        shelf_life_days = shelf_life_catalog.get(product, 30)

        current_stock = int(product_df["current_stock"].iloc[-1])

        # Max possible sales before expiry
        possible_sales = predicted_daily_demand * shelf_life_days

        if current_stock > possible_sales:
            expiry_risk = int(round(current_stock - possible_sales))
            status = "Expiry Risk"
        else:
            expiry_risk = 0
            status = "Safe"

        expiry_results[product] = {
            "Shelf Life (days)": shelf_life_days,
            "Current Stock": current_stock,
            "Possible Sales Before Expiry": int(round(possible_sales)),
            "Potential Expiry Units": expiry_risk,

            # ✅ THIS IS THE FIX (CRITICAL)
            "units": expiry_risk,

            "Status": status
        }

    return expiry_results