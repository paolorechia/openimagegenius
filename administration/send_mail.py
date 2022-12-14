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

        Today, I'm releasing the production environment under the link: https://app.openimagegenius.com)

        Please note that this is still alpha and highly unstable, but it should be a bit more stable than the development environment (https://dev.app.openimagegenius.com)
        
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

class WelcomeCorrectionAlphaEmail(Email):
    def __init__(self, ses_client, to_address) -> None:
        super().__init__(ses_client)
        self.subject = "Open Image Genius - Correct Link to the Platform"
        self.email_html_body = """

        """
        self.email_text_body = """
        Hi,

        I'm terribly sorry, but the previous link was incorrect (it used http instead of https). If you tried and could not access, please try it with HTTPS instead, like this:

        - https://app.openimagegenius.com
        - https://auth.openimagegenius.com
        - https://dev.auth.openimagegenius.com
        - https://dev.app.openimagegenius.com
        

        Best regards,
        """
        self.to_address = to_address

class OpenAlphaEmail(Email):
    def __init__(self, ses_client, to_address) -> None:
        super().__init__(ses_client)
        self.subject = "Moving to Open Alpha - Open Image Genius"
        self.email_html_body = """

        """
        self.email_text_body = """
        Hi, 
        
        While the current version is still rudimentary, here are some updates:

        1. I've opened the signup for any user (user limit may still apply), as I was not getting enough traffic on the app. Anyone can signup at https://auth.openimagegenius.com/
        2. Launched a "production" environment: https://app.openimagegenius.com/
        3. Rate limits now apply. Users may issue 5 requests / minute. No hard limit on number of images (at least not yet).
        4. Gallery feature to see your created images.
        5. Rescheduling of failed events when a GPU node connects. If you had some failed jobs, you may want to signin and check if your image is there.
        6. The GPU node may now share GPU memory between "dev" and production environments. In the past, running two nodes simultaneously triggered out of memory problems. 
        7. Created a telegram channel where a bot posts events about GPU / users connecting/disconnecting: https://t.me/openimagegenius
        8. Created a discord server in case people want to reach me out there: https://discord.gg/xZfaSu3akc
        9. You can read about the upcoming features in https://pacific-drip-6f9.notion.site/The-Fourth-Iteration-So-many-features-cff9e66392f340688447e164b6315e89 - I'm more than happy to receive requests / feedback on what's more important for you.

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
    elif args.email_type == "welcome-alpha-correction":
        email = WelcomeCorrectionAlphaEmail(
            to_address=args.to_address,
            ses_client=ses_client,
        )
    elif args.email_type == "open-alpha":
        email = OpenAlphaEmail(
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
