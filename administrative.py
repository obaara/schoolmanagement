from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
from sqlalchemy import or_, and_, func

from src.models.user import db, Student
from src.models.administrative import (
    Notification, Announcement, LibraryBook, BookTransaction, InventoryItem,
    TransportRoute, TransportVehicle, StudentTransport, Event
)
from src.routes.auth import token_required, role_required

administrative_bp = Blueprint('administrative', __name__)

# Notification Management
@administrative_bp.route('/notifications', methods=['GET'])
@token_required
def get_notifications():
    """Get notifications for current user"""
    try:
        current_user_id = request.current_user.get('user_id')
        
        # Get notifications where user is recipient
        notifications = Notification.query.filter(
            Notification.recipient_ids.contains(str(current_user_id))
        ).order_by(Notification.sent_at.desc()).limit(50).all()
        
        return jsonify({
            'notifications': [notification.to_dict() for notification in notifications]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@administrative_bp.route('/notifications', methods=['POST'])
@token_required
@role_required(['admin', 'teacher', 'staff'])
def create_notification():
    """Create new notification"""
    try:
        data = request.get_json()
        
        required_fields = ['recipient_ids', 'title', 'message', 'notification_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        notification = Notification(
            sender_id=request.current_user['user_id'],
            title=data['title'],
            message=data['message'],
            notification_type=data['notification_type'],
            is_urgent=data.get('is_urgent', False)
        )
        
        notification.set_recipient_ids(data['recipient_ids'])
        
        if data.get('delivery_channels'):
            notification.set_delivery_channels(data['delivery_channels'])
        
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'message': 'Notification created successfully',
            'notification': notification.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Announcement Management
@administrative_bp.route('/announcements', methods=['GET'])
@token_required
def get_announcements():
    """Get list of announcements"""
    try:
        current_user_role = request.current_user.get('role_type')
        
        # Get query parameters
        school_id = request.args.get('school_id', type=int)
        is_published = request.args.get('is_published', type=bool)
        
        query = Announcement.query
        
        if school_id:
            query = query.filter_by(school_id=school_id)
        
        # Non-admin users can only see published announcements
        if current_user_role not in ['admin', 'staff']:
            query = query.filter_by(is_published=True)
        elif is_published is not None:
            query = query.filter_by(is_published=is_published)
        
        # Filter by expiration date
        query = query.filter(
            or_(Announcement.expire_date.is_(None), 
                Announcement.expire_date >= datetime.utcnow())
        )
        
        announcements = query.order_by(Announcement.publish_date.desc()).all()
        
        return jsonify({
            'announcements': [announcement.to_dict() for announcement in announcements]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@administrative_bp.route('/announcements', methods=['POST'])
@token_required
@role_required(['admin', 'teacher', 'staff'])
def create_announcement():
    """Create new announcement"""
    try:
        data = request.get_json()
        
        required_fields = ['school_id', 'title', 'content']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        announcement = Announcement(
            author_id=request.current_user['user_id'],
            school_id=data['school_id'],
            title=data['title'],
            content=data['content'],
            publish_date=datetime.strptime(data['publish_date'], '%Y-%m-%d %H:%M:%S') if data.get('publish_date') else datetime.utcnow(),
            expire_date=datetime.strptime(data['expire_date'], '%Y-%m-%d %H:%M:%S') if data.get('expire_date') else None,
            is_published=data.get('is_published', False)
        )
        
        if data.get('target_audience'):
            announcement.set_target_audience(data['target_audience'])
        
        if data.get('attachments'):
            announcement.set_attachments(data['attachments'])
        
        db.session.add(announcement)
        db.session.commit()
        
        return jsonify({
            'message': 'Announcement created successfully',
            'announcement': announcement.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Library Management
@administrative_bp.route('/library/books', methods=['GET'])
@token_required
def get_library_books():
    """Get list of library books"""
    try:
        # Get query parameters
        search = request.args.get('search', '')
        category = request.args.get('category')
        available_only = request.args.get('available_only', type=bool)
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        query = LibraryBook.query.filter_by(is_active=True)
        
        # Apply filters
        if search:
            query = query.filter(or_(
                LibraryBook.title.contains(search),
                LibraryBook.author.contains(search),
                LibraryBook.isbn.contains(search)
            ))
        
        if category:
            query = query.filter_by(category=category)
        
        if available_only:
            query = query.filter(LibraryBook.available_copies > 0)
        
        # Execute query with pagination
        books = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        result = {
            'books': [book.to_dict() for book in books.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': books.total,
                'pages': books.pages,
                'has_next': books.has_next,
                'has_prev': books.has_prev
            }
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@administrative_bp.route('/library/books', methods=['POST'])
@token_required
@role_required(['admin', 'staff'])
def add_library_book():
    """Add new book to library"""
    try:
        data = request.get_json()
        
        required_fields = ['school_id', 'title', 'author']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        book = LibraryBook(
            school_id=data['school_id'],
            isbn=data.get('isbn'),
            title=data['title'],
            author=data['author'],
            publisher=data.get('publisher'),
            publication_year=data.get('publication_year'),
            category=data.get('category'),
            total_copies=data.get('total_copies', 1),
            available_copies=data.get('total_copies', 1),
            price=data.get('price')
        )
        
        db.session.add(book)
        db.session.commit()
        
        return jsonify({
            'message': 'Book added successfully',
            'book': book.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@administrative_bp.route('/library/transactions', methods=['GET'])
@token_required
def get_book_transactions():
    """Get library book transactions"""
    try:
        current_user_role = request.current_user.get('role_type')
        current_user_id = request.current_user.get('user_id')
        
        # Get query parameters
        student_id = request.args.get('student_id', type=int)
        book_id = request.args.get('book_id', type=int)
        status = request.args.get('status')
        
        query = BookTransaction.query
        
        # Apply role-based filtering
        if current_user_role == 'student':
            student = Student.query.filter_by(user_id=current_user_id).first()
            if not student:
                return jsonify({'error': 'Student profile not found'}), 404
            query = query.filter_by(student_id=student.student_id)
        elif current_user_role not in ['admin', 'staff']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Apply filters
        if student_id and current_user_role in ['admin', 'staff']:
            query = query.filter_by(student_id=student_id)
        
        if book_id:
            query = query.filter_by(book_id=book_id)
        
        if status:
            query = query.filter_by(status=status)
        
        transactions = query.order_by(BookTransaction.issue_date.desc()).all()
        
        result = []
        for transaction in transactions:
            transaction_data = transaction.to_dict()
            transaction_data['book'] = transaction.book.to_dict()
            if current_user_role in ['admin', 'staff']:
                transaction_data['student'] = transaction.student.to_dict()
            result.append(transaction_data)
        
        return jsonify({'transactions': result}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@administrative_bp.route('/library/issue-book', methods=['POST'])
@token_required
@role_required(['admin', 'staff'])
def issue_book():
    """Issue book to student"""
    try:
        data = request.get_json()
        
        required_fields = ['book_id', 'student_id', 'due_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if book is available
        book = LibraryBook.query.get(data['book_id'])
        if not book:
            return jsonify({'error': 'Book not found'}), 404
        
        if book.available_copies <= 0:
            return jsonify({'error': 'Book not available'}), 400
        
        # Check if student has any overdue books
        overdue_books = BookTransaction.query.filter_by(
            student_id=data['student_id'], status='Issued'
        ).filter(BookTransaction.due_date < date.today()).count()
        
        if overdue_books > 0:
            return jsonify({'error': 'Student has overdue books'}), 400
        
        # Create transaction
        transaction = BookTransaction(
            book_id=data['book_id'],
            student_id=data['student_id'],
            issue_date=date.today(),
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date(),
            status='Issued',
            issued_by=request.current_user['user_id']
        )
        
        # Update book availability
        book.available_copies -= 1
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'Book issued successfully',
            'transaction': transaction.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@administrative_bp.route('/library/return-book/<int:transaction_id>', methods=['POST'])
@token_required
@role_required(['admin', 'staff'])
def return_book(transaction_id):
    """Return book"""
    try:
        transaction = BookTransaction.query.get(transaction_id)
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        if transaction.status != 'Issued':
            return jsonify({'error': 'Book already returned'}), 400
        
        data = request.get_json() or {}
        
        # Calculate fine if overdue
        fine_amount = 0
        if transaction.due_date < date.today():
            days_overdue = (date.today() - transaction.due_date).days
            fine_per_day = 1.0  # $1 per day fine
            fine_amount = days_overdue * fine_per_day
        
        # Update transaction
        transaction.return_date = date.today()
        transaction.fine_amount = fine_amount
        transaction.status = 'Returned'
        transaction.returned_to = request.current_user['user_id']
        
        # Update book availability
        book = transaction.book
        book.available_copies += 1
        
        db.session.commit()
        
        return jsonify({
            'message': 'Book returned successfully',
            'transaction': transaction.to_dict(),
            'fine_amount': fine_amount
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Inventory Management
@administrative_bp.route('/inventory/items', methods=['GET'])
@token_required
@role_required(['admin', 'staff'])
def get_inventory_items():
    """Get list of inventory items"""
    try:
        # Get query parameters
        category = request.args.get('category')
        search = request.args.get('search', '')
        
        query = InventoryItem.query.filter_by(is_active=True)
        
        if category:
            query = query.filter_by(category=category)
        
        if search:
            query = query.filter(InventoryItem.item_name.contains(search))
        
        items = query.order_by(InventoryItem.item_name).all()
        
        return jsonify({
            'items': [item.to_dict() for item in items]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@administrative_bp.route('/inventory/items', methods=['POST'])
@token_required
@role_required(['admin', 'staff'])
def add_inventory_item():
    """Add new inventory item"""
    try:
        data = request.get_json()
        
        required_fields = ['school_id', 'item_name', 'category']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        item = InventoryItem(
            school_id=data['school_id'],
            item_name=data['item_name'],
            category=data['category'],
            description=data.get('description'),
            quantity=data.get('quantity', 0),
            unit_price=data.get('unit_price'),
            supplier=data.get('supplier'),
            purchase_date=datetime.strptime(data['purchase_date'], '%Y-%m-%d').date() if data.get('purchase_date') else None,
            condition=data.get('condition', 'New')
        )
        
        db.session.add(item)
        db.session.commit()
        
        return jsonify({
            'message': 'Inventory item added successfully',
            'item': item.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Transport Management
@administrative_bp.route('/transport/routes', methods=['GET'])
@token_required
def get_transport_routes():
    """Get list of transport routes"""
    try:
        school_id = request.args.get('school_id', type=int)
        
        query = TransportRoute.query.filter_by(is_active=True)
        if school_id:
            query = query.filter_by(school_id=school_id)
        
        routes = query.all()
        
        return jsonify({
            'routes': [route.to_dict() for route in routes]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@administrative_bp.route('/transport/routes', methods=['POST'])
@token_required
@role_required(['admin', 'staff'])
def create_transport_route():
    """Create new transport route"""
    try:
        data = request.get_json()
        
        required_fields = ['school_id', 'route_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        route = TransportRoute(
            school_id=data['school_id'],
            route_name=data['route_name'],
            route_description=data.get('route_description'),
            distance_km=data.get('distance_km'),
            estimated_time=data.get('estimated_time')
        )
        
        if data.get('stops'):
            route.set_stops(data['stops'])
        
        db.session.add(route)
        db.session.commit()
        
        return jsonify({
            'message': 'Transport route created successfully',
            'route': route.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@administrative_bp.route('/transport/vehicles', methods=['GET'])
@token_required
@role_required(['admin', 'staff'])
def get_transport_vehicles():
    """Get list of transport vehicles"""
    try:
        route_id = request.args.get('route_id', type=int)
        
        query = TransportVehicle.query.filter_by(is_active=True)
        if route_id:
            query = query.filter_by(route_id=route_id)
        
        vehicles = query.all()
        
        return jsonify({
            'vehicles': [vehicle.to_dict() for vehicle in vehicles]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@administrative_bp.route('/transport/vehicles', methods=['POST'])
@token_required
@role_required(['admin', 'staff'])
def add_transport_vehicle():
    """Add new transport vehicle"""
    try:
        data = request.get_json()
        
        required_fields = ['school_id', 'vehicle_number', 'vehicle_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if vehicle number already exists
        existing_vehicle = TransportVehicle.query.filter_by(
            vehicle_number=data['vehicle_number']
        ).first()
        if existing_vehicle:
            return jsonify({'error': 'Vehicle number already exists'}), 409
        
        vehicle = TransportVehicle(
            school_id=data['school_id'],
            route_id=data.get('route_id'),
            vehicle_number=data['vehicle_number'],
            vehicle_type=data['vehicle_type'],
            capacity=data.get('capacity'),
            driver_name=data.get('driver_name'),
            driver_phone=data.get('driver_phone'),
            driver_license=data.get('driver_license')
        )
        
        if data.get('insurance_details'):
            vehicle.set_insurance_details(data['insurance_details'])
        
        if data.get('maintenance_schedule'):
            vehicle.set_maintenance_schedule(data['maintenance_schedule'])
        
        db.session.add(vehicle)
        db.session.commit()
        
        return jsonify({
            'message': 'Transport vehicle added successfully',
            'vehicle': vehicle.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Event Management
@administrative_bp.route('/events', methods=['GET'])
@token_required
def get_events():
    """Get list of events"""
    try:
        # Get query parameters
        school_id = request.args.get('school_id', type=int)
        event_type = request.args.get('event_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = Event.query
        
        if school_id:
            query = query.filter_by(school_id=school_id)
        
        if event_type:
            query = query.filter_by(event_type=event_type)
        
        if start_date:
            query = query.filter(Event.start_date >= datetime.strptime(start_date, '%Y-%m-%d'))
        
        if end_date:
            query = query.filter(Event.start_date <= datetime.strptime(end_date, '%Y-%m-%d'))
        
        # Non-admin users can only see public events
        current_user_role = request.current_user.get('role_type')
        if current_user_role not in ['admin', 'staff']:
            query = query.filter_by(is_public=True)
        
        events = query.order_by(Event.start_date).all()
        
        return jsonify({
            'events': [event.to_dict() for event in events]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@administrative_bp.route('/events', methods=['POST'])
@token_required
@role_required(['admin', 'staff', 'teacher'])
def create_event():
    """Create new event"""
    try:
        data = request.get_json()
        
        required_fields = ['school_id', 'title', 'start_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        event = Event(
            school_id=data['school_id'],
            title=data['title'],
            description=data.get('description'),
            event_type=data.get('event_type'),
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d %H:%M:%S'),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d %H:%M:%S') if data.get('end_date') else None,
            location=data.get('location'),
            organizer_id=request.current_user['user_id'],
            is_public=data.get('is_public', True)
        )
        
        if data.get('participants'):
            event.set_participants(data['participants'])
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify({
            'message': 'Event created successfully',
            'event': event.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

