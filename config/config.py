import yaml
import os

def load_config():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, 'config.yml')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config['plc']
    except Exception as e:
        print(f"설정 파일 로드 실패: {str(e)}")
        # 기본값 반환
        return {
            'host': '127.0.0.1',
            'port': 5001
        }