import os
import base64
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logging_utils import print_and_logging
# スコープ設定（メールの読み取りと変更）
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail():
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

def get_gmail_service():
    """Gmail APIのサービスオブジェクトを取得"""
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)
    return service

def get_lancers_urls_from_unread_email(service):
    """<noreply@lancers.co.jp> から来た未読のメールから https://www.lancers.jp/work/detail/ で始まるURLのリストを取得する"""
    results = service.users().messages().list(userId='me', q='from:noreply@lancers.co.jp is:unread').execute()
    messages = results.get('messages', [])
    if not messages:
        print_and_logging('No unread messages found from noreply@lancers.co.jp.')
        return []
    
    message = messages[0]  # 最初の未読メッセージを取得
    msg = service.users().messages().get(userId='me', id=message['id']).execute()
    
    # メッセージを既読にする
    service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()
    
    # メール本文の取得とデコード
    parts = msg['payload'].get('parts', [])
    body_data = ''
    for part in parts:
        if part['mimeType'] == 'text/plain':
            body_data = part['body']['data']
            break
    if not body_data:
        print_and_logging('No plain text body found.')
        return []

    decoded_body = base64.urlsafe_b64decode(body_data).decode('utf-8')
    
    # URLの抽出
    urls = re.findall(r'https://www.lancers.jp/work/detail/\S+', decoded_body)
    return urls

def main():
    service = get_gmail_service()
    lancers_urls = get_lancers_urls_from_unread_email(service)
    print_and_logging(lancers_urls)

if __name__ == '__main__':
    main()
