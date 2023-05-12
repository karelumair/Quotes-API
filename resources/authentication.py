"""All the Authentication API endpoints"""

import hashlib
from flask import Response, request, jsonify, make_response
from flask_restful import Resource
from flask_jwt_extended import (
    jwt_required,
    get_jwt,
    decode_token,
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
)
from mongoengine.errors import DoesNotExist
from database.models import Author, LoginToken


class AuthorLogin(Resource):
    """Login Authentication API"""

    def post(self) -> Response:
        """Generate access token by login

        Returns:
            Response: JSON response of access token
        """
        login_details = request.get_json()

        try:
            author = Author.objects.get(name=login_details["name"])
        except DoesNotExist:
            return make_response(jsonify({"Error": "Author Does Not Exist!"}), 404)

        if author.createdBy != "author":
            response, status = {
                "Error": "User Author with the given name doesn't exists!"
            }, 404
        if author:
            encrpted_password = hashlib.sha256(
                login_details["password"].encode("utf-8")
            ).hexdigest()
            if encrpted_password == author.password:
                access_token = create_access_token(identity=str(author.id))
                refresh_token = create_refresh_token(identity=str(author.id))

                login_token = LoginToken(
                    author_id=author.id,
                    access=decode_token(access_token)["jti"],
                    refresh=decode_token(refresh_token)["jti"],
                )
                login_token.save()

                return make_response(
                    jsonify(
                        {
                            "access_token": access_token,
                            "refresh_token": refresh_token,
                        }
                    ),
                    200,
                )

            response, status = {"Error": "Invalid Credentials"}, 401
        else:
            response, status = {"Error": "Username does not exist!"}, 404

        return make_response(jsonify(response), status)


class TokenRefresh(Resource):
    """Token Views

    Returns:
            Response: JSON response of request
    """

    @jwt_required(refresh=True)
    def get(self):
        """Refresh Access Token

        Returns:
            Response: JSON response of refreshed access token
        """
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)

        token = LoginToken.objects.get(author_id=identity, refresh=get_jwt()["jti"])
        token.update(access=decode_token(access_token)["jti"])

        return make_response(jsonify({"access_token": access_token}), 200)


class AuthorLogout(Resource):
    """Author Logout View Class"""

    @jwt_required()
    def post(self):
        """Remove current author token and logout author

        Returns:
            Response: JSON response of logout
        """
        identity = get_jwt_identity()

        token = LoginToken.objects.get(author_id=identity, access=get_jwt()["jti"])
        token.delete()

        return make_response(jsonify(""), 204)

    @jwt_required()
    def delete(self):
        """Remove all the users token and logout from all devices

        Returns:
            Response: JSON response of logout
        """
        identity = get_jwt_identity()

        for token in LoginToken.objects(author_id=identity):
            token.delete()

        return make_response(jsonify(""), 204)


class CurrentUser(Resource):
    """Current User View Class"""

    @jwt_required()
    def get(self):
        """Return authenticated author

        Returns:
            Response: JSON response of author data
        """
        identity = get_jwt_identity()

        try:
            author = Author.objects.exclude("scrapeId").get(id=identity)
            response, status = author.to_json(), 200
        except DoesNotExist:
            response, status = {"message": "author doesn't exists"}, 404

        return make_response(jsonify(response), status)
