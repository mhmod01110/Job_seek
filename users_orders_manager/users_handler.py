from sqlalchemy import create_engine, Table, Column, Integer, String, DateTime, Enum, ForeignKey, and_ , CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import pandas as pd
import enum
import uuid
import csv
import os

Base = declarative_base()

# Enum definitions
class UserType(enum.Enum):
    SingleRequest = "SingleRequest"
    Recurrent = "Recurrent"

class OrderStatus(enum.Enum):
    Complete = "Complete"
    Incomplete = "Incomplete"
    
# Users table
class User(Base):
    __tablename__ = "users"
    provided_posts = set()

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), unique=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    user_type = Column(Enum(UserType), nullable=False)
    request_num = Column(Integer, nullable=False, default=1)
    period_days = Column(Integer, nullable=True, default=None)
    last_request_date = Column(DateTime, nullable=True, default=None)
    user_dir = Column(String, default=lambda context: f"./data/{context.get_current_parameters()['name']}_{context.get_current_parameters()['id']}")

    orders = relationship("Order", back_populates="user")

    __table_args__ = (
        CheckConstraint(
            "(user_type = 'SingleRequest' AND period_days IS NULL) OR (user_type = 'Recurrent' AND period_days > 0)",
            name="check_period_days"
        ),
        CheckConstraint("request_num > 0", name="check_request_num_positive")
    )

order_city_association = Table(
    "order_city_association", Base.metadata,
    Column("order_id", Integer, ForeignKey("orders.order_id"), primary_key=True),
    Column("city_id", Integer, ForeignKey("cities.city_id"), primary_key=True)
)

order_sector_association = Table(
    "order_sector_association", Base.metadata,
    Column("order_id", Integer, ForeignKey("orders.order_id"), primary_key=True),
    Column("sector_id", Integer, ForeignKey("sectors.sector_id"), primary_key=True)
)


class City(Base):
    __tablename__ = "cities"
    
    city_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    orders = relationship("Order", secondary=order_city_association, back_populates="cities")

class Sector(Base):
    __tablename__ = "sectors"
    
    sector_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    orders = relationship("Order", secondary=order_sector_association, back_populates="sectors")

    
class Order(Base):
    __tablename__ = "orders"
    
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    order_date = Column(DateTime, default=datetime.now())
    retrieved_posts = Column(Integer, default=0)
    remaining_posts = Column(Integer, default=0)
    order_status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.Incomplete)
    
    cities = relationship("City", secondary=order_city_association, back_populates="orders")
    sectors = relationship("Sector", secondary=order_sector_association, back_populates="orders")
    
    user = relationship("User", back_populates="orders")

    
# Database setup
engine = create_engine("sqlite:///users_database.db")
Session = sessionmaker(bind=engine)

# Create tables
Base.metadata.create_all(engine)

# User Manager
class UserManager:
    def __init__(self, session: Session):
        self.session = session
        
    def is_email_unique(self, email, user_id=None):
        """
        Check if an email is unique in the database.
        Optionally exclude a specific user ID (used for updates).
        """
        query = self.session.query(User).filter(User.email == email)
        if user_id:
            query = query.filter(User.id != user_id)
        return query.first() is None
    
    def is_email_unique(self, email, user_id=None):
        """
        Check if an email is unique in the database.
        Optionally exclude a specific user ID (used for updates).
        """
        query = self.session.query(User).filter(User.email == email)
        if user_id:
            query = query.filter(User.id != user_id)
        return query.first() is None

    def create_user(self, name, email, user_type: UserType, request_num: int, period_days: int = 0):
        """Create a new user."""
        try:
            if not self.is_email_unique(email):
                print("Error: Email already exists.")
                return "Email already exists."

            # Restriction: if user_type is recurrent, period_days must be a positive integer
            if user_type == UserType.Recurrent and (period_days is None or period_days <= 0):
                print("Error: For recurrent users, period_days must be a positive integer.")
                return "For recurrent users, period_days must be a positive integer."

            user = User(
                name=name.replace(" ", "_"),
                email=email,
                user_type=user_type,
                request_num=request_num,
                period_days=period_days
            )
            self.session.add(user)
            self.session.commit()
            print(f"User {name} created with ID {user.id}.")
            return user
        except Exception as e:
            self.session.rollback()
            print(f"Error creating user: {e}")
            return f"Error creating user: {e}"

            
    def get_user_by_id(self, user_id):
        """Retrieve a user by their ID."""
        return self.session.query(User).filter_by(id=user_id).first()

    def get_all_users(self):
        """Retrieve all users."""
        return self.session.query(User).all()

    def update_user(self, user_id, **kwargs):
        """Update user information. Pass fields as keyword arguments."""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                print("Error: User not found.")
                return "User not found."

            # Check if email is being updated and ensure it's unique
            if "email" in kwargs and not self.is_email_unique(kwargs["email"], user_id):
                print("Error: Email already exists.")
                return "Error updating user: Email already exists."

            for key, value in kwargs.items():
                setattr(user, key, value)
            self.session.commit()
            print(f"User {user_id} updated.")
            return user
        
        except Exception as e:
            self.session.rollback()
            print(f"An error occurred while updating user {user_id}: {e}")
            return f"Error updating user: {e}"

    def delete_user(self, user_id):
        """Delete a user by their ID."""
        user = self.get_user_by_id(user_id)
        if user:
            self.session.delete(user)
            self.session.commit()
            print(f"User {user_id} deleted.")
        else:
            print("User not found.")

    def request_posts(self, user_id, posts_df: pd.DataFrame):
        """Request posts for a specific user."""
        return OrderManager(self.session).handle_post_request(user_id, posts_df)
    
    def export_to_csv(self, file_path="users_export.csv"):
        """Export all users to a CSV file."""
        users = self.get_all_users()
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["id", "name", "email", "user_type", "request_num", "period_days", "last_request_date", "user_dir"])
            for user in users:
                writer.writerow([
                    user.id, 
                    user.name, 
                    user.email, 
                    user.user_type.value, 
                    user.request_num, 
                    user.period_days, 
                    user.last_request_date, 
                    user.user_dir
                ])
        print(f"Users exported to {file_path}")
        
        
# Order Manager
class OrderManager:
    def __init__(self, session: Session, posts_df: pd.DataFrame):
        self.session = session
        self.posts_df = posts_df
        self._initialize_recurrent_user_orders()

    def _initialize_recurrent_user_orders(self):
        """Automatically complete or create orders for recurrent users if their period has elapsed."""
        rec_users = self.session.query(User).filter_by(user_type=UserType.Recurrent).all()

        for user in rec_users:
            if user.last_request_date:
                # Calculate next allowed request date based on period days
                next_allowed_date = user.last_request_date + timedelta(days=user.period_days)
                
                # Check if enough time has passed to create a new order
                if next_allowed_date <= datetime.now():
                    # Look for any incomplete order for this user
                    order = self.session.query(Order).filter(
                        Order.user_id == user.id,
                        Order.order_status == OrderStatus.Incomplete
                    ).first()

                    if order:
                        # If an incomplete order exists, complete it
                        self.handle_order(order.order_id, self.posts_df)
                    else:
                        # If no incomplete order, create a new one
                        new_order = self.create_order(user.id, self.posts_df, num_retrieved_posts=0)
                        user.last_request_date = datetime.now()  # Update last request date
                        print(f"New order automatically created for recurrent user {user.id}.")
                        self.session.commit()


    def create_order(self, user_id, df, num_retrieved_posts=0, city_names=None, sector_names=None):
        """
        Create a new order for a user and associate it with cities and sectors.
        """
        user = UserManager(self.session).get_user_by_id(user_id)
        if not user:
            print("User not found.")
            return
        
        if num_retrieved_posts >= len(df):
            print("The user has consumed all posts in the database.")
            return
        
        # Determine remaining posts
        remaining_posts = user.request_num - num_retrieved_posts
        
        # Create a new order
        order = Order(
            user_id=user_id,
            retrieved_posts=num_retrieved_posts,
            remaining_posts=remaining_posts,
            order_status=OrderStatus.Incomplete if remaining_posts > 0 else OrderStatus.Complete
        )
        
        # Associate cities
        if city_names:
            for city_name in city_names:
                city = self.session.query(City).filter_by(name=city_name).first()
                if not city:
                    # Create the city if it doesn't exist
                    city = City(name=city_name)
                    self.session.add(city)
                order.cities.append(city)
        
        # Associate sectors
        if sector_names:
            for sector_name in sector_names:
                sector = self.session.query(Sector).filter_by(name=sector_name).first()
                if not sector:
                    # Create the sector if it doesn't exist
                    sector = Sector(name=sector_name)
                    self.session.add(sector)
                order.sectors.append(sector)
        
        # Save the order
        self.session.add(order)
        self.session.commit()
        print(f"Order {order.order_id} created for User {user_id}.")
        return order


    def get_order_by_id(self, order_id):
        """Retrieve an order by its ID."""
        return self.session.query(Order).filter_by(order_id=order_id).first()

    def get_all_orders(self):
        """Retrieve all orders."""
        return self.session.query(Order).all()
    
    def update_order(self, order_id, city_names=None, sector_names=None, **kwargs):
        """
        Update order information, including cities and sectors. Pass fields as keyword arguments.
        """
        order = self.get_order_by_id(order_id)
        if order:
            # Update basic fields
            for key, value in kwargs.items():
                setattr(order, key, value)
            
            # Update cities
            if city_names is not None:
                # Clear existing cities
                order.cities = []
                for city_name in city_names:
                    city = self.session.query(City).filter_by(name=city_name).first()
                    if not city:
                        city = City(name=city_name)
                        self.session.add(city)
                    order.cities.append(city)
            
            # Update sectors
            if sector_names is not None:
                # Clear existing sectors
                order.sectors = []
                for sector_name in sector_names:
                    sector = self.session.query(Sector).filter_by(name=sector_name).first()
                    if not sector:
                        sector = Sector(name=sector_name)
                        self.session.add(sector)
                    order.sectors.append(sector)
            
            # Recalculate remaining posts and update order status if needed
            if 'retrieved_posts' in kwargs:
                order.remaining_posts = order.user.request_num - order.retrieved_posts
                order.order_status = OrderStatus.Complete if order.remaining_posts <= 0 else OrderStatus.Incomplete

            self.session.commit()
            print(f"Order {order_id} updated.")
        else:
            print("Order not found.")


    def delete_order(self, order_id):
        """Delete an order by its ID."""
        order = self.get_order_by_id(order_id)
        if order:
            self.session.delete(order)
            self.session.commit()
            print(f"Order {order_id} deleted.")
        else:
            print("Order not found.")
    
    
    def handle_order(self, order_id: int, posts_df: pd.DataFrame):
        """Handle an order using only the order ID."""
        order = self.get_order_by_id(order_id)
        if not order:
            warning = f"No order found with ID {order_id}."
            print(warning)
            return warning

        user = self.get_user_by_id(order.user_id)
        if not user:
            warning = f"No user associated with order ID {order_id}."
            print(warning)
            return warning

        # Fetch user-requested cities and sectors
        requested_cities = [city.name for city in order.cities]
        requested_sectors = [sector.name for sector in order.sectors]

        if not requested_cities and not requested_sectors:
            warning = f"Order {order_id} has no requested cities or sectors. Unable to handle."
            print(warning)
            return warning

        # Filter posts_df for matching cities or sectors
        filtered_posts = posts_df[
            posts_df["city"].apply(lambda post_cities: any(city in post_cities for city in requested_cities)) |
            posts_df["sectors"].apply(lambda post_sectors: any(sector in post_sectors for sector in requested_sectors))
        ]

        if filtered_posts.empty:
            warning = f"No matching posts found for order {order_id}."
            print(warning)
            return warning
        
        
        status_flag = None
        if user.user_type == UserType.SingleRequest:
            status_flag = self._handle_single_order_user(user, order, filtered_posts)
        else:
            status_flag = self._handle_recurrent_user_order(user, order, filtered_posts)
        
        user.last_request_date = datetime.now()
        
        return status_flag
        
    def _handle_single_order_user(self, user: User, order: Order, posts_df: pd.DataFrame):
        total_requested_posts = user.request_num
        current_retrieved_posts = order.retrieved_posts
        posts_needed = total_requested_posts - current_retrieved_posts
        available_posts = self.get_available_posts(posts_df, user)
        posts_to_retrieve_count = min(posts_needed, available_posts.shape[0])
        posts_to_retrieve = available_posts.head(posts_to_retrieve_count)

        file_name = f"{order.order_id}_{user.name}_{order.order_date.strftime('%Y-%m-%d')}.csv"
        file_path = f"{user.user_dir}/{file_name}"
        os.makedirs(user.user_dir, exist_ok=True)

        if os.path.exists(file_path):
            if not posts_to_retrieve.empty:
                posts_to_retrieve.to_csv(file_path, mode='a', header=False, index=False)
                print(f"Additional posts appended to {file_name}")
        else:
            posts_to_retrieve.to_csv(file_path, index=False)
            print(f"Posts saved to {file_name}")

        user.provided_posts.update(posts_to_retrieve['email'].tolist())
        order.retrieved_posts += posts_to_retrieve_count
        order.remaining_posts = total_requested_posts - order.retrieved_posts
        
        status_flag = None
        if order.remaining_posts <= 0:
            order.order_status = OrderStatus.Complete
            status_flag = f"Order {order.order_id} for User {user.id} marked as complete."
        else:
            order.order_status = OrderStatus.Incomplete
            status_flag = f"Order {order.order_id} for User {user.id} is still incomplete. {order.remaining_posts} posts remaining."
        print(status_flag)
        self.session.commit()
        return status_flag
        
    def _handle_recurrent_user_order(self, user: User, order:Order, posts_df: pd.DataFrame):
        # Check if enough time has passed since the last request
        status_flag = None
        if user.last_request_date:
            next_allowed_date = user.last_request_date + timedelta(days=user.period_days)
            if next_allowed_date > datetime.now():
                status_flag = f"User {user.id} cannot request posts yet. Wait until {next_allowed_date}."
                print(status_flag)
                return status_flag

        # Process as single order if waiting period has passed
        self._handle_single_order_user(user, order, posts_df)
        city_names = [city.name for city in order.cities]  # Extract city names
        sector_names = [sector.name for sector in order.sectors]  # Extract sector names

        self.create_order(
            user.id, 
            posts_df, 
            num_retrieved_posts=0, 
            city_names=city_names, 
            sector_names=sector_names  # Pass names instead of entities
            )
        print(f"New order created for User {user.id} as recurrent order cycle continues.")
        user.last_request_date = datetime.now()
        self.session.commit()
        status_flag = f"User {user.id} has request {order.retrieved_posts} posts"
        return status_flag

        
    def get_available_posts(self, posts_df: pd.DataFrame, user):
        """Get posts that the user hasn't retrieved yet."""
        # Filter out posts that the user has already received
        return posts_df[~posts_df['email'].isin(user.provided_posts)]

    def get_user_by_id(self, user_id):
        """Retrieve a user by their ID."""
        return self.session.query(User).filter_by(id=user_id).first()

    def export_to_csv(self, file_path="orders_export.csv"):
        """Export all orders to a CSV file."""
        orders = self.get_all_orders()
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["order_id", "user_id", "order_date", "retrieved_posts", "remaining_posts", "order_status"])
            for order in orders:
                writer.writerow([
                    order.order_id, 
                    order.user_id, 
                    order.order_date, 
                    order.retrieved_posts, 
                    order.remaining_posts, 
                    order.order_status.value
                ])
        print(f"Orders exported to {file_path}")
        

# Database setup
engine = create_engine("sqlite:///users_database.db")
Session = sessionmaker(bind=engine)
session = Session()

