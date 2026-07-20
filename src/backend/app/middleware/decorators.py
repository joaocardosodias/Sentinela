from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt

def role_required(*allowed_roles):
    """
    Middleware genérico que verifica se o cargo do usuário está na lista permitida.
    Exemplo: @role_required('gestor_remoto', 'gestor_local')
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # Extraímos o cargo criptografado no token JWT
            claims = get_jwt()
            user_role = claims.get('role')
            
            # Checa se a pessoa tem permissão para entrar
            if user_role not in allowed_roles:
                return jsonify({
                    'message': 'Acesso negado. Você não tem permissão para entrar aqui.',
                    'seu_cargo': user_role,
                    'cargos_permitidos': allowed_roles
                }), 403
                
            return fn(*args, **kwargs)
        return decorator
    return wrapper

