'''
Business: User registration and authentication API
Args: event - dict with httpMethod, body, queryStringParameters
      context - object with request_id, function_name attributes
Returns: HTTP response dict with user data or error
'''
import json
import os
import hashlib
import re
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, EmailStr, field_validator

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_db_connection():
    import psycopg2
    database_url = os.environ.get('DATABASE_URL')
    return psycopg2.connect(database_url)

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    method: str = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, X-User-Id',
                'Access-Control-Max-Age': '86400'
            },
            'body': ''
        }
    
    if method == 'POST':
        body_data = json.loads(event.get('body', '{}'))
        action = body_data.get('action')
        
        if action == 'register':
            register_req = RegisterRequest(**body_data)
            
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("SELECT id FROM users WHERE email = %s", (register_req.email,))
            if cur.fetchone():
                cur.close()
                conn.close()
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'isBase64Encoded': False,
                    'body': json.dumps({'error': 'Пользователь с таким email уже существует'})
                }
            
            password_hash = hash_password(register_req.password)
            cur.execute(
                "INSERT INTO users (email, password_hash, full_name) VALUES (%s, %s, %s) RETURNING id",
                (register_req.email, password_hash, register_req.full_name)
            )
            user_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'isBase64Encoded': False,
                'body': json.dumps({
                    'success': True,
                    'user': {
                        'id': user_id,
                        'email': register_req.email,
                        'full_name': register_req.full_name
                    }
                })
            }
        
        elif action == 'login':
            login_req = LoginRequest(**body_data)
            
            conn = get_db_connection()
            cur = conn.cursor()
            
            password_hash = hash_password(login_req.password)
            cur.execute(
                "SELECT id, email, full_name FROM users WHERE email = %s AND password_hash = %s",
                (login_req.email, password_hash)
            )
            user = cur.fetchone()
            cur.close()
            conn.close()
            
            if not user:
                return {
                    'statusCode': 401,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'isBase64Encoded': False,
                    'body': json.dumps({'error': 'Неверный email или пароль'})
                }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'isBase64Encoded': False,
                'body': json.dumps({
                    'success': True,
                    'user': {
                        'id': user[0],
                        'email': user[1],
                        'full_name': user[2]
                    }
                })
            }
    
    return {
        'statusCode': 405,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'isBase64Encoded': False,
        'body': json.dumps({'error': 'Method not allowed'})
    }
