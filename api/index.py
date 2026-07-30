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
        # API قوي ومباشر ومستقر لجميع المنصات
        api_url = f"https://api.tiklydown.eu.org/api/download?url={url}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # محاولة السيرفر الأول
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            res_data = response.json()
            # في حال كان يوتيوب أو أينما كان نوع الفيديو
            video_url = res_data.get('video', {}).get('noWatermark') or res_data.get('url') or res_data.get('download_url')
            
            if video_url:
                return jsonify({
                    'title': res_data.get('title', 'فيديو جاهز للتحميل'),
                    'thumbnail': res_data.get('cover', ''),
                    'formats': [{'quality': 'HD Video', 'ext': 'mp4', 'url': video_url}]
                })

        # سيرفر احتياطي قوي جداً (Invidious API) المخصص لليوتيوب
        if 'youtu' in url:
            # استخراج الـ ID الخاص بالفيديو
            video_id = url.split('/')[-1].split('?')[0].replace('watch?v=', '')
            invidious_api = f"https://inv.tux.gay/api/v1/videos/{video_id}"
            
            inv_res = requests.get(invidious_api, headers=headers, timeout=10)
            if inv_res.status_code == 200:
                inv_data = inv_res.json()
                formats = []
                for fmt in inv_data.get('formatStreams', []):
                    formats.append({
                        'quality': fmt.get('qualityLabel', 'Video'),
                        'ext': 'mp4',
                        'url': fmt.get('url')
                    })
                
                if formats:
                    return jsonify({
                        'title': inv_data.get('title', 'YouTube Video'),
                        'thumbnail': inv_data.get('videoThumbnails', [{}])[0].get('url', ''),
                        'formats': formats
                    })

        return jsonify({'error': 'لم نتمكن من جلب السيرفرات، يرجى التأكد من أن الرابط لفيديو عام وشغال.'}), 400

    except Exception as e:
        return jsonify({'error': f'حدث خطأ أثناء جلب الفيديو: {str(e)}'}), 500
