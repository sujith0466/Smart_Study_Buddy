from flask import Blueprint, jsonify, request
from youtube_api import get_youtube_suggestions

api = Blueprint('api', __name__)

@api.route('/get_resources', methods=['GET'])
def get_resources():
    subject = request.args.get('subject')
    resources = get_youtube_suggestions([subject])
    return jsonify(resources)
