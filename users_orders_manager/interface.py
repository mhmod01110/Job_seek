from users_orders_manager.users_handler import *
from users_orders_manager.utils import *
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
email_db_path = os.path.join(parent_dir, "Processed_Data", "emails_database")
email_df = load_and_concat_csvs(email_db_path)
email_db = group_email_db(email_df)
cities_list = email_df["city"].unique()
email_df["sector"] = email_df["sectors"].apply(
    lambda value: ast.literal_eval(value) if isinstance(value, str) else value
)

# Extract unique sectors
sectors_list = list({sector for sectors_list in email_df["sector"] for sector in sectors_list})

user_manager = UserManager(session)
order_manager = OrderManager(session, email_db)

# Initialize City and Sector Tables
def initialize_cities_and_sectors():
    """Fill City and Sector tables with initial data from cities_list and sectors_list."""
    # Add cities
    for city_name in cities_list:
        if not session.query(City).filter_by(name=city_name).first():
            session.add(City(name=city_name))

    # Add sectors
    for sector_name in sectors_list:
        if not session.query(Sector).filter_by(name=sector_name).first():
            session.add(Sector(name=sector_name))

    session.commit()
    print("City and Sector tables initialized.")
    

def print_users():
    for user in user_manager.get_all_users():
        print(f"ID: {user.id}")
        print(f"Name: {user.name}")
        print(f"Email: {user.email}")
        print(f"User Type: {user.user_type.value}")
        print(f"Request Num: {user.request_num}")
        print(f"Period Days: {user.period_days}")
        print(f"Last Request Date: {user.last_request_date}")
        print(f"User Directory: {user.user_dir}")
        print("-" * 40)  # Separator for readability


# Use Case 1: User Creation
def create_user(name, email, user_type, request_num, period_days=None):
    user = user_manager.create_user(name, email, user_type, request_num, period_days)
    return user


# Use Case 2: User Retrieval by ID
def get_user_by_id(user_id):
    user = user_manager.get_user_by_id(user_id)
    return user


# Use Case 3: Retrieve All Users
def get_all_users():
    users = user_manager.get_all_users()
    return users


# Use Case 4: Update User Information
def update_user(user_id, **kwargs):
    return user_manager.update_user(user_id, **kwargs)


# Use Case 5: Delete User by ID
def delete_user(user_id):
    user_manager.delete_user(user_id)


# Use Case 6: Export Users to CSV
def export_users_to_csv(file_path="users_export.csv"):
    user_manager.export_to_csv(file_path)


# Adjusted Use Case 7: Order Creation for User
def create_order_for_user(user_id, df, retrieved_posts=0, city_names=None, sector_names=None):
    """
    Create an order for a user, associating it with cities and sectors if provided.
    """
    order = order_manager.create_order(
        user_id, 
        df, 
        retrieved_posts, 
        city_names=city_names, 
        sector_names=sector_names
    )
    return order


# Use Case 8: Retrieve Order by ID
def get_order_by_id(order_id):
    order = order_manager.get_order_by_id(order_id)
    return order


# Use Case 9: Retrieve All Orders
def get_all_orders():
    orders = order_manager.get_all_orders()
    return orders


# Adjusted Use Case 10: Update Order Information
def update_order(order_id, city_names=None, sector_names=None, **kwargs):
    """
    Update order information and associate it with new cities or sectors if provided.
    """
    order_manager.update_order(
        order_id, 
        city_names=city_names, 
        sector_names=sector_names, 
        **kwargs
    )


# Use Case 11: Delete Order by ID
def delete_order(order_id):
    order_manager.delete_order(order_id)


# Use Case 12: Handle Post Request for a User
def handle_order(order_id, email_db):
    status_flag = order_manager.handle_order(order_id, email_db)
    return status_flag


# Use Case 13: Get Available Posts for a User
def get_available_posts(email_db, user):
    available_posts = order_manager.get_available_posts(email_db, user)
    return available_posts


# Use Case 14: Export Orders to CSV
def export_orders_to_csv(file_path="orders_export.csv"):
    order_manager.export_to_csv(file_path)

# Automatically Sense and Add New Cities and Sectors
def auto_add_city_and_sector(city_names, sector_names):
    """
    Check and add new cities and sectors to their respective tables.
    """
    if city_names:
        for city_name in city_names:
            if not session.query(City).filter_by(name=city_name).first():
                session.add(City(name=city_name))

    if sector_names:
        for sector_name in sector_names:
            if not session.query(Sector).filter_by(name=sector_name).first():
                session.add(Sector(name=sector_name))

    session.commit()
    print("New cities and sectors added to the database, if any.")

# Initialize City and Sector Tables
initialize_cities_and_sectors()
