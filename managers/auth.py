from datetime import datetime, timedelta

from decouple import config
from flask_httpauth import HTTPTokenAuth
from jwt import encode, decode, DecodeError
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError
from werkzeug.exceptions import BadRequest

from models.users import ComplainerModel, ApproverModel, AdminModel


class AuthManager:
    @staticmethod
    def encode_token(user):
        payload = {
            'exp': datetime.utcnow() + timedelta(days=2),
            'sub': user.id,
            'type': user.__class__.__name__
            }
        return encode(payload,
                      key=config('JWT_KEY'),
                      algorithm='HS256'
                      )

    @staticmethod
    def decode_token(token):
        try:
            payload = decode(token, key=config('JWT_KEY'), algorithms=['HS256'])
            return payload['sub'], payload['type']
        except ExpiredSignatureError:
            raise BadRequest('Expired Token')
        except InvalidSignatureError:
            raise BadRequest('Invalid Token')
        except DecodeError:
            raise BadRequest('Token Required')


auth = HTTPTokenAuth()

@auth.verify_token
def verify_token(token):
    user_id, role = AuthManager.decode_token(token)
    return eval(f"{role}.query.filter_by(id=user_id).first()")


