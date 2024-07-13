import base64
from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
from ...services.database import mongo
from ...utils.conveter import serialize_cursor, serialize_document
import jwt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

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
