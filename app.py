from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from database import Database
import json
import csv
from io import StringIO

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
db = Database()

@app.route('/')
def index():
    """Serve the dashboard"""
    return render_template('dashboard.html')

@app.route('/api/watchlist', methods=['GET'])
def get_watchlist():
    """Get all stocks in the watchlist"""
    try:
        stocks = db.get_all_stocks()
        return jsonify({
            'success': True,
            'count': len(stocks),
            'stocks': stocks
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/watchlist/add', methods=['POST'])
def add_to_watchlist():
    """Add stock(s) to the watchlist - accepts single stock or array"""
    try:
        data = request.get_json()
        
        # Handle both single stock and array of stocks
        if isinstance(data, list):
            results = []
            for stock_data in data:
                result = db.add_stock(stock_data)
                results.append({
                    'symbol': stock_data.get('symbol'),
                    'success': result['success'],
                    'message': result['message']
                })
            return jsonify({
                'success': True,
                'results': results
            })
        else:
            result = db.add_stock(data)
            return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/watchlist/<symbol>', methods=['GET'])
def get_stock(symbol):
    """Get a specific stock by symbol"""
    try:
        stock = db.get_stock(symbol)
        if stock:
            return jsonify({'success': True, 'stock': stock})
        return jsonify({'success': False, 'message': 'Stock not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/watchlist/<symbol>', methods=['PUT'])
def update_stock(symbol):
    """Update stock information"""
    try:
        data = request.get_json()
        result = db.update_stock(symbol, data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/watchlist/<symbol>', methods=['DELETE'])
def delete_stock(symbol):
    """Remove stock from watchlist"""
    try:
        result = db.delete_stock(symbol)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/watchlist/sector/<sector>', methods=['GET'])
def get_by_sector(sector):
    """Get all stocks in a specific sector"""
    try:
        stocks = db.get_stocks_by_sector(sector)
        return jsonify({
            'success': True,
            'sector': sector,
            'count': len(stocks),
            'stocks': stocks
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/watchlist/export/json', methods=['GET'])
def export_json():
    """Export watchlist as JSON"""
    try:
        stocks = db.get_all_stocks()
        return jsonify(stocks)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/watchlist/export/csv', methods=['GET'])
def export_csv():
    """Export watchlist as CSV"""
    try:
        stocks = db.get_all_stocks()
        
        if not stocks:
            return "No stocks in watchlist", 404
        
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=stocks[0].keys())
        writer.writeheader()
        writer.writerows(stocks)
        
        return output.getvalue(), 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': 'attachment; filename=watchlist.csv'
        }
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
