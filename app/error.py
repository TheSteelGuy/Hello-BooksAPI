from flask import jsonify


def resource_not_found(error):
    """resource not found"""
    response = jsonify({"message": "the URL does not exist"})
    response.status_code = 404
    return response


def server_error(error):
    """Handle 500 error."""
    response = jsonify({
        "message": "{}.ths usually means your request cannot be proccessed.Kindly check if you are supplying data in correct format".format(error)
    })
    response.status_code = 500
    return response


def method_not_allowed(error):
    """Handle 405 error."""
    response = jsonify({"message": "Method not allowed"})
    response.status_code = 405
    return response
