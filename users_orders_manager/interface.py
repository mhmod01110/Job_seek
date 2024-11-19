from users_orders_manager.users_handler import *
from users_orders_manager.utils import *
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
email_db_path = os.path.join(parent_dir, "Processed_Data", "emails_database")
email_db = load_and_concat_csvs(email_db_path)
email_db = group_email_db(email_db)


user_manager = UserManager(session)
order_manager = OrderManager(session, email_db)

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


# Use Case 7: Order Creation for User
def create_order_for_user(user_id, df, retrieved_posts=0):
    order = order_manager.create_order(user_id, df, retrieved_posts)
    return order


# Use Case 8: Retrieve Order by ID
def get_order_by_id(order_id):
    order = order_manager.get_order_by_id(order_id)
    return order


# Use Case 9: Retrieve All Orders
def get_all_orders():
    orders = order_manager.get_all_orders()
    return orders


# Use Case 10: Update Order Information
def update_order(order_id, **kwargs):
    order_manager.update_order(order_id, **kwargs)


# Use Case 11: Delete Order by ID
def delete_order(order_id):
    order_manager.delete_order(order_id)


# Use Case 12: Handle Post Request for a User
def handle_order(order_id, email_db):
    order_manager.handle_order(order_id, email_db)


# Use Case 13: Get Available Posts for a User
def get_available_posts(email_db, user):
    available_posts = order_manager.get_available_posts(email_db, user)
    return available_posts


# Use Case 14: Export Orders to CSV
def export_orders_to_csv(file_path="orders_export.csv"):
    order_manager.export_to_csv(file_path)

