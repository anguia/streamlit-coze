import hashlib

def hash_password(password):
    """生成密码哈希值"""
    return hashlib.sha256(password.encode()).hexdigest()