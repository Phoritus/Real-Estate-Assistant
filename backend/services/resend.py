import resend
from env import RESEND_API_KEY

resend.api_key = RESEND_API_KEY

r = resend.Emails.send({
  "from": "onboarding@resend.dev",
  "to": "poohzazazaja@gmail.com",
  "subject": "Hello World",
  "html": "<p>Congrats on sending your <strong>first email</strong>!</p>"
})
