from flask import Flask, request, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func

app = Flask(__name__)

# Create the database engine
engine = create_engine('postgresql://user:password@localhost/mydatabase')
Session = sessionmaker(bind=engine)

# Helper function to get month range
def get_month_range(month):
    from datetime import datetime
    import calendar
    start_date = datetime.strptime(f'2022-{month}-01', '%Y-%m-%d')
    end_date = start_date.replace(day=calendar.monthrange(start_date.year, start_date.month)[1])
    return start_date, end_date

@app.route('/transactions', methods=['GET'])
def list_transactions():
    session = Session()
    month = request.args.get('month')
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    start_date, end_date = get_month_range(month)
    
    query = session.query(ProductTransaction).filter(
        ProductTransaction.date_of_sale.between(start_date, end_date)
    )
    
    if search:
        query = query.filter(
            (ProductTransaction.title.ilike(f'%{search}%')) |
            (ProductTransaction.description.ilike(f'%{search}%')) |
            (ProductTransaction.price.ilike(f'%{search}%'))
        )
    
    total = query.count()
    transactions = query.offset((page - 1) * per_page).limit(per_page).all()
    
    results = [{
        'id': t.id,
        'title': t.title,
        'description': t.description,
        'price': t.price,
        'date_of_sale': t.date_of_sale,
        'category': t.category,
        'sold': t.sold
    } for t in transactions]
    
    session.close()
    
    return jsonify({'total': total, 'transactions': results})

@app.route('/statistics', methods=['GET'])
def statistics():
    session = Session()
    month = request.args.get('month')
    
    start_date, end_date = get_month_range(month)
    
    total_sales = session.query(func.sum(ProductTransaction.price)).filter(
        ProductTransaction.date_of_sale.between(start_date, end_date)
    ).scalar()
    
    sold_items = session.query(func.count(ProductTransaction.id)).filter(
        ProductTransaction.date_of_sale.between(start_date, end_date),
        ProductTransaction.sold.is_(True)
    ).scalar()
    
    not_sold_items = session.query(func.count(ProductTransaction.id)).filter(
        ProductTransaction.date_of_sale.between(start_date, end_date),
        ProductTransaction.sold.is_(False)
    ).scalar()
    
    session.close()
    
    return jsonify({
        'total_sales': total_sales,
        'sold_items': sold_items,
        'not_sold_items': not_sold_items
    })

@app.route('/bar_chart', methods=['GET'])
def bar_chart():
    session = Session()
    month = request.args.get('month')
    
    start_date, end_date = get_month_range(month)
    
    ranges = {
        '0-100': (0, 100),
        '101-200': (101, 200),
        '201-300': (201, 300),
        '301-400': (301, 400),
        '401-500': (401, 500),
        '501-600': (501, 600),
        '601-700': (601, 700),
        '701-800': (701, 800),
        '801-900': (801, 900),
        '901-above': (901, float('inf'))
    }
    
    result = {key: 0 for key in ranges.keys()}
    
    for key, (low, high) in ranges.items():
        count = session.query(func.count(ProductTransaction.id)).filter(
            ProductTransaction.date_of_sale.between(start_date, end_date),
            ProductTransaction.price.between(low, high)
        ).scalar()
        result[key] = count
    
    session.close()
    
    return jsonify(result)

@app.route('/pie_chart', methods=['GET'])
def pie_chart():
    session = Session()
    month = request.args.get('month')
    
    start_date, end_date = get_month_range(month)
    
    categories = session.query(
        ProductTransaction.category,
        func.count(ProductTransaction.id)
    ).filter(
        ProductTransaction.date_of_sale.between(start_date, end_date)
    ).group_by(ProductTransaction.category).all()
    
    result = {category: count for category, count in categories}
    
    session.close()
    
    return jsonify(result)

@app.route('/combined', methods=['GET'])
def combined():
    month = request.args.get('month')
    
    transactions_response = list_transactions()
    statistics_response = statistics()
    bar_chart_response = bar_chart()
    pie_chart_response = pie_chart()
    
    return jsonify({
        'transactions': transactions_response.get_json(),
        'statistics': statistics_response.get_json(),
        'bar_chart': bar_chart_response.get_json(),
        'pie_chart': pie_chart_response.get_json()
    })

if __name__ == '__main__':
    app.run(debug=True)
