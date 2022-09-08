import boto3
import argparse
from botocore.config import Config

ses_client = boto3.client("ses", config=Config(
    region_name="us-east-1"
))


class Email:
    def __init__(self, ses_client) -> None:
        self.ses_client = ses_client
        self.subject = ""
        self.email_html_body = ""
        self.email_text_body = ""
        self.to_address = ""
        self.from_address = "moderation@mail.openimagegenius.com"

    def send(self):
        return self.ses_client.send_email(
            Source=self.from_address,
            Destination={
                "ToAddresses": [self.to_address],
            },
            Message={
                "Subject": {
                    "Data": self.subject,
                    "Charset": "UTF-8"
                },
                "Body": {
                    # "Html": {
                    #     "Data": self.email_html_body,
                    #     "Charset": "UTF-8"
                    # },
                    "Text": {
                        "Data": self.email_text_body,
                        "Charset": "UTF-8"
                    }
                },
            },
        )


class WelcomeAlphaEmail(Email):
    def __init__(self, ses_client, to_address) -> None:
        super().__init__(ses_client)
        self.subject = "Welcome - Alpha Version - Open Image Genius"
        self.email_html_body = """

        """
        self.email_text_body = """
        Hi,


        Thank you for subscribing to the alpha version of the Open Image Genius platform. I'm really excited to have you onboard.

        Today, I'm releasing the production environment under the link: http://app.openimagegenius.com)

        Please note that this is still alpha and highly unstable, but it should be a bit more stable than the development environment (http://dev.app.openimagegenius.com)
        
        If you received this e-mail, you should have access to both environments. Also please note that my GPU is not always turned on, in which case
        you will get a 'Job failed' error when trying to generate an image.

        If you want to unsubscribe from the platform or from this email list, please write to: moderation@mail.openimagegenius.com

        You're also welcome to reach me out on this e-mail for anything related to the platform,
        including complaints, bug reports, feedback, feature requests etc.

        You can also open an issue on the GitHub repository: https://github.com/paolorechia/openimagegenius


        Best regards,
        Paolo Rechia
        """
        self.to_address = to_address


def main(args):
    email = None
    if args.email_type == "welcome-alpha":
        email = WelcomeAlphaEmail(
            to_address=args.to_address,
            ses_client=ses_client,
        )
    else:
        raise ValueError(f"Unrecognized email type {args.email_type}")
    if not args.dry:
        print("Sending...")
        response = email.send()
        print(f"API Response: {response}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Send an email"
    )
    parser.add_argument("--to_address", type=str)
    parser.add_argument("--email_type", type=str)
    parser.add_argument("--dry", type=bool)
    args = parser.parse_args()
    main(args)
