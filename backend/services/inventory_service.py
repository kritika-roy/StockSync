def calculate_inventory(df, forecast_results):

    inventory_results = {}

    products = forecast_results.keys()

    for product in products:

        # Predicted demand from ML model
        avg_daily_demand = forecast_results[product]["Predicted Daily Demand"]

        # Inventory parameters
        lead_time = 7
        safety_stock = 0.2 * avg_daily_demand

        # Reorder point formula
        reorder_point = (avg_daily_demand * lead_time) + safety_stock

        # Get latest stock value from dataframe
        current_stock = int(
            df[df["product_name"] == product]["current_stock"].iloc[-1]
        )

        # Stock decision
        if current_stock < reorder_point:
            status = "LOW_STOCK"
        else:
            status = "Stock Safe"

        inventory_results[product] = {
            "Reorder Point": int(round(reorder_point)),
            "Current Stock": current_stock,
            "Status": status
        }

    return inventory_results