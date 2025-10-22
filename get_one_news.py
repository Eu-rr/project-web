import flask
from flask import jsonify
from data import db_session
from data.news import News

get_one_news = flask.Blueprint('news_api', __name__,
                            template_folder='templates')


@get_one_news.route('/api/news/<int:news_id>',  methods=['GET'])
def get_one_news(news_id):
    session = db_session.create_session()
    news = session.query(News).get(news_id)
    if not news:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'news': news.to_dict(only=('title', 'content', 'user_id', 'is_private'))
        }
    )