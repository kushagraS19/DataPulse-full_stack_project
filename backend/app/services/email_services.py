import resend

from app.core.config import settings


resend.api_key = settings.RESEND_API_KEY


async def send_password_change_otp(
    email: str,
    otp: str
):
    params: resend.Emails.SendParams = {
        "from": settings.EMAIL_FROM,
        "to": [email],
        "subject": "DataPulse Password Change OTP",
        "html": f"""
        <h2>DataPulse Password Change</h2>

        <p>Your OTP for changing your password is:</p>

        <h1>{otp}</h1>

        <p>This OTP will expire in 5 minutes.</p>

        <p>If you did not request a password change,
        please ignore this email.</p>

        <p>Regards,<br>
        DataPulse</p>
        """
    }

    email_response = await resend.Emails.send_async(params)

    return email_response

async def send_email_verification_otp(
    email: str,
    otp: str
):
    params: resend.Emails.SendParams = {
        "from": settings.EMAIL_FROM,
        "to": [email],
        "subject": "DataPulse Email Verification OTP",
        "html": f"""
            <h2>DataPulse Email Verification</h2>

            <p>Your OTP for verifying your email is:</p>

            <h1>{otp}</h1>

            <p>This OTP will expire in 5 minutes.</p>

            <p>If you did not request it, please ignore this email.</p>

            <p>Regards,<br>
            DataPulse</p>
        """
    }

    email_response = await resend.Emails.send_async(params)

    return email_response
