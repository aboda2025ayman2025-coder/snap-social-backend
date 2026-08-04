from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='../templates')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract_video():
    data = request.get_json() or {}
    url = data.get('url', '').strip()

    if not url:
        return jsonify({'error': 'يرجى إدخال رابط صحيح'}), 400

    # إرجاع الرابط مباشرة للمتصفح لمعالجته بدون المرور بخوادم Vercel المقتطعة
    return jsonify({
        'title': 'فيديو جاهز للتحميل',
        'direct_process': True,
        'url': url
    })
