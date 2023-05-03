# -*- coding: utf-8 -*-
{
    'name': "Real Time Stock XLSX Report | Stock Inventory Report | "
            "Stock Inventory Real Time Report",
    'summary': """ Get stock report in xlsx file for any location or warehouse or date range
    """,
    'description': """
        Stock Report in XLSX
        ==================
        This modules gives you a comprehensive stock report based on various filters.
        
        Features:
        ---------
            * Get the output in a xlsx file listing Product name, Internal Reference
            * Option to filter by Product
            * Option to filter by Stock Location
            * Option for Opening, Incoming and Outgoing, closing for a given date range
            * Option for fetching Valuation also
            * Generate Stock Inventory Real Time Report in XLSX by specific dates
            * Search by Location and Warehouse
            * Multi Company Specific Inventory Report
            
        Print Stock Inventory Real Time Report
        stock valuation report on date
        location wise stock report
        warehouse wise stock report
        Stock Inventory Report Stock Inventory XLSX Report
    
    """,
    'author': "Geo Technosoft",
    'website': "http://www.geotechnosoft.com/",
    'category': 'Warehouse Management',
    'version': '13.0.0.1',
    'sequence': 1,
    'depends': ['stock', 'stock_account'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/xlsx_output_view.xml',
        'wizard/daily_stock_report_view.xml',
        'views/stock_location_view.xml',
    ],
    'images': ['static/description/banner.png'],
    'price': 39.99,
    'currency': 'EUR',
    'license': 'OPL-1',
    'installable': True,
    'application': True,
}
