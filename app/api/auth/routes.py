import base64
from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from ...services.database import mongo
from ...utils.conveter import serialize_cursor, serialize_document
import jwt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import bcrypt
import datetime as dt

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login', methods=['POST'])
def start_login():
    data = request.json
    find_user = mongo.db.users.find_one({"phone_number": data['phone_number']})

    if find_user is None:
        return jsonify({
            "result": "failed", 
            "message": "User with such data was not found."
        }), 404
    
    code = "111111"
    access_token = create_access_token(identity={'code': code, 'phone_number': data['phone_number']})

    return jsonify({
        "result": "success",
        "message": "You must pass verification, code = 111111. The following request must be sent to the address 'auth/verification_login/', the request body must contain: code='111111'. headers should contain the previously received token, like this: Authorization: 'Bearer $access_token'",
        "access_token": access_token
    }), 201

@auth_blueprint.route('/verification_login', methods=['POST'])
@jwt_required()
def verification_login():
    data = request.json
    token_data = get_jwt_identity()

    if data['code'] == token_data['code']:
        find_user = mongo.db.users.find_one({'phone_number': token_data['phone_number']})

        if find_user is None:
            return jsonify({
                "result": "failed", 
                "message": "User with such data was not found."
            }), 404
        else:
            access_token = create_access_token(identity={'_id': str(find_user['_id'])})
            return jsonify({
                "result": 'success',
                "user": serialize_document(find_user),
                "access_token": access_token
            }), 201
    else:
        return jsonify({
            "result": "failed",
            "message": "Invalid verification code entered."
        }), 401

@auth_blueprint.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    token_data = get_jwt_identity()
    find_user = mongo.db.users.find_one({"_id": ObjectId(token_data['_id'])})

    if find_user is None:
        return jsonify({
            "result": "failed", 
            "message": "User with such data was not found."
        }), 404
    
    access_token = create_access_token(identity={'_id': str(find_user['_id'])})
    return jsonify({
        "result": 'success',
        "user": serialize_document(find_user),
        "access_token": access_token
    }), 201


@auth_blueprint.route('/signup', methods=['POST'])
def signup():
    data = request.json

    email = data['email']
    phone_number = data['phone_number']
    password = data['password']
    repeat_password = data['repeat_password']

    # search by email
    find_user = mongo.db.users.find_one({"email": email})
    if find_user is not None:
        return jsonify({
            "result": "failed", 
            "message": "A user with this email already exists."
        }), 409
    
    # search by phone number 
    find_user = mongo.db.users.find_one({"phone_number": phone_number})
    if find_user is not None:
        return jsonify({
            "result": "failed",
            "message": "A user with this number already exists.",
        }), 409
    
    if password != repeat_password:
        return jsonify({
            "result": "failed", 
            "message": "Password mismatch."
        }), 401
    
    data.pop("repeat_password", None)
    data['password'] = bcrypt.hashpw(password.encode(encoding="utf-8") , bcrypt.gensalt())
    data['createdAt'] = dt.datetime.now()
    data['isDeleted'] = False

    insert_user = mongo.db.users.insert_one(data)
    if insert_user.inserted_id:
        find_user = mongo.db.users.find_one(insert_user.inserted_id)
        find_user.pop("password", None)

        access_token = create_access_token(identity={'_id': str(insert_user.inserted_id)})

        return jsonify({
            "result": "success",
            "message": "User successfully registered.",
            "data": {
                "user": serialize_document(find_user),
                "access_token": access_token
            }
        }), 201