import csv
import json
import os

# 파일 경로 설정 (공공데이터포털에서 다운로드한 CSV 파일명으로 수정하세요)
BRIDGE_CSV = '국토교통부_전국교량표준데이터.csv'
TUNNEL_CSV = '국토교통부_전국터널표준데이터.csv'
OUTPUT_JS = 'structures_data.js'

def read_csv(file_path):
    """
    여러 인코딩(utf-8-sig, utf-8, cp949)을 시도하며 CSV 파일을 읽습니다.
    """
    encodings = ['utf-8-sig', 'utf-8', 'cp949']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                # 첫 줄을 읽어 파일이 유효한지 확인 (encoding 에러 발생 유도)
                f.readline()
                f.seek(0)
                # DictReader로 데이터 한꺼번에 읽기
                return list(csv.DictReader(f))
        except (UnicodeDecodeError, UnicodeError):
            continue
        except Exception as e:
            print(f"Error reading {file_path} with {encoding}: {e}")
            break
    return None

def rebuild():
    structures = []
    
    # 1. 교량 데이터 처리
    if os.path.exists(BRIDGE_CSV):
        print(f"Processing {BRIDGE_CSV}...")
        data = read_csv(BRIDGE_CSV)
        if data:
            for row in data:
                try:
                    # 다양한 컬럼명 변형 대응 (정확한 확인 결과 반영)
                    name = (row.get('교량명') or row.get('시설물명') or '').strip()
                    lat = float(row.get('교량시작점위도') or row.get('교량시점위도') or row.get('위도') or 0)
                    lng = float(row.get('교량시작점경도') or row.get('교량시점경도') or row.get('경도') or 0)
                    length = (row.get('교량연장') or row.get('연장') or '').strip()
                    
                    # 시도명, 시군구명 추가
                    sd = (row.get('시도명') or '').strip()
                    sg = (row.get('시군구명') or '').strip()
                    
                    if name and lat and lng:
                        structures.append({
                            "n": name,
                            "t": "b",
                            "ll": [lat, lng],
                            "l": f"{length}m" if length and 'm' not in length else length,
                            "sd": sd,
                            "sg": sg
                        })
                except:
                    continue
    
    # 2. 터널 데이터 처리
    if os.path.exists(TUNNEL_CSV):
        print(f"Processing {TUNNEL_CSV}...")
        data = read_csv(TUNNEL_CSV)
        if data:
            for row in data:
                try:
                    name = (row.get('터널명') or row.get('시설물명') or '').strip()
                    lat = float(row.get('터널시작점위도') or row.get('터널시점위도') or row.get('시설물시점위도') or row.get('위도') or 0)
                    lng = float(row.get('터널시작점경도') or row.get('터널시점경도') or row.get('시설물시점경도') or row.get('경도') or 0)
                    length = (row.get('터널연장') or row.get('시설물연장') or row.get('연장') or '').strip()
                    
                    # 시도명, 시군구명 추가
                    sd = (row.get('시도명') or '').strip()
                    sg = (row.get('시군구명') or '').strip()
                    
                    if name and lat and lng:
                        structures.append({
                            "n": name,
                            "t": "t",
                            "ll": [lat, lng],
                            "l": f"{length}m" if length and 'm' not in length else length,
                            "sd": sd,
                            "sg": sg
                        })
                except:
                    continue

    if not structures:
        print("Error: No data found. Please check CSV filenames and encodings.")
        return

    # 3. JS 파일 쓰기
    print(f"Writing to {OUTPUT_JS} ({len(structures)} items)...")
    content = f"const STRUCTURES_DATA = {json.dumps(structures, ensure_ascii=False)};"
    with open(OUTPUT_JS, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Complete!")

if __name__ == "__main__":
    rebuild()
