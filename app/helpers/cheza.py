from enum import verify
import os
import time

import httpx

from app.config.default import settings


class Cheza:
    @staticmethod
    def register_customer(**kwargs):
        payload = {
            "msisdn": kwargs.get("phone_number", ""),
            "linkId": kwargs.get("request_id", ""),
            "message": kwargs.get("message", "REG"),
            "requestTimestamp": time.time_ns(),
        }
        with httpx.Client(
            headers={"Content-Type": "application/json"},
            verify=bool(int(os.environ.get("VERIFY_SSL", 0)))
        ) as client:
            response = (
                client.post(
                    url=os.environ.get("CHEZACASH_GAME_SMS_REGISTRATION_URL", ""),
                    json=payload,
                    timeout=settings.DEFAULT_TIMEOUT,
                )
                .raise_for_status()
                .json()
            )
        return response

    @staticmethod
    def send_sms(**kwargs):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {Cheza.generate_access_token()}",
        }
        payload = {
            "phone": kwargs.get("phone_number", ""),
            "message": kwargs.get("message", ""),
            "request_id": kwargs.get("mpesa_ref_number", ""),
        }
        with httpx.Client(
            base_url=os.environ.get("CHEZACASH_SMS_API_BASE_URL", ""),
            headers=headers,
            verify=bool(int(os.environ.get("VERIFY_SSL", 0)))) as client:
            response = (
                client.post(
                    "/sendsms.php", json=payload, timeout=settings.DEFAULT_TIMEOUT
                )
                .raise_for_status()
                .json()
            )
        return response

    @staticmethod
    def generate_access_token() -> str:
        token = ""
        try:
            url = f"{os.environ.get('CHEZACASH_SMS_API_BASE_URL')}/token.php"
            payload = {
                "client_id": os.environ.get("CHEZACASH_SMS_CLIENT_ID"),
                "client_secret": os.environ.get("CHEZACASH_SMS_CLIENT_SECRET"),
                "grant_type": os.environ.get("CHEZACASH_SMS_GRANT_TYPE"),
            }
            token = httpx.post(
                url,
                json=payload,
                timeout=settings.DEFAULT_TIMEOUT,
                verify=bool(int(os.environ.get("VERIFY_SSL", 0)))
            ).json()["access_token"]
        except httpx.HTTPError:
            pass
        return token
