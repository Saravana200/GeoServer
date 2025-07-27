from passlib.context import CryptContext

hash_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=13 
)

class Hashing():

    @staticmethod
    def create_hash(password:str)->str:
        return hash_context.hash(password)
    
    @staticmethod
    def validate_hase(password:str, hash:str)->bool:
        return hash_context.verify(password,hash)
        