from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__, template_folder='../templates')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract_video():
    data = request.get_json() or {}
    url = data.get('url')

    if not url:
        return jsonify({'error': 'يرجى إدخال رابط صحيح'}), 400

    try:
        # استخدام API مباشر وسريع بديل
        api_endpoint = f"https://api.vkrdown.com/api/download?url={url}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(api_endpoint, headers=headers, timeout=12)
        res_data = response.json()

        if response.status_code == 200 and res_data.get('status') == True:
            data_info = res_data.get('data', {})
            download_url = data_info.get('url') or data_info.get('downloadUrl')
            title = data_info.get('title', 'فيديو جاهز للتحميل')
            thumb = data_info.get('thumbnail', '')

            # جمع كل الجودات المتاحة لو موجودة
            formats = []
            if 'downloads' in data_info and isinstance(data_info['downloads'], list):
                for item in data_info['downloads']:
                    formats.append({
                        'quality': item.get('quality', 'Video HD'),
                        'ext': item.get('format', 'mp4'),
                        'url': item.get('url')
                    })
            elif download_url:
                formats.append({
                    'quality': 'HD Video',
                    'ext': 'mp4',
                    'url': download_url
                })

            if formats:
                return jsonify({
                    'title': title,
                    'thumbnail': thumb,
                    'formats': formats
                })

        # في حال لم يرجع السيرفر الأول نتائج، يتم التحويل لـ API احتياطي ممتاز
        fallback_api = f"https://aadvance-downloader.vercel.app/api/download?url={url}"
        fb_res = requests.get(fallback_api, timeout=10).json()
        
        if fb_res.get('url'):
            return jsonify({
                'title': fb_res.get('title', 'فيديو جاهز'),
                'thumbnail': fb_res.get('thumbnail', ''),
                'formats': [{'quality': 'Download Video', 'ext': 'mp4', 'url': fb_res['url']}]
            })

        return jsonify({'error': 'تعذر استخراج رابط الفيديو، تأكد من صحة الرابط وسماحية الفيديو.'}), 400

    except Exception as e:
        return jsonify({'error': f'حدث خطأ أثناء الاتصال: {str(e)}'}), 500
