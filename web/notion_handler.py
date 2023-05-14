from notion_client import Client
from config import Config

notion = Client(auth=Config.NOTION_API_KEY)

def get_database_id(database_name):
    results = notion.search(filter={"property": "object", "value": "database"}).get("results")
    for result in results:
        if result['title'][0]['text']['content'] == database_name:
            return result['id']
    return None

def create_page(database_id, result):
    new_page = {
        "Location": {"title": [{"text": {"content": result['location']}}]},
        "Date Time": {"date": {"start": result['date_time'].isoformat()}},
        "Weather": {"rich_text": [{"text": {"content": result['weather']}}]},
        "Temperature": {"number": result['temperature']},
        "Wind Direction": {"rich_text": [{"text": {"content": result['wind_direction']}}]}
    }
    notion.pages.create(parent={"database_id": database_id}, properties=new_page)

def save_to_notion(result):
    database_name = "data"
    database_id = get_database_id(database_name)
    if database_id:
        create_page(database_id, result)
    else:
        print("Database not found. Please create a database with the name 'Photo Info'")
