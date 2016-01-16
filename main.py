from flask import Flask, jsonify, render_template
import feedparser

app = Flask(__name__)

GOODREADS_RSS_URL = 'https://www.goodreads.com/quotes_of_the_day/rss'


def parse_quotes(url):
    feedparser._HTMLSanitizer.acceptable_elements = []
    feed = feedparser.parse(url)
    quotes = []
    for feed in feed.entries:
        quotes.append([a for a in feed.summary.splitlines() if a and a != '-'])
    return quotes


@app.route('/quotes/api/v1')
def quotes():
    quotes = parse_quotes(GOODREADS_RSS_URL)
    return jsonify(quotes=quotes)


@app.route('/quotes/api/v1/<id>')
def single_quote(id):
    quotes = parse_quotes(GOODREADS_RSS_URL)
    return jsonify({'id': id,
                    'quote':
                        {'summary': quotes[int(id)][0],
                         'author': quotes[(int(id))][1]}
                    })


@app.route('/')
def home():
    return render_template('quotes.html',
                           quotes=parse_quotes(GOODREADS_RSS_URL))

if __name__ == '__main__':
    app.run(debug=True)
