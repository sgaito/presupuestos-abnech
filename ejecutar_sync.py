from app import sync_precios_google_sheet

success, message, count = sync_precios_google_sheet()
print(message)