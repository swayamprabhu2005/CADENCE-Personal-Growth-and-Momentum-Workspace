import base64
import hashlib
import logging
import os
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import settings


logger = logging.getLogger(__name__)

ENCRYPTION_PREFIX = "enc:v1:"


def _derive_key(key_input: str) -> bytes:
    """
    Derive a 32-byte (256-bit) key from:
    - 64-character hexadecimal key
    - 44-character base64 key
    - arbitrary passphrase using SHA-256
    """

    if not key_input:
        key_input = (
            "ai-goal-journal-default-secret-dev-key-change-in-prod"
        )

    key_input = key_input.strip()
    key_bytes = key_input.encode("utf-8")

    # 64-character hexadecimal key
    if len(key_bytes) == 64:
        try:
            return bytes.fromhex(key_input)
        except ValueError:
            pass

    # 44-character base64 key
    if len(key_bytes) == 44:
        try:
            decoded = base64.b64decode(key_bytes)
            if len(decoded) == 32:
                return decoded
        except Exception:
            pass

    # Fallback: derive a 32-byte key using SHA-256
    return hashlib.sha256(key_bytes).digest()


class FieldEncryptionService:
    """
    Field-level encryption using AES-256-GCM.

    Used for sensitive data such as:
    - Journal entries
    - AI summaries
    - Other encrypted user content
    """

    def __init__(
        self,
        primary_key_str: Optional[str] = None,
        old_keys_str: Optional[str] = None,
    ):
        self._primary_key = _derive_key(
            primary_key_str or settings.ENCRYPTION_KEY
        )

        self._aesgcm = AESGCM(self._primary_key)

        # Parse old keys for encryption-key rotation support
        old_keys_raw = (
            old_keys_str or settings.ENCRYPTION_OLD_KEYS or ""
        ).split(",")

        self._fallback_keys: list[bytes] = [
            _derive_key(key)
            for key in old_keys_raw
            if key.strip()
        ]

    def encrypt(self, plaintext: Optional[str]) -> Optional[str]:
        """
        Encrypt plaintext using AES-256-GCM.

        Returns:
            enc:v1:<base64(nonce + ciphertext + authentication tag)>
        """

        if plaintext is None:
            return None

        if not isinstance(plaintext, str):
            plaintext = str(plaintext)

        # Prevent double encryption
        if plaintext.startswith(ENCRYPTION_PREFIX):
            return plaintext

        # AES-GCM standard 12-byte nonce
        nonce = os.urandom(12)

        plaintext_bytes = plaintext.encode("utf-8")

        ciphertext_with_tag = self._aesgcm.encrypt(
            nonce,
            plaintext_bytes,
            None,
        )

        combined = nonce + ciphertext_with_tag

        encoded = base64.b64encode(combined).decode("ascii")

        return f"{ENCRYPTION_PREFIX}{encoded}"

    def decrypt(self, ciphertext: Optional[str]) -> Optional[str]:
        """
        Decrypt an AES-256-GCM encrypted value.

        Behaviour:
        - None -> None
        - Legacy plaintext -> returned unchanged
        - Valid encrypted value -> decrypted
        - Wrong key -> ValueError
        - Corrupted ciphertext -> ValueError
        - Tampered ciphertext -> ValueError
        """

        if ciphertext is None:
            return None

        if not isinstance(ciphertext, str):
            ciphertext = str(ciphertext)

        # Legacy plaintext support
        if not ciphertext.startswith(ENCRYPTION_PREFIX):
            return ciphertext

        # Remove encryption prefix
        payload_b64 = ciphertext[len(ENCRYPTION_PREFIX):]

        if not payload_b64:
            raise ValueError("Encrypted payload is empty")

        # Decode Base64 safely
        try:
            raw = base64.b64decode(
                payload_b64,
                validate=True,
            )
        except Exception as e:
            logger.warning(
                "Invalid encrypted payload encoding: %s",
                e,
            )
            raise ValueError(
                "Invalid encrypted payload"
            ) from e

        # AES-GCM requires:
        # 12-byte nonce + at least 16-byte authentication tag
        if len(raw) < 28:
            raise ValueError(
                "Payload too short to be valid AES-GCM ciphertext"
            )

        nonce = raw[:12]
        encrypted_data = raw[12:]

        # ---------------------------------------------------------
        # Try primary/current encryption key
        # ---------------------------------------------------------
        primary_error = None

        try:
            decrypted_bytes = self._aesgcm.decrypt(
                nonce,
                encrypted_data,
                None,
            )

            return decrypted_bytes.decode("utf-8")

        except Exception as e:
            primary_error = e

            logger.warning(
                "Decryption with primary key failed; "
                "attempting fallback keys."
            )

        # ---------------------------------------------------------
        # Try old encryption keys
        # ---------------------------------------------------------
        for old_key in self._fallback_keys:
            try:
                old_aes = AESGCM(old_key)

                decrypted_bytes = old_aes.decrypt(
                    nonce,
                    encrypted_data,
                    None,
                )

                return decrypted_bytes.decode("utf-8")

            except Exception:
                continue

        # ---------------------------------------------------------
        # No key could decrypt the value
        # ---------------------------------------------------------
        logger.error(
            "Unable to decrypt encrypted content using "
            "primary or fallback keys."
        )

        raise ValueError(
            "Unable to decrypt encrypted content. "
            "The key is incorrect or the encrypted data is corrupted."
        ) from primary_error

    def is_encrypted(self, val: Optional[str]) -> bool:
        """
        Check whether a value uses our encryption envelope.
        """

        return (
            isinstance(val, str)
            and val.startswith(ENCRYPTION_PREFIX)
        )


# Global encryption service
crypto_service = FieldEncryptionService()