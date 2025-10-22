'''
Business: User registration and authentication API
Args: event - dict with httpMethod, body, queryStringParameters
      context - object with request_id, function_name attributes
Returns: HTTP response dict with user data or error
'''
import json
import os
import hashlib
import secrets
import re
from datetime import datetime, timedelta
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

class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None

class ResetPasswordRequest(BaseModel):
    email: EmailStr

class ConfirmResetRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

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
        
        elif action == 'update_profile':
            update_req = UpdateProfileRequest(**body_data)
            user_id = body_data.get('user_id')
            
            if not user_id:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'isBase64Encoded': False,
                    'body': json.dumps({'error': 'user_id обязателен'})
                }
            
            conn = get_db_connection()
            cur = conn.cursor()
            
            updates = []
            values = []
            
            if update_req.full_name:
                updates.append('full_name = %s')
                values.append(update_req.full_name)
            if update_req.phone:
                updates.append('phone = %s')
                values.append(update_req.phone)
            if update_req.bio:
                updates.append('bio = %s')
                values.append(update_req.bio)
            
            if updates:
                updates.append('updated_at = CURRENT_TIMESTAMP')
                values.append(user_id)
                query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s RETURNING id, email, full_name, phone, bio"
                cur.execute(query, values)
                user = cur.fetchone()
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
                            'id': user[0],
                            'email': user[1],
                            'full_name': user[2],
                            'phone': user[3],
                            'bio': user[4]
                        }
                    })
                }
            
            cur.close()
            conn.close()
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'isBase64Encoded': False,
                'body': json.dumps({'error': 'Нет данных для обновления'})
            }
        
        elif action == 'reset_password':
            reset_req = ResetPasswordRequest(**body_data)
            
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("SELECT id FROM users WHERE email = %s", (reset_req.email,))
            user = cur.fetchone()
            
            if not user:
                cur.close()
                conn.close()
                return {
                    'statusCode': 404,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'isBase64Encoded': False,
                    'body': json.dumps({'error': 'Пользователь не найден'})
                }
            
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=1)
            
            cur.execute(
                "INSERT INTO password_reset_tokens (user_id, token, expires_at) VALUES (%s, %s, %s)",
                (user[0], token, expires_at)
            )
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
                    'token': token,
                    'message': 'Токен для сброса пароля создан'
                })
            }
        
        elif action == 'confirm_reset':
            confirm_req = ConfirmResetRequest(**body_data)
            
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute(
                "SELECT user_id, expires_at, used FROM password_reset_tokens WHERE token = %s",
                (confirm_req.token,)
            )
            token_data = cur.fetchone()
            
            if not token_data:
                cur.close()
                conn.close()
                return {
                    'statusCode': 404,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'isBase64Encoded': False,
                    'body': json.dumps({'error': 'Неверный токен'})
                }
            
            if token_data[2]:
                cur.close()
                conn.close()
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'isBase64Encoded': False,
                    'body': json.dumps({'error': 'Токен уже использован'})
                }
            
            if datetime.now() > token_data[1]:
                cur.close()
                conn.close()
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'isBase64Encoded': False,
                    'body': json.dumps({'error': 'Токен истёк'})
                }
            
            new_password_hash = hash_password(confirm_req.new_password)
            cur.execute(
                "UPDATE users SET password_hash = %s WHERE id = %s",
                (new_password_hash, token_data[0])
            )
            cur.execute(
                "UPDATE password_reset_tokens SET used = TRUE WHERE token = %s",
                (confirm_req.token,)
            )
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
                    'message': 'Пароль успешно изменён'
                })
            }
        
        elif action == 'login':
            login_req = LoginRequest(**body_data)
            
            conn = get_db_connection()
            cur = conn.cursor()
            
            password_hash = hash_password(login_req.password)
            cur.execute(
                "SELECT id, email, full_name, phone, bio FROM users WHERE email = %s AND password_hash = %s",
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
                        'full_name': user[2],
                        'phone': user[3],
                        'bio': user[4]
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