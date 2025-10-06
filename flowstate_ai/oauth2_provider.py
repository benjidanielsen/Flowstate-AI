from flask import Flask, request, jsonify, redirect
from authlib.integrations.flask_oauth2 import AuthorizationServer, ResourceProtector
from authlib.oauth2.rfc6749 import grants
from authlib.oauth2.rfc6749.errors import InvalidClientError
from werkzeug.security import gen_salt
from datetime import datetime, timedelta
from models import db, User, OAuth2Client, OAuth2Token

app = Flask(__name__)
app.config.update({
    'DEBUG': True,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///flowstate_ai.db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SECRET_KEY': 'replace-with-a-secure-random-secret',
})

# Initialize DB
from flask_sqlalchemy import SQLAlchemy

db.init_app(app)

authorization = AuthorizationServer(app, query_client=lambda client_id: OAuth2Client.query.filter_by(client_id=client_id).first())
require_oauth = ResourceProtector()

# Grant classes
class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    def save_authorization_code(self, code, request):
        client = request.client
        auth_code = OAuth2Token(
            client_id=client.client_id,
            code=code,
            redirect_uri=request.redirect_uri,
            scope=request.scope,
            user_id=request.user.id,
            expires_at=datetime.utcnow() + timedelta(minutes=10),
            code_challenge=request.data.get('code_challenge'),
            code_challenge_method=request.data.get('code_challenge_method'),
        )
        db.session.add(auth_code)
        db.session.commit()

    def query_authorization_code(self, code, client):
        auth_code = OAuth2Token.query.filter_by(code=code, client_id=client.client_id).first()
        if auth_code and auth_code.is_expired() is False:
            return auth_code

    def delete_authorization_code(self, authorization_code):
        db.session.delete(authorization_code)
        db.session.commit()

    def authenticate_user(self, authorization_code):
        return User.query.get(authorization_code.user_id)

class RefreshTokenGrant(grants.RefreshTokenGrant):
    def authenticate_refresh_token(self, refresh_token):
        token = OAuth2Token.query.filter_by(refresh_token=refresh_token).first()
        if token and token.is_refresh_token_active():
            return token

    def authenticate_user(self, credential):
        return User.query.get(credential.user_id)

    def revoke_old_credential(self, credential):
        credential.revoked = True
        db.session.add(credential)
        db.session.commit()

# Register grants
authorization.register_grant(AuthorizationCodeGrant)
authorization.register_grant(RefreshTokenGrant)

@app.route('/oauth/authorize', methods=['GET', 'POST'])
def authorize():
    user = get_current_user()  # Implement your user session logic
    if not user:
        return redirect('/login?next=' + request.url)

    if request.method == 'GET':
        try:
            grant = authorization.get_consent_grant(end_user=user)
        except InvalidClientError:
            return jsonify({'error': 'invalid_client'}), 400
        # Render your authorization page here
        return f"""
        <form method='post'>
            <p>Client {grant.client.client_name} wants access to your data.</p>
            <button name='confirm' value='yes' type='submit'>Authorize</button>
            <button name='confirm' value='no' type='submit'>Deny</button>
        </form>
        """

    confirm = request.form.get('confirm')
    if confirm == 'yes':
        return authorization.create_authorization_response(grant_user=user)
    return authorization.create_authorization_response(grant_user=None)

@app.route('/oauth/token', methods=['POST'])
def issue_token():
    return authorization.create_token_response()

@app.route('/oauth/revoke', methods=['POST'])
def revoke_token():
    return authorization.create_endpoint_response('revocation')

@app.route('/api/userinfo')
@require_oauth('profile')
def api_userinfo():
    user = request.oauth.user
    return jsonify(id=user.id, username=user.username, email=user.email)


# Helper to get current logged-in user (mock implementation)
def get_current_user():
    # This function should integrate with your authentication/session system.
    # For demonstration, we assume a user with id=1 is logged in.
    return User.query.get(1)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables
    app.run(port=5000)
