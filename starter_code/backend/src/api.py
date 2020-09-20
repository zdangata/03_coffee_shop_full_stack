#Code for API endpoints were taken and adapted from lessons in the (https://classroom.udacity.com/nanodegrees/nd0044-ent/parts/573bef13-96dd-4f0f-9d47-afdd5f22ebc5) API Development and Documentation part of the course
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth, get_token_auth_header

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks')
def drinks():
    drinks = Drink.query.all()
    formatted_drinks = [drink.short() for drink in drinks]
    # returns a 404 error if there are no drinks in the database e.g. if all drink have been deleted
    if (len(drinks) == 0):
        print('There are currently no drinks saved here')

    return jsonify({
        'success': True,
        'drinks': formatted_drinks
    }), 200

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def drinks_detail(payload):
    drinks = Drink.query.all()
    formatted_drinks = [drink.long() for drink in drinks]

    if (len(drinks) == 0):
        print('There are currently no drinks saved here')

    token = get_token_auth_header()
    print(token)
    return jsonify({
        'success': True,
        'drinks':formatted_drinks
    }), 200

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    body = request.get_json()

    title = body.get('title', None)
    recipe = body.get('recipe', None)

    if body is None:
        abort(404)
        
    try:
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()
        #formatted_drinks = [drink.long() for drink in drinks]
        
        return jsonify({
            'success': True,
            'drinks': drink.long()
        }), 200
        
    except:
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):

    body = request.get_json()

    title = body.get('title', None)
    recipe = body.get('recipe', None)
    #recipe = json.dumps(recipe)

    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if drink is None:
                abort(404)

    try:
        if title:
            #drink = Drink(title=title)
            #drink.title = str(body.get('title'))
            #drink = Drink(title=title, recipe=json.dumps(recipe))
            drink.title = title

        if recipe:
            #drink = Drink(recipe=json.dumps(recipe))
            drink.recipe = json.dumps(recipe)

        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200

    except:
        abort(400)
'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)

        return jsonify({
            'success': True,
            'delete': drink_id
        }), 200
    except:
        abort(422)

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
                "success": False, 
                "error": 404,
                "message": "resource not found"
                }), 404



'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(401)
def Auth_error(error):
    return jsonify({
                "success": False, 
                "error": 401,
                "message": "resource not found"
                }), 401


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
                "success": False, 
                "error": 400,
                "message": "bad request"
                }), 400