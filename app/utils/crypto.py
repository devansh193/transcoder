import base64
import time
import uuid
from typing import Dict, Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa


class SecureKeyGenerator:
    def __init__(self, key_size: int = 4096, public_exponent: int = 65537):
        self.key_size = key_size
        self.public_exponent = public_exponent

    def generate_key_pair(self) -> Dict[str, str]:
        try:
            private_key = rsa.generate_private_key(
                public_exponent=self.public_exponent, key_size=self.key_size
            )
            private_bytes = private_key.private_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )

            public_key = private_key.public_key()
            public_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            return {
                "key_id": str(uuid.uuid4()),
                "private_key": base64.b64encode(private_bytes).decode("utf-8"),
                "public_key": base64.b64encode(public_bytes).decode("utf-8"),
                "key_size": self.key_size,
                "created_at": int(time.time()),
                "status": "active",
                "fingerprint": self._generate_key_fingerprint(public_bytes),
            }
        except Exception as e:
            raise ValueError(f"Key generation failed: {str(e)}")

    def rotate_api_key(
        self, existing_key: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        new_key_pair = self.generate_key_pair()

        if existing_key:
            new_key_pair.update(
                {
                    "previous_key_id": existing_key.get("key_id"),
                    "rotated_at": int(time.time()),
                    "rotation_reason": "Scheduled rotation",
                }
            )

        return new_key_pair

    @staticmethod
    def sign_data(private_key_base64: str, data: str) -> str:
        try:
            private_key = serialization.load_pem_private_key(
                base64.b64decode(private_key_base64("utf-8")), password=None
            )

            signature = private_key.sign(
                data.encode("utf-8"),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return base64.b64encode(signature).decode("utf-8")
        except Exception as e:
            raise ValueError(f"Signing failed: {str(e)}")

    @staticmethod
    def verify_signature(public_key_base64: str, data: str, signature: str) -> bool:
        try:
            public_key = serialization.load_der_public_key(
                base64.b64decode(public_key_base64.encode("utf-8"))
            )

            public_key.verify(
                base64.b64decode(signature.encode("utf-8")),
                data.encode("utf-8"),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False

    def _generate_key_fingerprint(self, public_key: bytes) -> str:
        digest = hashes.Hash(hashes.SHA256())
        digest.update(public_key)
        return base64.b64encode(digest.finalize()).decode("utf-8")


def main():
    key_generator = SecureKeyGenerator(key_size=2048)

    initial_key = key_generator.generate_key_pair()
    print("Initial Key ID:", initial_key["key_id"])

    rotated_key = key_generator.rotate_api_key(existing_key=initial_key)
    print("Rotated Key ID:", rotated_key["key_id"])
    print("Previous Key ID:", rotated_key.get("previous_key_id"))

    test_data = "Secure Communication"
    signature = SecureKeyGenerator.sign_data(rotated_key["private_key"], test_data)

    is_valid = SecureKeyGenerator.verify_signature(
        rotated_key["public_key"], test_data, signature
    )

    print("Signature Valid:", is_valid)


if __name__ == "__main__":
    main()
