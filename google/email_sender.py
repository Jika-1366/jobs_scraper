import os
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# スコープ設定（メールの送信権限を追加）
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send'
]

def _authenticate_gmail():
    """Google API認証を行う"""
    creds = None
    # 保存された認証情報があればそれを使う
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # 認証情報がない、または無効であれば新たに認証を行う
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            load_dotenv()  # .env ファイルから環境変数を読み込む
            client_id = os.getenv("GOOGLE_CLIENT_ID")
            client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
            if not client_id or not client_secret:
                raise ValueError("環境変数 GOOGLE_CLIENT_ID または GOOGLE_CLIENT_SECRET が設定されていません。")
            client_config = {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "redirect_uris": ["http://localhost"]
                }
            }
            flow = InstalledAppFlow.from_client_config(
                client_config, SCOPES)
            creds = flow.run_local_server(port=0)
        # 認証情報を保存
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def _get_gmail_service():
    """Gmail APIのサービスオブジェクトを取得"""
    creds = _authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)
    return service

def send_email(to: str, subject: str, body: str):
    """
    指定したメールアドレスにメールを送信する
    
    Args:
        to: 送信先メールアドレス
        subject: メールの件名
        body: メールの本文
    
    Returns:
        bool: 送信成功時はTrue、失敗時はFalse
    """
    try:
        service = _get_gmail_service()
        
        # メールメッセージの作成
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        # メッセージをBase64エンコード
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # メール送信
        service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return True
        
    except HttpError as error:
        print(f'メール送信中にエラーが発生しました: {error}')
        return False
    except Exception as e:
        print(f'予期せぬエラーが発生しました: {e}')
        return False

def send_job_notification(to: str, job_url: str, suggestion: str):
    """
    案件情報を指定したメールアドレスに送信する
    
    Args:
        to: 送信先メールアドレス
        job_url: 案件のURL
        suggestion: AIからの提案内容
    
    Returns:
        bool: 送信成功時はTrue、失敗時はFalse
    """
    subject = "新しい案件が見つかりました"
    body = f"""
新しい案件が見つかりました。

案件URL: {job_url}

AIからの提案:
{suggestion}

ご確認ください。
    """
    
    return send_email(to, subject, body)
