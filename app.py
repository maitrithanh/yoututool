from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route('/api/video-info', methods=['POST'])
def video_info():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'Missing YouTube URL'}), 400

    try:
        with yt_dlp.YoutubeDL({}) as ydl:
            info = ydl.extract_info(url, download=False)

            grouped_formats = {
                'video+audio': [],
                'video-only': [],
                'audio-only': []
            }

            for f in info['formats']:
                if not f.get('url'):
                    continue

                has_audio = f.get('acodec') != 'none'
                has_video = f.get('vcodec') != 'none'

                # Xác định loại
                if has_audio and has_video:
                    f_type = 'video+audio'
                elif has_video:
                    f_type = 'video-only'
                elif has_audio:
                    f_type = 'audio-only'
                else:
                    continue  # bỏ qua nếu không có audio lẫn video

                grouped_formats[f_type].append({
                    'format_id': f.get('format_id'),
                    'ext': f.get('ext'),
                    'resolution': f.get('resolution') or (
                        f"{f.get('width')}x{f.get('height')}" if f.get('width') and f.get('height') else "audio"
                    ),
                    'filesize': f.get('filesize'),
                    'url': f.get('url')
                })

            return jsonify({
                'title': info['title'],
                'thumbnail': info['thumbnail'],
                'formats': grouped_formats
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
