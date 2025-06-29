from flask import Blueprint, request, jsonify
from datetime import datetime, date
from sqlalchemy import or_, and_, func
from decimal import Decimal

from src.models.user import db, Student
from src.models.financial import FeeStructure, Invoice, Payment, FinancialAccount, FinancialTransaction, Expense
from src.routes.auth import token_required, role_required

financial_bp = Blueprint('financial', __name__)

# Fee Structure Management
@financial_bp.route('/fee-structures', methods=['GET'])
@token_required
@role_required(['admin', 'staff'])
def get_fee_structures():
    """Get list of fee structures"""
    try:
        school_id = request.args.get('school_id', type=int)
        year_id = request.args.get('year_id', type=int)
        fee_type = request.args.get('fee_type')
        
        query = FeeStructure.query
        
        if school_id:
            query = query.filter_by(school_id=school_id)
        
        if year_id:
            query = query.filter_by(year_id=year_id)
        
        if fee_type:
            query = query.filter_by(fee_type=fee_type)
        
        fee_structures = query.order_by(FeeStructure.created_at.desc()).all()
        
        return jsonify({
            'fee_structures': [fee.to_dict() for fee in fee_structures]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@financial_bp.route('/fee-structures', methods=['POST'])
@token_required
@role_required(['admin', 'staff'])
def create_fee_structure():
    """Create new fee structure"""
    try:
        data = request.get_json()
        
        required_fields = ['school_id', 'year_id', 'fee_name', 'amount', 'fee_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        fee_structure = FeeStructure(
            school_id=data['school_id'],
            year_id=data['year_id'],
            fee_name=data['fee_name'],
            amount=Decimal(str(data['amount'])),
            fee_type=data['fee_type'],
            payment_schedule=data.get('payment_schedule'),
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data.get('due_date') else None,
            is_mandatory=data.get('is_mandatory', True)
        )
        
        if data.get('applicable_classes'):
            fee_structure.set_applicable_classes(data['applicable_classes'])
        
        db.session.add(fee_structure)
        db.session.commit()
        
        return jsonify({
            'message': 'Fee structure created successfully',
            'fee_structure': fee_structure.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@financial_bp.route('/fee-structures/<int:fee_id>', methods=['PUT'])
@token_required
@role_required(['admin', 'staff'])
def update_fee_structure(fee_id):
    """Update fee structure"""
    try:
        fee_structure = FeeStructure.query.get(fee_id)
        if not fee_structure:
            return jsonify({'error': 'Fee structure not found'}), 404
        
        data = request.get_json()
        
        if 'fee_name' in data:
            fee_structure.fee_name = data['fee_name']
        if 'amount' in data:
            fee_structure.amount = Decimal(str(data['amount']))
        if 'fee_type' in data:
            fee_structure.fee_type = data['fee_type']
        if 'payment_schedule' in data:
            fee_structure.payment_schedule = data['payment_schedule']
        if 'due_date' in data:
            fee_structure.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        if 'is_mandatory' in data:
            fee_structure.is_mandatory = data['is_mandatory']
        if 'applicable_classes' in data:
            fee_structure.set_applicable_classes(data['applicable_classes'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Fee structure updated successfully',
            'fee_structure': fee_structure.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Invoice Management
@financial_bp.route('/invoices', methods=['GET'])
@token_required
def get_invoices():
    """Get list of invoices"""
    try:
        current_user_role = request.current_user.get('role_type')
        current_user_id = request.current_user.get('user_id')
        
        # Get query parameters
        student_id = request.args.get('student_id', type=int)
        status = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        query = Invoice.query
        
        # Apply role-based filtering
        if current_user_role == 'student':
            student = Student.query.filter_by(user_id=current_user_id).first()
            if not student:
                return jsonify({'error': 'Student profile not found'}), 404
            query = query.filter_by(student_id=student.student_id)
        elif current_user_role == 'parent':
            # Parents can see invoices for their children
            # This would require a parent-child relationship table
            # For now, we'll restrict access
            return jsonify({'error': 'Access denied'}), 403
        elif current_user_role not in ['admin', 'staff']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Apply filters
        if student_id and current_user_role in ['admin', 'staff']:
            query = query.filter_by(student_id=student_id)
        
        if status:
            query = query.filter_by(status=status)
        
        # Execute query with pagination
        invoices = query.order_by(Invoice.issue_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        result = {
            'invoices': [],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': invoices.total,
                'pages': invoices.pages,
                'has_next': invoices.has_next,
                'has_prev': invoices.has_prev
            }
        }
        
        for invoice in invoices.items:
            invoice_data = invoice.to_dict()
            if current_user_role in ['admin', 'staff']:
                invoice_data['student'] = invoice.student.to_dict()
            invoice_data['fee_structure'] = invoice.fee_structure.to_dict()
            result['invoices'].append(invoice_data)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@financial_bp.route('/invoices', methods=['POST'])
@token_required
@role_required(['admin', 'staff'])
def create_invoice():
    """Create new invoice"""
    try:
        data = request.get_json()
        
        required_fields = ['student_id', 'fee_id', 'amount', 'due_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Generate invoice number
        invoice_count = Invoice.query.count() + 1
        invoice_number = f"INV{invoice_count:06d}"
        
        # Calculate total amount
        amount = Decimal(str(data['amount']))
        discount = Decimal(str(data.get('discount', 0)))
        total_amount = amount - discount
        
        invoice = Invoice(
            student_id=data['student_id'],
            fee_id=data['fee_id'],
            invoice_number=invoice_number,
            amount=amount,
            discount=discount,
            total_amount=total_amount,
            issue_date=datetime.strptime(data['issue_date'], '%Y-%m-%d').date() if data.get('issue_date') else date.today(),
            due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        )
        
        db.session.add(invoice)
        db.session.commit()
        
        return jsonify({
            'message': 'Invoice created successfully',
            'invoice': invoice.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@financial_bp.route('/invoices/<int:invoice_id>', methods=['GET'])
@token_required
def get_invoice(invoice_id):
    """Get specific invoice details"""
    try:
        current_user_role = request.current_user.get('role_type')
        current_user_id = request.current_user.get('user_id')
        
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        # Check permissions
        if current_user_role == 'student':
            student = Student.query.filter_by(user_id=current_user_id).first()
            if not student or invoice.student_id != student.student_id:
                return jsonify({'error': 'Access denied'}), 403
        elif current_user_role not in ['admin', 'staff']:
            return jsonify({'error': 'Access denied'}), 403
        
        invoice_data = invoice.to_dict()
        invoice_data['student'] = invoice.student.to_dict()
        invoice_data['fee_structure'] = invoice.fee_structure.to_dict()
        invoice_data['payments'] = [payment.to_dict() for payment in invoice.payments]
        
        return jsonify({'invoice': invoice_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Payment Management
@financial_bp.route('/payments', methods=['GET'])
@token_required
def get_payments():
    """Get list of payments"""
    try:
        current_user_role = request.current_user.get('role_type')
        current_user_id = request.current_user.get('user_id')
        
        # Get query parameters
        student_id = request.args.get('student_id', type=int)
        invoice_id = request.args.get('invoice_id', type=int)
        status = request.args.get('status')
        
        query = Payment.query
        
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
        
        if invoice_id:
            query = query.filter_by(invoice_id=invoice_id)
        
        if status:
            query = query.filter_by(status=status)
        
        payments = query.order_by(Payment.payment_date.desc()).all()
        
        result = []
        for payment in payments:
            payment_data = payment.to_dict()
            if current_user_role in ['admin', 'staff']:
                payment_data['student'] = payment.student.to_dict()
            payment_data['invoice'] = payment.invoice.to_dict()
            result.append(payment_data)
        
        return jsonify({'payments': result}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@financial_bp.route('/payments', methods=['POST'])
@token_required
def create_payment():
    """Create new payment"""
    try:
        current_user_role = request.current_user.get('role_type')
        current_user_id = request.current_user.get('user_id')
        
        data = request.get_json()
        
        required_fields = ['invoice_id', 'payment_method', 'amount']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Get invoice
        invoice = Invoice.query.get(data['invoice_id'])
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        # Check permissions
        if current_user_role == 'student':
            student = Student.query.filter_by(user_id=current_user_id).first()
            if not student or invoice.student_id != student.student_id:
                return jsonify({'error': 'Access denied'}), 403
        elif current_user_role not in ['admin', 'staff']:
            return jsonify({'error': 'Access denied'}), 403
        
        # Validate payment amount
        amount = Decimal(str(data['amount']))
        if amount <= 0:
            return jsonify({'error': 'Payment amount must be positive'}), 400
        
        # Check if payment exceeds outstanding balance
        outstanding_balance = Decimal(str(invoice.calculate_balance()))
        if amount > outstanding_balance:
            return jsonify({'error': 'Payment amount exceeds outstanding balance'}), 400
        
        payment = Payment(
            invoice_id=data['invoice_id'],
            student_id=invoice.student_id,
            payment_method=data['payment_method'],
            amount=amount,
            transaction_id=data.get('transaction_id'),
            status=data.get('status', 'Completed'),
            processed_by=current_user_id
        )
        
        if data.get('gateway_response'):
            payment.set_gateway_response(data['gateway_response'])
        
        db.session.add(payment)
        
        # Update invoice status if fully paid
        new_balance = outstanding_balance - amount
        if new_balance <= 0:
            invoice.status = 'Paid'
        elif invoice.status == 'Pending':
            invoice.status = 'Partial'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Payment recorded successfully',
            'payment': payment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Financial Reporting
@financial_bp.route('/reports/summary', methods=['GET'])
@token_required
@role_required(['admin', 'staff'])
def get_financial_summary():
    """Get financial summary report"""
    try:
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        school_id = request.args.get('school_id', type=int)
        
        # Build date filters
        date_filters = []
        if start_date:
            date_filters.append(Invoice.issue_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            date_filters.append(Invoice.issue_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        # Invoice summary
        invoice_query = db.session.query(
            func.count(Invoice.invoice_id).label('total_invoices'),
            func.sum(Invoice.total_amount).label('total_invoiced'),
            func.count(Invoice.invoice_id).filter(Invoice.status == 'Paid').label('paid_invoices'),
            func.count(Invoice.invoice_id).filter(Invoice.status == 'Pending').label('pending_invoices'),
            func.count(Invoice.invoice_id).filter(Invoice.status == 'Overdue').label('overdue_invoices')
        )
        
        if date_filters:
            invoice_query = invoice_query.filter(and_(*date_filters))
        
        invoice_summary = invoice_query.first()
        
        # Payment summary
        payment_query = db.session.query(
            func.count(Payment.payment_id).label('total_payments'),
            func.sum(Payment.amount).label('total_collected')
        ).filter(Payment.status == 'Completed')
        
        if date_filters:
            payment_query = payment_query.join(Invoice).filter(and_(*date_filters))
        
        payment_summary = payment_query.first()
        
        # Outstanding balance
        outstanding_query = db.session.query(
            func.sum(Invoice.total_amount - func.coalesce(
                db.session.query(func.sum(Payment.amount))
                .filter(Payment.invoice_id == Invoice.invoice_id)
                .filter(Payment.status == 'Completed')
                .scalar_subquery(), 0
            )).label('outstanding_balance')
        ).filter(Invoice.status.in_(['Pending', 'Partial', 'Overdue']))
        
        outstanding_balance = outstanding_query.scalar() or 0
        
        # Fee type breakdown
        fee_breakdown = db.session.query(
            FeeStructure.fee_type,
            func.sum(Invoice.total_amount).label('total_amount')
        ).join(Invoice).group_by(FeeStructure.fee_type).all()
        
        result = {
            'summary': {
                'total_invoices': invoice_summary.total_invoices or 0,
                'total_invoiced': float(invoice_summary.total_invoiced or 0),
                'paid_invoices': invoice_summary.paid_invoices or 0,
                'pending_invoices': invoice_summary.pending_invoices or 0,
                'overdue_invoices': invoice_summary.overdue_invoices or 0,
                'total_payments': payment_summary.total_payments or 0,
                'total_collected': float(payment_summary.total_collected or 0),
                'outstanding_balance': float(outstanding_balance)
            },
            'fee_type_breakdown': [
                {
                    'fee_type': breakdown.fee_type,
                    'total_amount': float(breakdown.total_amount)
                } for breakdown in fee_breakdown
            ]
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@financial_bp.route('/reports/outstanding', methods=['GET'])
@token_required
@role_required(['admin', 'staff'])
def get_outstanding_report():
    """Get outstanding payments report"""
    try:
        # Get invoices with outstanding balances
        outstanding_invoices = db.session.query(
            Invoice,
            (Invoice.total_amount - func.coalesce(
                db.session.query(func.sum(Payment.amount))
                .filter(Payment.invoice_id == Invoice.invoice_id)
                .filter(Payment.status == 'Completed')
                .scalar_subquery(), 0
            )).label('outstanding_amount')
        ).filter(Invoice.status.in_(['Pending', 'Partial', 'Overdue'])).all()
        
        result = []
        for invoice, outstanding_amount in outstanding_invoices:
            if outstanding_amount > 0:
                invoice_data = invoice.to_dict()
                invoice_data['student'] = invoice.student.to_dict()
                invoice_data['fee_structure'] = invoice.fee_structure.to_dict()
                invoice_data['outstanding_amount'] = float(outstanding_amount)
                
                # Calculate days overdue
                if invoice.due_date < date.today():
                    invoice_data['days_overdue'] = (date.today() - invoice.due_date).days
                else:
                    invoice_data['days_overdue'] = 0
                
                result.append(invoice_data)
        
        # Sort by days overdue (descending)
        result.sort(key=lambda x: x['days_overdue'], reverse=True)
        
        return jsonify({'outstanding_invoices': result}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Expense Management
@financial_bp.route('/expenses', methods=['GET'])
@token_required
@role_required(['admin', 'staff'])
def get_expenses():
    """Get list of expenses"""
    try:
        # Get query parameters
        category = request.args.get('category')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = Expense.query
        
        if category:
            query = query.filter_by(category=category)
        
        if start_date:
            query = query.filter(Expense.expense_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        
        if end_date:
            query = query.filter(Expense.expense_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        expenses = query.order_by(Expense.expense_date.desc()).all()
        
        return jsonify({
            'expenses': [expense.to_dict() for expense in expenses]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@financial_bp.route('/expenses', methods=['POST'])
@token_required
@role_required(['admin', 'staff'])
def create_expense():
    """Create new expense record"""
    try:
        data = request.get_json()
        
        required_fields = ['school_id', 'category', 'description', 'amount']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        expense = Expense(
            school_id=data['school_id'],
            category=data['category'],
            description=data['description'],
            amount=Decimal(str(data['amount'])),
            expense_date=datetime.strptime(data['expense_date'], '%Y-%m-%d').date() if data.get('expense_date') else date.today(),
            vendor=data.get('vendor'),
            receipt_number=data.get('receipt_number'),
            payment_method=data.get('payment_method'),
            approved_by=data.get('approved_by'),
            created_by=request.current_user['user_id']
        )
        
        db.session.add(expense)
        db.session.commit()
        
        return jsonify({
            'message': 'Expense recorded successfully',
            'expense': expense.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

