from flask import Flask, render_template, request, send_file
import pandas as pd
import os

app = Flask(__name__)

# Simulated comps data for demonstration
MOCK_COMPS = [
    {"Address": "123 Land St", "Acres": 1.0, "Sold Price": 15000, "Sold Date": "2024-12-01"},
    {"Address": "456 Dirt Rd", "Acres": 0.8, "Sold Price": 12000, "Sold Date": "2024-11-15"},
    {"Address": "789 Field Ave", "Acres": 1.2, "Sold Price": 18000, "Sold Date": "2025-01-10"},
]

@app.route('/', methods=['GET', 'POST'])
def home():
    comps = []
    target_offer_low = target_offer_high = profit_target = 0

    if request.method == 'POST':
        address = request.form.get('address')
        comps = MOCK_COMPS  # Replace with scraped results
        avg_price_per_acre = sum([c['Sold Price']/c['Acres'] for c in comps]) / len(comps)

        target_offer_low = round(avg_price_per_acre * 0.30, 2)
        target_offer_high = round(avg_price_per_acre * 0.45, 2)
        profit_target = 7000

    return render_template('index.html', comps=comps,
                           target_offer_low=target_offer_low,
                           target_offer_high=target_offer_high,
                           profit_target=profit_target)

@app.route('/download', methods=['POST'])
def download():
    comps_df = pd.DataFrame(MOCK_COMPS)
    file_path = 'comps_output.xlsx'
    comps_df.to_excel(file_path, index=False)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
