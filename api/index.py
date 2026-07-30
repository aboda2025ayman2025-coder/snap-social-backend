from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract_video():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'يرجى إدخال رابط صحيح'}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            # استخراج الجودات التي تحتوي على فيديو وصوت معا
            clean_formats = []
            for f in formats:
                # التأكد أن المقطع يحتوي على فيديو وصوت وليس فيديو فقط (no audio)
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    clean_formats.append({
                        'quality': f.get('format_note') or f.get('resolution') or 'Video',
                        'ext': f.get('ext', 'mp4'),
                        'url': f.get('url')  # الرابط المباشر للتحميل
                    })

            # لو لم يجد صيغ مدمجة، نأخذ أفضل صيغة مباشرة
            if not clean_formats and 'url' in info:
                clean_formats.append({
                    'quality': 'Best Quality',
                    'ext': info.get('ext', 'mp4'),
                    'url': info['url']
                })

            return jsonify({
                'title': info.get('title', 'Video'),
                'thumbnail': info.get('thumbnail'),
                'formats': clean_formats
            })

    except Exception as e:
        return jsonify({'error': f'حدث خطأ أثناء معالجة الرابط: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
